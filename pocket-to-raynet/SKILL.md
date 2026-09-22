---
name: pocket-to-raynet
description: >-
  Zapisuje hovory nahrané v Hey Pocket do Raynet CRM jako realizované telefonáty
  včetně shrnutí, vazby na klienta a obchodní případ, a zakládá navazující aktivity
  z action items. Použij vždy, když uživatel chce dostat hovor, nahrávku, telefonát
  nebo konzultaci do Raynetu nebo do CRM — i když řekne jen „zapiš ten hovor",
  „hoď to do CRM", „zpracuj dnešní hovory", „co jsem dnes navolal, dej to ke klientům"
  nebo „udělej z toho aktivitu". Spusť i tehdy, když uživatel nezmíní Pocket ani Raynet
  jménem, ale jde o převod nahraného hovoru na CRM záznam, o follow-up z hovoru,
  nebo o dohledání, jestli už je hovor v CRM zapsaný.
---

# Pocket → Raynet

Převádí nahrávky hovorů z Hey Pocket na realizované telefonáty v Raynet CRM.

Prostředí je **finanční poradenství — hypotéky a investiční nemovitosti**. Hovory jsou
konzultace s klienty, bankéři a kolegy. Do CRM patří jen ty klientské.

## Jak to funguje

Proces je **interaktivní, ne automatický**. Uživatel ho spustí pokynem, ty připravíš
návrh a **před zápisem ho necháš potvrdit**. Není to opatrnost pro opatrnost: Raynet
obsahuje přes 1000 klientů, z toho ~94 % fyzických osob, mezi nimi už existující
duplicity, a Pocket komolí jména v přepisech. Špatně spárovaný hovor skončí u cizího
člověka a nikdo si toho nevšimne. Potvrzení stojí pět vteřin, oprava půl hodiny.

Zápis do CRM je navíc **nevratný přes MCP** — žádný `delete` nástroj neexistuje.

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
krok 5. Když uživatel klienta jmenuje, využij toho.

### 2. Načti nahrávky

`search_pocket_conversations` s `recordingDateAfter` / `recordingDateBefore`.
Bez `query` běží recency režim, který vrací plné přepisy po 5 na stránku.

`query` použij jen na dohledání konkrétní nahrávky podle tématu. **Nespoléhej na něj
při hledání podle jména klienta** — vrací sekční zásahy, opakuje tutéž nahrávku
víckrát a jméno v titulku spolehlivě netrefí. Vždy deduplikuj podle `recordingId`.

`recordingDate` ze `search_*` je **začátek** hovoru. Zapamatuj si ho, je to klíč
pro krok 3 i pro `scheduledFrom`.

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

Hraniční případy nezahazuj potichu — vypiš je jako přeskočené s důvodem, ať má
uživatel možnost říct „tenhle zapiš".

Skill si nepamatuje, co jsi minule vědomě přeskočil. Proto se při opakovaném běhu
přes stejné okno vynoří znovu. Řešením je posouvat datové okno dopředu, ne to řešit
v rámci skillu.

### 4. Spáruj klienta

Klienti jsou v Raynetu záznamy entity `company` — i fyzické osoby. Hledej v tomto
pořadí a **vždy ověř kombinací e-mail + příjmení**:

1. `company_list(email=…)` — nejlepší pokrytí (~97 %), ale **e-mail není unikátní**.
   Běžně ho sdílí majitel se svojí s.r.o., manželé, a v jednom ověřeném případě
   dva různí lidé. Proto samotná shoda e-mailu nestačí.
2. `company_list(name="Příjmení")` — case-insensitive substring.
3. `company_list(fulltext=…)` — jen celá slova a prefixy, ne libovolný substring.
4. `lead_list(…)` — nový zájemce bývá nejdřív lead, ne klient.

**Pozor na komolení jmen.** Pocket přepisuje totéž příjmení různě — ověřeno
`Balint`/`Balent`, `Hasová`/`Hasolová`, `Pejro`/`Pejřil`/`Pejza`. Fulltext na
jméno z přepisu vrátil nula zásahů u klientky, která v CRM je. Zkoušej varianty
a fonetické blízké tvary; jméno z přepisu ber jako nápovědu, ne jako klíč.

Vyhodnocení:

| Výsledek | Co udělat |
|---|---|
| právě 1 jistý zásah | pokračuj |
| víc kandidátů | **zastav**, vypiš je s id, jménem, e-mailem a vlastníkem, nech vybrat |
| 0 zásahů | **zastav**, viz níže |

