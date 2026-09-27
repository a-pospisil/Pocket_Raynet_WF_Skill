---
name: pocket-to-raynet
description: >-
  Zapisuje hovory nahrané v Hey Pocket do Raynet CRM jako realizované telefonáty
  včetně shrnutí, vazby na klienta a obchodní případ, zakládá navazující aktivity
  z action items a připravuje e-maily z hovoru jako upravitelné koncepty. Použij vždy,
  když uživatel chce dostat hovor, nahrávku, telefonát nebo konzultaci do Raynetu nebo
  do CRM — i když řekne jen „zapiš ten hovor", „hoď to do CRM", „zpracuj dnešní hovory",
  „co jsem dnes navolal, dej to ke klientům", „udělej z toho aktivitu" nebo „připrav
  klientovi mail z toho hovoru". Spusť i tehdy, když uživatel nezmíní Pocket ani Raynet
  jménem, ale jde o převod nahraného hovoru na CRM záznam, o follow-up nebo e-mail
  z hovoru, nebo o dohledání, jestli už je hovor v CRM zapsaný.
compatibility: >-
  Vyžaduje MCP servery Hey Pocket (plán Pro) a Raynet CRM, a Python 3 pro skripty
  (jen standardní knihovna).
metadata:
  version: "0.2.0"
  author: Adam Pospíšil
  hermes:
    tags: [crm, raynet, pocket, hypoteky, email]
---

# Pocket → Raynet

Převádí nahrávky hovorů z Hey Pocket na realizované telefonáty v Raynet CRM.

Prostředí je **finanční poradenství — hypotéky a investiční nemovitosti**. Hovory jsou
konzultace s klienty, bankéři a kolegy. Do CRM patří klientské hovory; soukromé
jen jako osobní aktivita bez obsahu.

## Jak to funguje

Proces je **interaktivní, ne automatický**. Uživatel ho spustí pokynem, ty připravíš
návrh a **před zápisem ho necháš potvrdit**. Není to opatrnost pro opatrnost: Raynet
obsahuje přes 1000 klientů, z toho ~94 % fyzických osob, mezi nimi už existující
duplicity, a Pocket komolí jména v přepisech. Špatně spárovaný hovor skončí u cizího
člověka a nikdo si toho nevšimne. Potvrzení stojí pět vteřin, oprava půl hodiny.

Zápis do CRM je navíc **nevratný přes MCP** — žádný `delete` nástroj neexistuje.