🛑 **Nového klienta nikdy nezakládej.** `company_create` umí vytvořit jen organizaci,
ne fyzickou osobu — vznikl by záznam špatného typu, který se bude jinak chovat při
každém dalším párování. Když klient v CRM není, řekni to a vyzvi uživatele, ať ho
založí v Raynet UI; pak pokračuj.

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

Proč zrovna takhle — obojí je vykoupené chybou z ostrého provozu:

- **`activity_list`, ne `phonecall_list`.** Hovor se v Raynetu běžně zapisuje i jako
  **událost** (`Event`) nebo schůzka, ne jen jako telefonát. Dotaz na telefonáty
  takový záznam nevidí a hovor by se zapsal podruhé.
- **Filtr přes `createdFrom`, ne přes `scheduledFrom`.** Ručně zapsaný hovor má často
  `scheduledFrom: null` a vyplněný jen `completed`. Časové okno na `scheduledFrom`
  takový záznam **nikdy nevrátí**, ať je okno jakkoli široké.

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
rozhodnout, zeptej se. Při žádném založ telefonát bez vazby a zmiň to; zakládat OP
sám nemáš.

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

U dávky ukaž souhrn a pak polož jednu otázku na celek, ne na každý záznam zvlášť.
Když uživatel zápis potvrdí pro dávku, neptej se znovu u každé položky.

### 9. Zapiš telefonát

Podle výsledku kroku 5 jedna ze dvou větví.

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

### 10. Navazující aktivity

`search_pocket_actionitems(recordingDateFrom=…, recordingDateTo=…)` vrátí úkoly,
které Pocket z hovoru vytěžil. Filtruj na `recordingId` zpracovávané nahrávky.

| Pocket `actionType` | Raynet |
|---|---|
| `create_reminder` s termínem | `task_create` (`deadline` povinný) |
| `create_reminder` = zavolat | `phonecall_create(status="SCHEDULED")` |
| `draft_email`, `send_message` | `task_create` — e-mail jako aktivitu **nelze založit** |

Zakládej jen položky s `assignee: "me"` a `status: "TODO"`. To, co má udělat klient,
do CRM jako úkol nepatří.

Po zápisu uzavři smyčku v Pocketu:
`update_pocket_actionitem(actionItemId=…, status="COMPLETED")`.
Priorita se při čtení vrací malými písmeny, při zápisu vyžaduje velká.

### 11. Shrň, co vzniklo

Vypiš, co bylo založeno (s id), co přeskočeno a proč, a co zůstalo na uživateli
(typicky ruční založení klienta). U dávky stačí tabulka.

## Když něco nesedí

| Situace | Reakce |
|---|---|
| Klient nenalezen | Zastav, vyzvi k ručnímu založení v Raynet UI |
| Víc kandidátů na klienta | Zastav, předlož seznam |
| Hovor se týká víc klientů najednou | Nezapisuj, přeskoč s důvodem — typicky hovor s bankéřem |
| Případ z hovoru není mezi OP klienta | Zeptej se; nesahej po jiném OP jen proto, že je po ruce |
| Backend vrátí chybu u id | Nezkoušej jiné id naslepo — chyba obvykle vyjmenuje platná |
| `confirmToken` vypršel | Zopakuj náhled, získej nový token |
| Nahrávka bez obsahu | Přeskoč, zmiň v souhrnu |
| Raynet nedostupný | Zastav celou dávku, nic nezapisuj napůl |

Rate limit je 24 000 requestů denně a běžně je z velké části volný;
`rate_limit_status` se do limitu nepočítá, takže se na něj dá před dávkou podívat zdarma.

## Reference

Načti podle potřeby, ne dopředu:

- **`references/raynet-reference.md`** — číselníky, id fází OP, kategorie aktivit,
  povinná pole jednotlivých entit, sémantika přepisu u `tags` a `participants`.
  Otevři při práci s kategoriemi, fázemi OP nebo při chybě validace.
- **`references/pocket-reference.md`** — tvary odpovědí obou režimů hledání,
  formáty `recordingId`, limity action items. Otevři při nečekaném tvaru dat.
- **`references/html-formatting.md`** — co Raynet v HTML polích unese a co ne.
  Otevři při ručním sestavování HTML mimo skript.