Potvrzování se má postupně vypínat tam, kde se ukáže, že skill nechybuje
(viz [Režimy potvrzování](#režimy-potvrzování)). Aby to šlo posoudit, zapisuje se
každá akce do [audit logu](#audit-log) — včetně toho, jestli uživatel návrh opravil.

E-maily se **nikdy neodesílají**, jen připraví jako koncept k úpravě.

## Postup

### 1. Zjisti rozsah

Co se má zpracovat? Typicky jedna z variant:

| Pokyn | Rozsah |
|---|---|
| „zapiš poslední hovor" | 1 nejnovější nahrávka |
| „zpracuj dnešní hovory" | `recordingDateAfter` = dnešní půlnoc |
| „zapiš hovor s Balentem" | konkrétní nahrávka, klient zadaný ručně |

Když to z pokynu nejde určit, zeptej se. Neodvozuj rozsah z „posledního běhu" —
skill si mezi spuštěními nic nepamatuje, stav drží výhradně Raynet.

Varianta s ručně zadaným klientem je nejrychlejší a nejbezpečnější, protože přeskočí
párování klienta (krok 4). Když uživatel klienta jmenuje, využij toho.

### 2. Načti nahrávky

`search_pocket_conversations` s `recordingDateAfter` / `recordingDateBefore`.
Bez `query` běží recency režim, který vrací plné přepisy po 5 na stránku.

`query` použij jen na dohledání konkrétní nahrávky podle tématu. **Nespoléhej na něj
při hledání podle jména klienta** — vrací sekční zásahy, opakuje tutéž nahrávku
víckrát a jméno v titulku spolehlivě netrefí. Vždy deduplikuj podle `recordingId`.

`recordingDate` ze `search_*` je **začátek** hovoru. Zapamatuj si ho — je to klíč
pro kroky 4 a 5 i pro `scheduledFrom`.

### 3. Rozhodni, co do CRM vůbec patří

Ne každá nahrávka je klientský hovor. Do CRM nepatří:

| Typ | Jak poznat |
|---|---|
| Diktované poznámky sobě | jeden mluvčí, „poznámky k…", příprava prezentace |
| Interní porady s kolegy | protistrana je poradce z týmu, vývojář, asistentka |
| Vývojové hovory | řeší se aplikace, issues, merge |
| **Hovory s bankéřem přes víc případů** | jeden bankéř, přeskakuje mezi klienty, metodika |
| **Nepřijatý hovor / zapomenuté nahrávání** | útržky, okolní ruch, žádná souvislá konverzace |
| Testovací a prázdné | pár desítek znaků, `[background noise]` |

Bankéřské hovory a nepřijaté hovory vypadají na první pohled jako klientské, ale
zapsat se nedají — bankéřský proto, že se týká několika případů najednou a nejde
přiřadit k jednomu klientovi, nepřijatý proto, že se nic neodehrálo. Poznáš je
z obsahu, ne z názvu.

**Soukromý hovor** — protistrana není klient ani kolega a hovor se netýká práce
(rodina, známí, lékař). Do CRM patří jako **osobní aktivita** (krok 9, větev C):
bez obsahu, jen s krátkým neutrálním názvem, tak jako ostatní soukromé aktivity
v Raynetu („Lékař", „Louny"). CRM vidí celý tým — obsah soukromého hovoru do něj
nepatří.

Vyplyne-li ze soukromého hovoru **požadavek na úvěr nebo spolupráci** („hele,
potřeboval bych hypotéku"), je to nový obchod: pokračuj krokem 4 a hovor zapiš
k zájemci, ne jako osobní. Do shrnutí dej jen obchodní část.

Hraniční případy nezahazuj potichu — vypiš je jako přeskočené s důvodem, ať má
uživatel možnost říct „tenhle zapiš".

Skill si nepamatuje, co jsi minule vědomě přeskočil. Proto se při opakovaném běhu
přes stejné okno vynoří znovu. Řešením je posouvat datové okno dopředu, ne to řešit
v rámci skillu.

### 4. Spáruj klienta

Klienti jsou v Raynetu záznamy entity `company` — i fyzické osoby. Jméno z přepisu
je nejslabší místo celého procesu: Pocket ho komolí (`Balint`/`Balent`,
`Semrád`/`Semerák`, `Hasolová`/`Hassová`) a německé jméno `Bretschneider` je v CRM
zapsané foneticky jako `Bretšnajdr`. Jméno z přepisu ber jako nápovědu, ne jako klíč.

Postupuj od signálů, které na přepisu nezávisí, k těm, které na něm závisí:

**a) Naplánovaná aktivita v čase hovoru.** Měl-li uživatel hovor v kalendáři, víš,
s kým byl, bez ohledu na to, jak Pocket jméno slyšel:

```
activity_list(ownerId=2, scheduledFrom=<začátek − 2 h>, scheduledTill=<konec + 1 h>)
```

Aktivita s klientem, jejíž téma sedí na obsah hovoru, klienta určuje; jméno pak
jen ověř. Hovory se často uskuteční později, než byly naplánované — proto okno
začíná dvě hodiny před nahrávkou.

**b) E-mail, pokud v hovoru zazní** — `company_list(email=…)`. Nejlepší pokrytí
(~97 % klientů), ale **e-mail není unikátní**: sdílí ho majitel se svou s.r.o.,
manželé, a v jednom ověřeném případě dva různí lidé. Samotná shoda nestačí.

**c) Jméno přes `scripts/match_name.py`.** Filtr `company_list(name=…)` je substring,
ale **rozlišuje diakritiku** — ověřeno, `Calek` nenajde `Milan Čálek`. A přepis
bývá v pádě („s Honzou Rumlem"). Skript z jména nejdřív udělá hledací výrazy:

```bash
python3 scripts/match_name.py variants "Honzou Rumlem"
# surname_variants: ["Ruml", "Rum", "Řum"]   first_name_fallback: ["Jan"]
```

Každý výraz pošli do `company_list(name=<výraz>)`, odpovědi ulož a nech ohodnotit
(foneticky, bez diakritiky a titulů, v libovolném pořadí, Honza = Jan):

```bash
python3 scripts/match_name.py score "Honzou Rumlem" odpoved1.json odpoved2.json
```

Předávej **jméno**, ne celý název nahrávky. Z názvu si ho skript umí odhadnout
(obsah hranatých závorek, jinak poslední dvě slova s velkým písmenem), ale jen
nouzově. Křestní jméno jako hledací výraz použij až nakonec — vrací hodně záznamů.

**d) `lead_list`** — nový zájemce bývá nejdřív lead, ne klient.

Verdikt skriptu řídí, co dál:

| Verdikt | Co udělat |
|---|---|
| `jistý` | pokračuj |
| `pravděpodobný` | pokračuj, ale v návrhu (krok 8) shodu označ: „Semrád → Ing. Jaroslav Semerák (41)?" |
| `nejistý` | **zastav**, předlož kandidáty s id, e-mailem a vlastníkem, nech vybrat |
| `žádný` | zkus zbylé výrazy a `lead_list`; pak **zastav**, viz níže |

`nejistý` vyjde i tehdy, když je klient v CRM dvakrát (Zbyněk Svoboda je tam pod
id 613 i 603). Skript mezi shodnými záznamy nehádá — a ty taky ne.

🛑 **Klienta nezakládej přes `company_create`.** Umí vytvořit jen organizaci, ne
fyzickou osobu — vznikl by záznam špatného typu, který se bude jinak chovat při
každém dalším párování.

Když klient v CRM není, rozliš dvě situace:

- **Čekal bys ho tam** — hovor navazuje na dřívější jednání, zmiňuje OP nebo
  podklady. Nejspíš jen selhalo párování: zastav a zeptej se.
- **Nový zájemce** — první kontakt, požadavek na úvěr nebo spolupráci. Navrhni
  **lead** (`lead_create` s `leadPerson=true`), který na rozdíl od `company_create`
  fyzickou osobu umí. Parametry: `references/raynet-reference.md`, *Založení leadu*.
  Předtím zkontroluj `lead_list`, jestli lead už není.

Z leadu vznikne klient převodem v Raynet UI — přes MCP to nejde (`lead_convert`
jen napojí lead na už existující záznam). Do té doby zapiš hovor k leadu
(`phonecall_create(lead=<id>)`).

**Klient není vždy ten, s kým se mluví.** Hovor bývá veden s partnerem, rodičem nebo
známým, ale financování se řeší pro někoho jiného — a záznam patří k tomu, kdo bude
dlužníkem. Nahrávka „Martin G. — financování bytu pro Fenni G." patří k Fenni,
ne k Martinovi. Když jsou v CRM oba, rozhodni podle toho, **čí je to případ**.

### 5. Zkontroluj, co už u klienta je

Teprve když znáš `companyId`, jde spolehlivě zjistit, jestli hovor není už zapsaný
a jestli k němu neexistuje naplánovaná aktivita.

Obojí zjistíš dvěma dotazy na **`activity_list`**, ne na `phonecall_list`:

```
activity_list(companyId=<id>, createdFrom=<den 00:00>, createdTill=<další den 00:00>)
activity_list(companyId=<id>, entityType="phonecall", status="SCHEDULED")
```

Obojí je vykoupené chybou ze suchého běhu: hovor bývá uložený i jako **událost**
nebo schůzka (dotaz na telefonáty ho nevidí), a ručně zapsaný hovor má často
`scheduledFrom: null` (časové okno na `scheduledFrom` ho **nikdy** nevrátí).

**Už zpracováno?** Ano, pokud mezi aktivitami klienta je taková, která:
- má `completed` do ±15 minut od konce nahrávky, **nebo**
- vznikla týž den a tematicky odpovídá obsahu hovoru, **nebo**
- má v `description` stopu s `recordingId` této nahrávky.

Zpracované tiše přeskoč — neohlašuj je jednu po druhé.

**Existuje naplánovaný hovor k dokončení?** Naplánovaný telefonát, jehož
`scheduledTill` už uplynul, je kandidát na přepsání tímto realizovaným — hovor
se prostě uskutečnil později, než bylo v kalendáři.

Posuď z přepisu, jestli se týká **téhož tématu** jako ten naplánovaný; téma ber
z jeho `title` a `description` v Raynetu. Sedí-li, **dokonči existující místo
zakládání nového** (krok 9). Zůstane tím vazba na OP a nevznikne duplicita ani
naplánovaný hovor, který by visel otevřený napořád.

Nesedí-li téma, založ nový a naplánovaný nech být — uživatel ho vyřídí zvlášť.

### 6. Najdi obchodní případ

```
businessCase_list(companyId=<id>, status="B_ACTIVE")
```

Vazba na OP je volitelná, ale hodnotná — drží hovor v kontextu úvěrového procesu.
Při jednom otevřeném OP ho navaž. Při více vyber podle obsahu hovoru, a nejde-li to
rozhodnout, zeptej se.

**Nový OP**, když žádný otevřený neodpovídá a z hovoru plyne **nová konkrétní
potřeba** — „klient chce hypotéku na 10 milionů", „refinancování bytu na firmu".
Obecné povídání o možnostech bez konkrétního záměru OP nezakládá. Parametry,
kategorie a výchozí fáze: `references/raynet-reference.md`, *Založení OP*.

OP zakládej **před** telefonátem, ať se na něj telefonát rovnou naváže.
Založení spustí automatiku Raynetu, která sama vytvoří úkoly „Zaslat nabídku_"
a „EPP 2" — ty z action items neduplikuj.

⚠️ **Správný OP nemusí patřit klientovi z hovoru.** Případy se jmenují podle banky
a produktu („Podnikatelský úvěr Moneta – nemovitost 2–3 mil. Kč") a hovor s jedním
člověkem se může týkat případu vedeného na někom úplně jiném — na spolužadateli,
manželce nebo tipaři. Když z obsahu plyne případ, který mezi OP spárovaného klienta
není, **zeptej se** místo toho, abys sáhl po jeho vlastním OP jen proto, že je po ruce.

### 7. Připrav obsah

Načti detail: `get_pocket_conversation(recording_ids=[…])`. Vrátí `summary.markdown`
a `audioUrl`.

`recordingDate` z tohoto volání je **konec** hovoru → `scheduledTill`.
(Začátek máš z kroku 2. Ta nekonzistence je reálná, ověřená, a snadno se na ni naletí.)

Text pro Raynet:

- **`solution`** = shrnutí hovoru. Sem patří Pocket Summary.
- **`description`** = kontext a vstupní zadání, pokud je co doplnit.

Obě pole jsou **HTML**, ne Markdown. Syrový Markdown se v CRM zobrazí jako doslovné
`###` a `**`. Na převod použij `scripts/md_to_raynet_html.py` — dělá i odstranění
proprietárních bloků `<pocket:chart>` a `<pocket:decision-tree>`, které Pocket do
shrnutí vkládá a v CRM nedávají smysl.

```bash
python3 scripts/md_to_raynet_html.py vstup.md
```

Podrobnosti o podporovaných značkách: `references/html-formatting.md`.

⚠️ **Citlivé údaje.** Přepisy obsahují rodná čísla, zůstatky úvěrů a čísla účtů.
Rodná čísla a čísla účtů do CRM nezapisuj — v shrnutí je vynech nebo nahraď.
Finanční parametry případu (výše úvěru, LTV, sazba, bonita) naopak patří dovnitř,
jsou to pracovní data.

### 8. Ukaž návrh a nech potvrdit

Než cokoli zapíšeš, vypiš přehledně:

```
Klient:    Peter Balent (id 599)
OP:        OP-26-0462 – Neúčelový úvěr, zástava byt Prokopova (fáze: Identifikace požadavku)
Telefonát: Konzultace k hypotéce na Slovensku
Kdy:       21. 9. 2026 15:48–15:57  (realizován)
Shrnutí:   <prvních pár řádků převedeného textu>
```

Co se navrhuje jinak než rutinně, v návrhu **viditelně označ**, ať to uživatel
nepřehlédne:

- klient s verdiktem `pravděpodobný`: `Klient: Ing. Jaroslav Semerák (41) ⚠ přepis „Semrád"`
- nový OP: `OP (nový): Hypotéka – koupě bytu Praha 3, 10 000 000 Kč`
- dokončení naplánovaného: `Dokončí naplánovaný 30517 „Storno HÚ ČS" ze 14:30`
- nový zájemce: `Lead (nový): Jan Novák – hypotéka na byt, zdroj: vlastní kontakt`
- soukromý hovor: `Osobní aktivita: „Soukromý hovor" 18:00–18:20, bez obsahu`

U dávky ukaž souhrn a pak polož jednu otázku na celek, ne na každý záznam zvlášť.
Když uživatel zápis potvrdí pro dávku, neptej se znovu u každé položky.

Když uživatel v návrhu něco opraví, zapiš do logu `outcome: edited` — z toho se
později pozná, kde skill chybuje a kde už ne.

### 9. Zapiš telefonát

Podle výsledku kroků 3 a 5 jedna ze tří větví.

**Větev A — dokončení naplánovaného hovoru.** Našel se naplánovaný telefonát
po termínu na stejné téma:

```
phonecall_update(
  id            = <id naplánovaného telefonátu>,
  status        = "COMPLETED",
  scheduledFrom = <skutečný začátek>,
  scheduledTill = <skutečný konec>,
  solution      = <HTML shrnutí>,
  description   = <doplň, nepřepisuj — viz níže>
)
```

`description` naplánovaného hovoru bývá **přípravou na hovor** a má svou hodnotu
(body k ověření, kontext případu). Načti si ho přes `phonecall_get`, ponech
a nové informace připoj za něj. Přepsat ho znamená smazat, co si uživatel předem
připravil.

Vazbu na `company` ani `businessCase` neposílej — už tam je a je správná.

Tahle větev **přepisuje existující záznam**. Hodnoty z `phonecall_get` (`status`,
`scheduledFrom`, `scheduledTill`, `description`, `solution`) ulož do logu jako
`before` — přes MCP neexistuje undo a tohle je jediná cesta, jak přepis vrátit.
Skript `audit_log.py` přepis bez `before` ani nezapíše.

**Větev B — nový telefonát.** Ve všech ostatních případech:

```
phonecall_create(
  title        = <název nahrávky, očištěný>,
  owner        = 2,
  company      = <clientId>,
  businessCase = <bcId nebo vynech>,
  status       = "COMPLETED",
  scheduledFrom = <začátek, 'yyyy-MM-dd HH:mm'>,
  scheduledTill = <konec>,
  solution     = <HTML shrnutí>,
  description  = <HTML kontext, volitelně>
)
```

U nového zájemce pošli `lead=<leadId>` místo `company` — klient zatím neexistuje.

**Větev C — soukromý hovor** (krok 3): `phonecall_create` s `personal=true`,
`category=112` (soukromá aktivita), `owner=2`, `status="COMPLETED"` a časy — **bez**
`company`, `description` a `solution`. Název krátký a neutrální („Soukromý hovor",
„Lékař"), nesmí prozradit obsah. Podrobně: `raynet-reference.md`, *Soukromé aktivity*.

Poznámky, které ušetří chybu:

- `owner` je povinný a nemá default. Adam Pospíšil = **2**.
- `status="COMPLETED"` přepíše `completed` server-side. **Neposílej `completed`
  zároveň se `status`** — vyhraje `status` a tvoje hodnota se zahodí.
- Telefonát **nemá pole `person`**, CRM to strukturálně zakazuje. Kontaktní osobu
  navaž přes `participants`.
- Zápisové nástroje Raynetu běží na dva kroky: první volání vrátí náhled
  a `confirmToken`, druhé se stejnými argumenty plus tokenem zápis provede.
  Token platí 60 sekund a **nikdy se nevymýšlí**.

Na konec `description` přidej stopu ke zdroji, ať je záznam dohledatelný:

```html
<p>— Zdroj: Pocket recording &lt;recordingId&gt; —</p>
```

Po každém zápisu — i po každém zamítnutém návrhu — zapiš řádek do audit logu
(viz [Audit log](#audit-log)).

### 10. Navazující aktivity

`search_pocket_actionitems(recordingDateFrom=…, recordingDateTo=…)` vrátí úkoly,
které Pocket z hovoru vytěžil. Filtruj na `recordingId` zpracovávané nahrávky.

| Pocket `actionType` | Co udělat |
|---|---|
| `create_reminder` s termínem | `task_create` (`deadline` povinný) |
| `create_reminder` = zavolat | `phonecall_create(status="SCHEDULED")` |
| `draft_email` | **koncept e-mailu**, viz níže |
| `send_message` | text zprávy vypiš v souhrnu připravený ke zkopírování (SMS/WhatsApp přes MCP poslat nejde) |

Zakládej jen položky s `assignee: "me"` a `status: "TODO"`. To, co má udělat klient,
do CRM jako úkol nepatří.

Po zápisu uzavři smyčku v Pocketu:
`update_pocket_actionitem(actionItemId=…, status="COMPLETED")`.
Priorita se při čtení vrací malými písmeny, při zápisu vyžaduje velká.

#### Podklady od klienta

Řeší-li se v hovoru úvěr, zjisti, co už od klienta je a co chybí, a chybějící
vyžádej e-mailem. Seznam podkladů podle případu a celý postup:
**`references/podklady.md`**. Ve zkratce:

1. **Co je potřeba** — podle typu příjmu, účelu úvěru a fáze případu.
2. **Co už je** — oddíl „PODKLADY OD KLIENTA" v popisu OP, e-maily od klienta
   v Raynetu (`activity_list(companyId)` → řádky `_entityName: "Email"`) a co
   zaznělo v hovoru. Jako přílohy v Raynetu ani na Drive doklady nejsou.
3. **Koncept e-mailu** jen s tím, co chybí. Co si Adam zajistí sám (LV, kupní
   smlouva z katastru), po klientovi nechtěj.
4. **Zapiš do popisu OP**, co bylo vyžádáno — `businessCase_update` přepisuje celý
   popis, takže načti, připoj, a původní popis ulož do logu jako `before`.

#### E-maily

E-mail se **nikdy neodesílá** — jen připraví. Uživatel ho upraví a odešle sám.

```bash
python3 scripts/make_email_draft.py --to klient@example.cz --subject "…" --body telo.md \
        [--cc kolega@egfin.cz] [--attach soubor.pdf]
```

Vznikne `.eml` s hlavičkou `X-Unsent: 1`, na které záleží: bez ní Apple Mail otevře
soubor jako **přijatou** zprávu jen pro čtení a text se musí kopírovat jinam. S ní se
otevře jako koncept v okně pro psaní, kde jde všechno upravit. Podpis se připojí sám.

- **Adresu příjemce ber z Raynetu** (`primaryAddress.email` klienta), ne z Pocketu.
  Pocket v `payload.email.to` adresy vymýšlí — v datech je `josef.novotny@example.com`
  nebo místo adresy jen jméno. Když v Raynetu adresa není, zeptej se.
- **Před psaním otevři `references/email-style.md`** — stavba, formulace a pravopis
  podle Adamových skutečných e-mailů. Návrh od Pocketu ber jako obsahový podklad,
  ne jako hotový text.
- Když uživatel koncept upraví a řekne co (nebo vloží finální verzi), vytáhni
  z rozdílu pravidlo a připiš ho do sekce *Naučená pravidla* v `email-style.md`.
  Tak se návrhy postupně blíží tomu, jak píše. (Kde jsou soubory skillu jen
  pro čtení, pravidlo aspoň vypiš a navrhni ho doplnit.)

### 11. Shrň, co vzniklo

Vypiš, co bylo založeno (s id), co přeskočeno a proč, a co zůstalo na uživateli
(typicky převod nového leadu na klienta v Raynet UI). U dávky stačí tabulka.

## Když něco nesedí

| Situace | Reakce |
|---|---|
| Klient nenalezen, ale měl by tam být | Zastav a zeptej se — nejspíš selhalo párování |
| Nový zájemce | Navrhni lead, ne klienta přes `company_create` |
| Víc kandidátů na klienta | Zastav, předlož seznam |
| Hovor se týká víc klientů najednou | Nezapisuj, přeskoč s důvodem — typicky hovor s bankéřem |
| Případ z hovoru není mezi OP klienta | Zeptej se; nesahej po jiném OP jen proto, že je po ruce |
| Backend vrátí chybu u id | Nezkoušej jiné id naslepo — chyba obvykle vyjmenuje platná |
| `confirmToken` vypršel | Zopakuj náhled, získej nový token |
| Nahrávka bez obsahu | Přeskoč, zmiň v souhrnu |
| Raynet nedostupný | Zastav celou dávku, nic nezapisuj napůl |
| Klient má v CRM duplicitu | Zastav, předlož oba záznamy — nevybírej sám |

## Režimy potvrzování

Každý typ akce má svůj režim. Všechno, co mění CRM, začíná na potvrzování — a vypíná
se až tehdy, když data ukážou, že to běží dobře. Ne dřív.

| Akce | Režim | Proč |
|---|---|---|
| Nový realizovaný telefonát | potvrdit | první kandidát na automatiku — chybný záznam se snadno opraví |
| Soukromý hovor jako osobní aktivita | potvrdit | jde o soukromí — plést se tu nesmí |
| Dokončení naplánovaného telefonátu | potvrdit | přepisuje existující záznam |
| Nový lead | potvrdit | nový zájemce v CRM |
| Nový OP | potvrdit | spouští automatiku Raynetu (úkoly) |
| Zápis do evidence podkladů v OP | potvrdit | přepisuje popis OP |
| Úkol, naplánovaný telefonát | potvrdit | |
| Koncept e-mailu | bez potvrzení | nic se neodesílá, jen vznikne soubor k úpravě |
| Uzavření action itemu v Pocketu | bez potvrzení | navazuje na už potvrzený zápis |

Režim mění jen uživatel. Podkladem je:

```bash
python3 scripts/audit_log.py stats
```

U každého typu akce ukáže, kolik návrhů prošlo beze změny, a upozorní, když
z posledních 20 byl opraven nejvýš jeden. Akce, které přepisují existující záznam,
nech na potvrzení déle než ty, které jen zakládají nové: chybný nový záznam se
opraví, přepsaný původní obsah se vrací jen z logu.

## Audit log

Každou akci zapiš do logu — i přeskočení, eskalaci a zamítnutý návrh. Když skill
udělá desítky akcí denně, jiná cesta, jak zpětně zjistit, co kdy zapsal a proč,
neexistuje.

```bash
echo '{"action": "create_phonecall", "outcome": "confirmed", "entity_id": 35927}' | python3 scripts/audit_log.py append
```

| Pole | Obsah |
|---|---|
| `action` | `create_phonecall`, `create_personal_activity`, `complete_phonecall`, `create_scheduled_phonecall`, `create_task`, `create_lead`, `create_business_case`, `update_business_case`, `draft_email`, `complete_action_item`, `skip`, `escalate` |
| `outcome` | `confirmed` · `edited` (uživatel něco opravil) · `rejected` · `auto` · `skipped` |
| `mode` | `confirm` (výchozí) nebo `auto` |
| vazby | `recording_id`, `client_id`, `business_case_id`, `entity`, `entity_id` |
| `before`, `after` | stav polí před a po změně — **u přepisů je `before` povinné** |
| `note` | proč — hlavně u `skip` a `escalate` |

Log leží v `~/.pocket-to-raynet/audit.jsonl` (nebo v `$POCKET_RAYNET_LOG`), záměrně
mimo repozitář — obsahuje jména klientů. Prohlížení: `audit_log.py show --date …`.
V prostředí bez trvalého disku (chat na claude.ai) se log nezachová; tam zapsané
řádky vypiš na konci do souhrnu.

## Reference

Načti podle potřeby, ne dopředu:

- **`references/raynet-reference.md`** — číselníky, id fází OP, kategorie aktivit,
  povinná pole jednotlivých entit, sémantika přepisu u `tags` a `participants`.
  Otevři při práci s kategoriemi, fázemi OP nebo při chybě validace.
- **`references/pocket-reference.md`** — tvary odpovědí obou režimů hledání,
  formáty `recordingId`, limity action items. Otevři při nečekaném tvaru dat.
- **`references/html-formatting.md`** — co Raynet v HTML polích unese a co ne.
  Otevři při ručním sestavování HTML mimo skript.
- **`references/email-style.md`** — jak Adam píše e-maily, včetně naučených pravidel.
  Otevři před každým konceptem e-mailu.
- **`references/podklady.md`** — jaké podklady chtít podle typu případu, kde zjistit,
  co už přišlo, a jak vést evidenci v popisu OP. Otevři, když se v hovoru řeší úvěr.

Skripty ve `scripts/` potřebují jen Python 3 se standardní knihovnou.
