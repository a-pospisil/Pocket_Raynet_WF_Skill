---
name: pocket-to-raynet
description: >-
  Zapisuje hovory a schůzky nahrané v Hey Pocket do Raynet CRM: stručný strukturovaný
  zápis k aktivitě (dokončí naplánovanou, jinak založí realizovanou), kartu případu
  v popisu obchodního případu včetně tabulky nájmů a bonity po bankách, vlastní pole
  klienta, jeden souhrnný úkol s návrhem e-mailu a návrh posunu fáze. Ráno umí připravit
  dnešní schůzky. Použij vždy, když uživatel chce dostat hovor, nahrávku, telefonát,
  schůzku nebo konzultaci do Raynetu nebo do CRM — i když řekne jen „zapiš ten hovor",
  „hoď to do CRM", „zpracuj dnešní hovory", „dej to ke klientům", „udělej z toho aktivitu"
  nebo „připrav mi dnešní schůzky". Spusť i tehdy, když uživatel nezmíní Pocket ani Raynet
  jménem, ale jde o převod nahraného hovoru na CRM záznam, o follow-up z hovoru,
  o dohledání, jestli už je hovor v CRM zapsaný, nebo o přípravu na schůzku s klientem.
compatibility: >-
  Vyžaduje MCP servery Hey Pocket (plán Pro) a Raynet CRM, a Python 3 pro skripty
  (jen standardní knihovna).
metadata:
  version: "0.4.0"
  hermes:
    tags: [crm, raynet, pocket, hypoteky, email]
---

# Pocket → Raynet

Převádí nahrávky hovorů a schůzek z Hey Pocket na stručné, strukturované zápisy v Raynet CRM.

Prostředí je **finanční poradenství: hypotéky a investiční nemovitosti** (Evergreen Finance). Hovory jsou konzultace s klienty,
bankéři, odhadci, makléři a kolegy. Skill běží v Claude Code i v orchestrátoru **Hermes** (každý poradce má vlastní instanci
s vlastním Pocketem a Raynetem). Proto nepoužívá nástroje vázané na jedno prostředí: potvrzení je obyčejná otázka v chatu.

## Tvrdá pravidla

Platí vždy, bez výjimky. Zdůvodnění: `docs/NAVRH-ZAPISY.md`, kap. 4a.

1. **Nikdy nezapsat pod jiného klienta.** Klient je jistý jen při shodě dvou nezávislých znaků (e-mail nebo telefon + příjmení),
   nebo když ho uživatel jmenuje. Jinak se zeptej.
2. **Naplánovanou aktivitu z téhož dne dokonči, nezakládej novou.** Když u klienta visí telefonát, schůzka nebo událost
   naplánovaná **na stejný den**, kdy hovor proběhl, a podle Pocketu proběhla v jiný čas (později i dřív), označ jako hotovou
   tu původní (krok 5, větev A; Událost větev A2). Aktivitu naplánovanou na jiný den ani nenaplánovanou nedokončuj (Adam, 1. 10. 2026).
3. **Při nejistotě se zeptej** (klient, OP, aktivita k dokončení, rozdělení hovoru, posun fáze). Zápis přes MCP nejde smazat.
4. **Nic nemaž a nic neruš sám od sebe.** Duplicitní nebo testovací telefonát zruš (`status="CANCELLED"`) jen na výslovný
   pokyn uživatele. Schůzky s pozvánkou nikdy: zrušení v Raynetu je smaže i v Google kalendáři.
5. **Rodná čísla, čísla účtů a údaje z dokladů jen z dokumentu, nikdy z hovoru.** Z přepisu ani ze shrnutí Pocketu je nepřebírej
   (čísla komolí). Do karty klienta (`Rodne_cisl`, `bankAccount`, číslo OP, kdo OP vydal, platnost OP, rodné příjmení, státní
   příslušnost) je zapiš jen z dokumentu, který máš k dispozici (DP, výpis, smlouva, doklad), v náhledu s uvedením zdroje
   (Adam, 1. 10. 2026; doklady 12. 10. 2026). V textu zápisu je nikdy neuváděj.
6. **Bez potvrzení se nic nezapíše.** Nejdřív náhled, pak zápis.
7. **Zápis nikdy do Události.** Událost (`Event`) nemá v rozhraní Raynetu pole „Výsledek“: zápis uložený do jejího `solution`
   se na kartě klienta nezobrazí. Zápis patří jen do Schůzky (`Meeting`) nebo Telefonátu (`PhoneCall`). Naplánovaná Událost
   se řeší větví A2 v kroku 9 (Adam, 12. 10. 2026).

## Postup

### 0. Zjisti, kdo zapisuje

```
user_info()                          → username (e-mail přihlášeného uživatele)
person_list(email=<username>)        → id = owner pro všechny zápisy
```

Vlastník se nikdy nezadává napevno. Každý poradce zapisuje sám za sebe (Adam = 2, ostatní viz `references/raynet-reference.md`).

### 1. Zjisti rozsah

| Pokyn | Rozsah |
|---|---|
| „zapiš poslední hovor" | 1 nejnovější nahrávka |
| „zpracuj dnešní hovory" | `recordingDateAfter` = dnešní půlnoc |
| „zapiš hovor s Novákem" | konkrétní nahrávka, klient zadaný ručně (nejbezpečnější varianta) |
| „připrav dnešní schůzky" / ranní běh | režim **Příprava**, viz konec souboru |

Když to z pokynu nejde určit, zeptej se. Skill si mezi spuštěními nic nepamatuje, stav drží Raynet.

### 2. Načti nahrávky

`search_pocket_conversations` s `recordingDateAfter` / `recordingDateBefore` (recency režim bez `query`, 5 na stránku).
`query` jen na dohledání podle tématu, ne podle jména. Vždy deduplikuj podle `recordingId`.

`recordingDate` ze `search_*` je **začátek** hovoru (→ `scheduledFrom`).

### 3. Roztřiď nahrávky a vyber šablonu

| Typ | Co s ním | Šablona |
|---|---|---|
| krátký klientský hovor (do ~3 min, stav podkladů, termín) | zapsat | **S** mikrozápis |
| follow-up, nabídka, průběh žádosti, čerpání, servis | zapsat | **M** |
| úvodní schůzka, strategická konzultace, roadmapa bonity | zapsat + karta OP + bonita | **L** |
| třetí strana k případu (odhadce, makléř, developer, RK, advokát, notář, úschova, účetní, daňový poradce) | zapsat k OP klienta, bez OP ke klientovi | S/M |
| kolega: předání nebo porada ke konkrétnímu případu | zapsat k OP | S/M |
| **bankéř přes víc případů** | **rozdělit**: ke každému jistě spárovanému klientovi S do jeho OP, zbytek se zeptat | S × N |
| nový zájemce, který v CRM není | lead (krok 4) | S |
| diktát sobě, interní porada bez klienta, appka, osobní, lékař, Broker Trust, prázdné, nepřijatý hovor | **nezapisovat** | – |

Hraniční případy nezahazuj potichu: vypiš je jako přeskočené s důvodem. Šablony a zásady psaní: **`references/sablony-zapisu.md`**
(otevři vždy před psaním textu).

### 4. Spáruj klienta

Klienti jsou záznamy `company`, i fyzické osoby. Hledej v tomto pořadí a **vždy ověř dvěma znaky**:

1. `company_list(email=…)`: nejlepší pokrytí, ale e-mail **není unikátní** (manželé, majitel a jeho s.r.o.).
2. `company_list(name="Příjmení")`: podřetězec, bez ohledu na velikost písmen.
3. `company_list(fulltext=…)`: jen celá slova a prefixy.
4. `lead_list(…)`: nový zájemce bývá nejdřív lead.

Pocket komolí jména (`Novak`/`Novák`/`Nowak`, `Dvořáková`/`Dvořáčková`; jména jsou ilustrační) a cizí jména bývají v CRM
zapsaná foneticky (`Schneider` → `Šnajdr`). Filtr `name` je podřetězec, ale **rozlišuje diakritiku** (ověřeno: příjmení bez háčku
klienta s háčkem nenajde) a přepis bývá v pádě („s Honzou Novákem"). Jméno z přepisu je nápověda, ne klíč. Na hledání použij
`scripts/match_name.py`:

```bash
python3 scripts/match_name.py variants "Honzou Novákem"          # hledací výrazy pro company_list(name=…)
python3 scripts/match_name.py score "Honzou Novákem" odp1.json odp2.json   # seřadí kandidáty z odpovědí
```

`score` porovnává foneticky, bez diakritiky a titulů, v libovolném pořadí slov a zná domácké podoby (Honza = Jan). Jeho verdikt
(`jistý` / `pravděpodobný` / `nejistý` / `žádný`) se týká **jen jména**, tedy jednoho znaku ze dvou: druhý znak (e-mail nebo telefon)
ověř zvlášť (tvrdé pravidlo 1). U klienta vedeného v CRM dvakrát vrátí `nejistý` a nehádá.

| Výsledek | Co udělat |
|---|---|
| právě 1 zásah se dvěma shodnými znaky | pokračuj |
| víc kandidátů nebo jen jeden znak | **zastav**, vypiš kandidáty (id, jméno, e-mail, vlastník), nech vybrat |
| 0 zásahů | navrhni **lead** (`lead_create`: `topic`, `firstName`, `lastName`, `leadPerson=true`, kontakt, zdroj). Po potvrzení založ a zápis naváž na lead. Klienta (fyzickou osobu) přes MCP nezakládej. Výjimka jen na výslovný pokyn „založ klienta“: viz níže. |

Když hovor zjevně navazuje na rozjednaný případ (zmiňuje OP, dřívější podklady, předchozí schůzku), 0 zásahů znamená spíš
chybu párování než nového zájemce: zeptej se, lead nezakládej.

**Založení klienta na výslovný pokyn.** `company_create` vytvoří vždy organizaci. Povinné a výchozí: `name` = „Jméno Příjmení“,
`role="A_SUBSCRIBER"`, `state="A_POTENTIAL"`, `rating="C"`, `owner` = poradce, který hovor vedl. K tomu, co jistě zaznělo:
kontakt a adresa (vždy s `addressName`), `contactSource`, tipař (`category`, jen výslovně jmenovaný), vlastní pole a Profil
klienta (krok 11). V souhrnu uveď „v UI přepnout na fyzickou osobu, jméno a příjmení zvlášť“.

**Klient není vždy ten, s kým se mluví.** Hovor s partnerem, rodičem nebo známým patří k tomu, kdo bude dlužníkem.
Mluvčího navaž přes `participants`.

### 5. Zkontroluj, co už u klienta je

```
activity_list(companyId=<id>, createdFrom=<den 00:00>, createdTill=<další den 00:00>)
activity_list(companyId=<id>, status="SCHEDULED", scheduledFrom=<den hovoru 00:00>, scheduledTill=<den hovoru 23:59>)
```

Vždy `activity_list` přes všechny typy, ne `phonecall_list`: hovor bývá uložený i jako schůzka nebo událost.
Filtruj přes `createdFrom`, ne přes `scheduledFrom`: ručně zapsaný hovor má často `scheduledFrom: null`.

**Už zapsáno?** Ano, když aktivita klienta má štítek `AI zápis` nebo stopu s tímto `recordingId`, nebo `scheduledTill` do ±15 min
od konce nahrávky, nebo vznikla týž den a obsahem odpovídá. Zapsané tiše přeskoč.

**Naplánovaná aktivita k dokončení (tvrdé pravidlo 2).** Otevřený telefonát, schůzka nebo událost klienta naplánovaná
**na stejný den** jako hovor, která tématem odpovídá, se **dokončí**, i když hovor proběhl v jiný čas. Téma ber z jejího `title`
a `description`. Okno `scheduledFrom`/`scheduledTill` v `activity_list` funguje jako překryv, proto u každého kandidáta ověř,
že jeho vlastní `scheduledFrom` je opravdu ve dni hovoru.

U každého kandidáta čti **typ** (`_entityName`): `Meeting` a `PhoneCall` jdou do větve A, `Event` do větve A2 (tvrdé pravidlo 7).

| Situace | Co udělat |
|---|---|
| 1 otevřená schůzka nebo telefonát téhož dne, téma sedí | větev A: dokončit ji |
| 1 otevřená **událost** téhož dne, téma sedí | větev A2: do Události nezapisovat, v náhledu navrhnout převod na Schůzku |
| víc kandidátů téhož dne nebo nejasné téma | **zeptej se**, kterou dokončit |
| žádná aktivita téhož dne | větev B: nová realizovaná aktivita |

Naplánované schůzky z kalendáře bývají v Raynetu typu Událost (12. 10. 2026 všechny dnešní položky kalendáře; nejspíš je zakládá
synchronizace s Google kalendářem, `[k ověření]`). Větev A2 proto čekej často.

Otevřené aktivity z **jiných dní** a nenaplánované (`NEW`) nech beze změny. Uveď je jen v náhledu jako „visí otevřené:
<typ, název, datum>“, ať je uživatel může vyřídit ručně.

### 6. Najdi obchodní případ

```
businessCase_list(companyId=<id>, status="B_ACTIVE")
```

1 otevřený OP: naváž. Víc OP: vyber podle obsahu, a když to nejde jistě, zeptej se. Žádný a hovor žádný případ neřeší: zápis bez OP.

**Když hovor evidentně řeší konkrétní případ a klient pro něj nemá otevřený OP, navrhni založení OP** (Adam, 12. 10. 2026:
„pokud je evidentní, že se rovnou řeší OP, pak zakládej“; rozšiřuje pravidlo z 1. 10. o běžící žádosti). Evidentní = konkrétní
úvěrový záměr a k tomu aspoň dvě věci z: banka nebo produkt, částka, nemovitost nebo účel, termín, nabídka, žádost nebo podklady,
další krok poradce. Neevidentní: obecná konzultace bez záměru, servisní hovor (fixace končí za rok), „možná někdy“. Pak OP nezakládej
a v souhrnu napiš „případ zatím bez OP“.

Návrh OP v náhledu: název „banka/produkt – popis“, kategorie, fáze (10 Identifikace požadavku; 1 Nabídnuto, když nabídka odešla;
2 Podaná žádost, když je žádost podaná), banka v `producent`, výše (`totalAmount` + `vyse_uveru`; když ji neznáš, zeptej se),
zdroj (`source`, v UI povinný) a další pole, která jistě zazněla (`references/sablony-zapisu.md`, „Pole OP z hovoru“). Založ ho až
po potvrzení a zápis k němu naváž. Volající, který je jen lead, OP mít nemůže (OP potřebuje klienta): zápis jde k leadu a OP navrhni
až po převodu leadu na klienta v UI. Založení OP spustí automatiku se dvěma úkoly (`references/raynet-reference.md`), ty do checklistu
nepřebírej.

⚠️ OP se jmenují podle banky a produktu, ne podle klienta, a případ z hovoru může být vedený na spolužadateli nebo manželce.
Když z obsahu plyne případ, který mezi OP klienta není, nesahej po jiném OP: u evidentního případu navrhni nový OP, jinak **se zeptej**.

### 7. Připrav obsah

`get_pocket_conversation(recording_ids=[…])` vrátí `summary.markdown` a `recordingDate` = **konec** hovoru (→ `scheduledTill`).

Text piš podle `references/sablony-zapisu.md` (S / M / L). Když potřebuješ převést hotový Markdown, použij
`scripts/md_to_raynet_html.py` (odstraní `<pocket:*>` bloky a rediguje RČ a čísla účtů).

**Shrnutí Pocketu je jen rejstřík témat, fakta ber z přepisu.** Diarizace prohazuje mluvčí a AI shrnutí přisuzuje výroky
a plány špatné osobě. Případy z 22. 9.–1. 10. 2026: „klient odjíždí do Keni“ (do Keni jel Adam, klient na kongres),
„dcera jiného klienta“ (šlo o klienta, se kterým se mluvilo), „Adam jede do lázní“ (jela klientka). Proto:

1. Kdo co řekl, udělá, slíbil, kam jede, částky a data: vždy z přepisu (`get_pocket_conversation` s přepisem), ne ze shrnutí.
2. Jména osob a firem ověř proti Raynetu a e-mailům. Osoba nebo firma, která je ve shrnutí, ale v přepisu nezazní, je chyba
   shrnutí: do zápisu ji nepiš.
3. V náhledu uveď řádek **„Chyby Pocketu“**: co shrnutí tvrdí jinak než přepis a jak to je správně.
4. Mluvčí v Pocketu přes MCP přejmenovat nejde (nástroj chybí). Do souhrnu napiš „v Pocketu přejmenovat: Speaker 1 = …“,
   ať to uživatel opraví v appce.
5. Doporučení pro poradce: na začátku nahrávky nadiktovat jméno klienta a téma. Párování je pak jisté.

**Režim „doslovně Pocket“ (jen na výslovný pokyn).** Když uživatel řekne „přepiš zápis přesně z Pocketu, nic neměň“
(Adam, 12. 10. 2026), do `solution` jde AI shrnutí Pocketu (`summary.markdown`) **beze změny textu**, bez šablony S / M / L,
bez řádku „Chyby Pocketu“ a bez patičky. Jen převod Markdown → HTML skriptem
`scripts/md_to_raynet_html.py --check` (nadpisy tučně, odrážky jako seznam, vnořené odrážky uvnitř `<li>`; RČ a čísla účtů
skript dál rediguje). Přepínač `--check` ověří, že text bez značek je shodný s originálem; jinak se nezapisuje. Rozpory shrnutí
s přepisem napiš jen do chatu, ne do zápisu. Výchozí formát zůstává šablona podle `references/sablony-zapisu.md`, dokud
uživatel nerozhodne jinak.

Do textu patří i interní věci: další postup, rozdělení práce, ladění s kolegou. Zápis je interní, klient vidí jen návrh e-mailu.
**Rady k fakturaci nepiš** (jak má fakturace vypadat, komu a kolika odběratelům fakturovat). Fakturaci uveď jen tak, jak ji
klient sám popsal (Adam, 1. 10. 2026).

**Bonita (u šablony L, a kdykoli se v hovoru mění příjmy, závazky nebo záměr).** Pro **všech 8 bank** (ČS, ČSOB, KB, RB, UCB,
mBank, Oberbank, MONETA) podle metodiky:

- Zdroj pravidel: metodika bank na jednom místě v **Evergreen app** (napojení se připravuje). Do té doby Adamův vault `wiki/metodiky/`.
  U kolegy bez přístupu k metodice skill bonitu nepočítá a napíše „bonita: chybí přístup k metodice“.
  Začni `rychla-reference.md`, postup výpočtu a vzorce v `kalkulacky-bank.md` („Postup výpočtu krok za krokem“, „Kontrolní čísla“).
  Velké stránky nečti celé: blok „⚡ Rychle“, pak `grep -n "^## "` a jen potřebná sekce.
- Sazby z `temata/sazby-a-slevy-bank.md` (nejvýš 1 měsíc staré, jinak označit), stres podle metodiky banky.
- Chybějící vstup → **rozpětí min–max** s jednou větou, co je rozdílem. Nic nedomýšlet.
- Výstup: plný rozpad u každé banky a „projde u X z 8“ (formát v šablonách). Je to orientační výpočet, ne schválení.
- **Podnikatelské úvěry (MONETA SBL, úvěr pro s.r.o., Živnohypo) bonitu po 8 bankách nepočítají.** Místo ní parametry produktu
  (obrat, LTV, DSCR, limit) a co banka započte: např. nájmy z DPFO, celý úvěr spoludlužníka (Adam, 1. 10. 2026).

### 8. Ukaž náhled a nech potvrdit

```
Klient:     Jan Ukázkový (id 999, e-mail + příjmení ✓, vlastník Adam)
OP:         OP-26-0462 – Neúčelový úvěr, zástava byt Prokopova (fáze: Identifikace požadavku)
Aktivita:   DOKONČIT schůzku 32195 „Konzultace a výpočet“ (naplánováno 21. 9. 15:15, proběhlo 21. 9. 16:02–16:47)
            visí otevřené: telefonát „Doplnit výpisy“ (18. 9.) – beze změny
Šablona:    L · štítek AI zápis
Karta OP:   přepsat stav (nájmy 2 → 3, bonita 2,1–3,5 mil.); ruční text zachován
Karta kl.:  e-mail2 + telefon (nové) · zdroj = workshop · Pocet_deti 1 → 2 · profil přepsán (3 nemovitosti, fixace ČSOB 6/2028)
Úkol:       1 souhrnný úkol, 4 body, termín 6. 10., návrh e-mailu ano
Fáze OP:    návrh Identifikace požadavku → Nabídnuto (zapíše se jen po potvrzení)
Text:       <prvních 5 řádků zápisu>
```

Do náhledu patří i řádky `Účastníci:` (vlastník klienta, když není zapisující) a `Chyby Pocketu:` (krok 7).
U naplánované Události (větev A2) místo řádku `Aktivita:`:

```
Aktivita:   UDÁLOST 99001 „Jan Ukázkový“ (21. 9. 10:00) – do Události zápis nejde (nemá Výsledek).
            Volba a) převeď ji v Raynetu na Schůzku (detail aktivity → změna typu), pak zapíšu do Schůzky   ← výchozí
            Volba b) založím novou Schůzku se zápisem, Událost nechám beze změny k ručnímu smazání
```

U dávky souhrn a jedna otázka na celek, ale položka s nejistým klientem, OP nebo aktivitou se potvrzuje zvlášť. Dávku nad
~5 hovorů dej jako stránku k revizi (HTML nebo artefakt), kde uživatel u každého hovoru zvolí Zapsat / Doptat / Nezapisovat
a texty upraví přímo v náhledu. Zapisuj pak jen položky „Zapsat“ s upravenými texty.

### 9. Zapiš aktivitu

Zápisové nástroje Raynetu běží na dva kroky: první volání vrátí náhled a `confirmToken`, druhé se stejnými argumenty plus tokenem
zápis provede. Token platí 60 s a nikdy se nevymýšlí.

**Větev A: dokončení naplánované aktivity** (`phonecall_update` / `meeting_update` podle typu; `event_update` nikdy, viz A2):

```
<typ>_get(id)                                   → současný description, tags, participants
<typ>_update(
  id, status="COMPLETED",
  scheduledFrom=<skutečný začátek>, scheduledTill=<skutečný konec>,
  solution=<HTML zápis>,
  tags=<stávající štítky + ",AI zápis">
)
```

`description` (příprava, pozvánka, odkaz na Meet) **nech být**. Vazbu na klienta a OP neposílej, už tam je.
`participants` neposílej, pokud je neměníš (update přepíše celý seznam).

`status=COMPLETED` nastaví `completed` na `scheduledTill`. Když posíláš skutečný konec ve `scheduledTill`, sedí; jinak hned potom
`<typ>_update(id, completed=<konec>)` bez `status`. Po zápisu výsledek ověř přes `activity_list(companyId=<id>)`.

Větev A přepisuje existující záznam: hodnoty z `<typ>_get` ulož do audit logu jako `before` (viz [Audit log](#audit-log)).

**Větev A2: naplánovaná Událost** (tvrdé pravidlo 7). Typ aktivity přes MCP změnit nejde. Do Události **nic nezapisuj**
a v náhledu nabídni (formát v kroku 8):

- **a) převod v UI (výchozí):** uživatel v Raynetu přehodí Událost na Schůzku. Převod vytvoří **novou Schůzku s novým id**
  (název, čas, účastníci i případný výsledek se přenesou) a Událost zanikne; `event_get` na staré id pak vrací
  **502 Bad Gateway**, ne „nenalezeno“. Schůzku proto znovu dohledej přes `activity_list(companyId=<id>, entityType="meeting")`
  v okně dne hovoru a pokračuj větví A (`meeting_update`).
- **b) nová Schůzka:** když uživatel převod dělat nechce, `meeting_create` (stejný název a čas, `company`, klient v `participants`,
  `status="COMPLETED"`, `solution`, štítek `AI zápis`), pak `meeting_update(id, completed=<konec>)` bez `status`. Událost
  **neruš** (zrušení ji smaže i v Google kalendáři), jen ji v souhrnu uveď k ručnímu smazání.

**Větev B: nová realizovaná aktivita** (telefonát; u osobní nebo online schůzky `meeting_create`):

```
phonecall_create(
  title, owner=<krok 0>, company=<id> nebo lead=<id>, businessCase=<id nebo vynech>,
  status="COMPLETED", scheduledFrom=<začátek>, scheduledTill=<konec>,
  solution=<HTML zápis>, tags="AI zápis"
)
phonecall_update(id, completed=<konec>)          ← bez status; create nastaví completed na čas zápisu
```

Telefonát ani schůzka nemají pole `person`, kontaktní osobu navaž přes `participants`. Neposílej `completed` a `status` v jednom volání.

**Vlastník klienta musí zápis vidět.** Když vlastník klienta (`company.owner`, poradce) není ten, kdo zapisuje, přidej ho
do `participants` jako `{person: <owner id>}`. Jinak zápis ve svém přehledu neuvidí (Adam, 1. 10. 2026). U větve A pošli
celý seznam: stávající účastníky s jejich `id` + vlastníka.

### 10. Aktualizuj kartu OP

Jen když se změnil stav případu (vždy u šablony L). `businessCase_get` → sestav kartu podle šablony → `businessCase_update(description=…)`.
Ruční text, který v popisu napsal člověk, **zachovej** pod nadpisem „Původní poznámky“. „Klíčová rozhodnutí“ jen doplňuj.
**Pole OP z hovoru.** Když hovor evidentně řeší tento případ (stejná definice jako v kroku 6), doplň **prázdná** vlastní pole OP
podle `references/sablony-zapisu.md`, „Pole OP z hovoru“: jen co zaznělo, počítané hodnoty (LTV) se vzorcem, roletky přesným textem,
v náhledu „prázdné → nové“. Vyplněnou hodnotu přepiš jen jistou novou hodnotou a jako „staré → nové“. Výši OP (`totalAmount`)
existujícího OP měň jen na výslovný pokyn, např. „hodnota OP = 65 % z odhadu“ (odhad bývá jen v PDF příloze e-mailu, kterou MCP
nepřečte: zeptej se na částku). Fáze jen jako návrh (krok 13).

### 11. Doplň kartu klienta (maximum údajů)

Na kartu klienta patří **maximum toho, co z hovoru jistě plyne** a platí napříč případy. Jedno `company_update` po potvrzení:

- **standardní pole:** e-mail a telefon, adresa bydliště, IČO a DIČ (OSVČ), plátce DPH, zdroj kontaktu, tipař (`category`,
  určuje dělení provize, proto jen prázdné a výslovně jmenovaný tipař, jinak se zeptej), sociální sítě;
- **vlastní pole:** osobní (vzdělání, rodinný stav, zúžení SJM, počet dětí, hlavní banka), zaměstnání (čistý příjem, zaměstnavatel,
  pozice, nástup, HPP/DPČ/DPP), výdaje (bydlení, domácnost, stávající úvěry po řádcích), nájmy (v DP, současný a budoucí čistý
  nájem), podnikání (počátek, obor, svobodné povolání, paušál, paušální daň). Mapování „co zaznělo → klíč“ je v šabloně;
  bankovní řádky BT kredit jen z výpočtu, pole typu soubor jen čti;
- **Profil klienta v `notice`:** osoba a domácnost, vazby (spolužadatel, firma), příjmy, nemovitosti, závazky, konce fixací,
  cíle, servisní příležitosti, preferovaná komunikace. Ruční text zůstane pod „Původní poznámky“.

Před zápisem `company_get`. Prázdné doplň, existující přepiš jen jistou hodnotou a změnu „staré → nové“ ukaž v náhledu.
Měsíční příjem ze závislé činnosti je v poli vždy **čistý**. Zazní-li jen hrubý, přepočítej ho na čistý (vzorec v šabloně,
„Přepočet hrubé mzdy na čistou“) a v náhledu i v profilu ho označ „přepočet z hrubé“; doložená čistá mzda (páska, potvrzení
o příjmu, výpis) ho později přepíše (Adam, 12. 10. 2026).
Do `customFields` posílej jen měněné klíče (`null` nebo prázdná hodnota pole smaže). Kontakt nebo adresu vždy s `addressName`
(stávající, u prázdné „Sídlo klienta“), jinak update neprojde. Po zápisu `company_get` a kontrola, že pole sedí.
RČ a číslo účtu jen z dokumentu (tvrdé pravidlo 5). Co MCP neumí (jméno a příjmení zvlášť, titul, datum narození, příznak fyzické osoby), uveď v souhrnu
jako „doplnit v UI“. Pole, klíče a šablona profilu: `references/sablony-zapisu.md`, „Karta klienta“.

### 12. Souhrnný úkol

Drobnosti z hovoru jdou do **jednoho úkolu** (checklist: kdo · co · do kdy). Samostatný úkol jen pro věc s vlastním termínem
a řešitelem, kterou je potřeba hlídat zvlášť. Co dodá klient, je v zápisu a v návrhu e-mailu, ne v úkolech.

Úkol navrhuj jen u **aktivního případu s kroky poradce s termínem**. Jinak stačí „Další kroky“ v zápisu. Při revizi 1. 10. 2026
Adam ponechal navržený úkol jen u 1 ze 7 hovorů.

- `task_create(title, deadline, owner=<krok 0>, company=<id>, businessCase=<id>, description=<checklist + návrh e-mailu>, tags="AI zápis")`.
- **Checklist s odškrtáváním** (formát v šabloně): bod = `☐ kdo · co · do kdy`, splněný `☑ … · hotovo <datum>`. `deadline` úkolu
  = termín nejbližšího otevřeného bodu, ať Raynet upozorní včas. Raynet zaškrtávací políčka v úkolu nemá, `☐`/`☑` jsou znaky textu.
- **Odškrtávání:** (a) při každém dalším běhu ke klientovi načti otevřené úkoly se štítkem „AI zápis“
  (`task_list(companyId=<id>, tags="AI zápis")`, stav není COMPLETED/CANCELLED) a body, které podle hovoru, e-mailu nebo zápisu
  evidentně proběhly, navrhni v náhledu odškrtnout; (b) na pokyn v chatu („odškrtni odhadce u Nováka“). Po odškrtnutí posuň
  `deadline` na další otevřený bod. Když jsou odškrtnuté všechny, navrhni úkol dokončit (`status="COMPLETED"`, do `solution`
  jedna věta, co se udělalo). Nové body z hovoru přidej do existujícího otevřeného úkolu, nový úkol nezakládej.
- Řešitel jiný než zapisující: po založení `task_get` a přepsat osobu u druhého účastníka v `participants`
  (`resolverPerson` nefunguje). Výsledek ověř přes `task_get`.
- Návrh e-mailu klientovi patří do popisu úkolu po úvodní schůzce, po nabídce a vždy, když v hovoru zazní „pošlu vám…“.
  Když uživatel chce e-mail „sem do chatu“, dej ho do chatu ke zkopírování (Adam, 12. 10. 2026). Co se vyřešilo na místě
  (např. faktura zaplacená při schůzce), do e-mailu nepiš.
- **Návrh e-mailu** piš podle `references/email-style.md` (stavba a formulace z Adamových e-mailů a pravidla naučená z jeho úprav).
  Podklady chtěj jen ty, které chybí: co je potřeba podle typu případu a kde zjistit, co už přišlo, je v `references/podklady.md`.
  Co si poradce zajistí sám (LV, kupní smlouva z katastru), po klientovi nechtěj.
- **Adresu příjemce ber z Raynetu**, ne z Pocketu: Pocket v `payload.email.to` adresy vymýšlí nebo místo adresy dá jen jméno.
- Když uživatel chce koncept **do pošty**, vyrob `.eml` přes `scripts/make_email_draft.py`. Hlavička `X-Unsent: 1` zajistí, že se
  v Apple Mail otevře jako koncept k úpravě, ne jako přijatá zpráva jen pro čtení. Nic se neodesílá. Podpis je
  v `assets/signature.txt` (Adamův; kolega si ho nahradí svým).
- Když uživatel návrh upraví a řekne co (nebo vloží finální verzi), připiš z rozdílu pravidlo do *Naučená pravidla*
  v `email-style.md`.
- Action items z Pocketu (`search_pocket_actionitems`, filtr na `recordingId`) slouč do checklistu. Po zápisu je v Pocketu uzavři
  (`update_pocket_actionitem(status="COMPLETED")`; priorita se při zápisu píše velkými písmeny).

### 13. Posun fáze OP (jen návrh)

Když hovor jasně posunul případ (nabídka odeslána → „Nabídnuto“, žádost podána → „Podaná žádost + EPP 2.0“, schváleno, podepsáno),
navrhni posun v náhledu. Po potvrzení `businessCase_update(businessCasePhase=<id>)`. Id fází: `references/raynet-reference.md`.
Nic jiného na OP neměň. Výjimka: k návrhu **Prohry** (fáze 5) patří i kategorie prohry (`losingCategory`) a jedna věta důvodu
(`losingReason`); „jiná“ nikdy bez důvodu. Číselník: `references/raynet-reference.md`.

### 14. Shrň, co vzniklo

Tabulka: co bylo zapsáno nebo dokončeno (id), karta OP, karta klienta, úkol, fáze, co přeskočeno a proč, co zůstalo na uživateli.
V prostředí bez trvalého disku (chat na claude.ai) sem vypiš i řádky audit logu, jinak se ztratí.

## Příprava před schůzkou (ranní běh)

Hermes ráno, nebo pokyn „připrav dnešní schůzky":

1. `activity_list(ownerId=<krok 0>, scheduledFrom=<dnes 00:00>, scheduledTill=<dnes 23:59>)`: schůzky, telefonáty
   **i události** s klientem. U Události v náhledu doporuč převod na Schůzku ještě před schůzkou (tvrdé pravidlo 7), ať jde
   zápis po schůzce rovnou do ní.
2. U každé: karta OP (otevřené body, rozpětí bonity), poslední 2–3 aktivity, otevřené úkoly.
3. **Připoj** na konec `description` blok „PŘÍPRAVA (AI, <datum>)“ podle šablony (Doptat · Ověřit · Mít po ruce). Původní text,
   pozvánku a odkaz na Meet nech beze změny. Když blok s dnešním datem už existuje, nepřidávej ho.
4. Náhled všech příprav a jedno potvrzení na celek.
5. Na konec náhledu přidej **otevřené body checklistů** poradce s termínem dnes nebo po termínu
   (`task_list(ownerId=<krok 0>, tags="AI zápis", deadlineTill=<dnes 23:59>)`, jen body `☐`), ať je vidí ráno najednou.
   Nic se nezapisuje.

## Když něco nesedí

| Situace | Reakce |
|---|---|
| Klient nenalezen | navrhni lead; klienta fyzickou osobu zakládá člověk v UI |
| Víc kandidátů na klienta, OP nebo aktivitu k dokončení | zastav, předlož seznam, nech vybrat |
| Bankéřský hovor, část nejde přiřadit | zapiš jen jisté části, na zbytek se zeptej |
| Případ z hovoru není mezi OP klienta | nesahej po jiném OP; evidentní případ → návrh nového OP (krok 6), jinak se zeptej |
| Pocket prohodil mluvčí | oprav podle obsahu, nejisté označ `[k ověření]`; přejmenování mluvčích nech na uživateli (MCP to neumí) |
| Shrnutí Pocketu tvrdí něco jiného než přepis | platí přepis; rozdíl uveď v náhledu („Chyby Pocketu“) |
| Naplánovaná aktivita je Událost | do Události nezapisovat, větev A2 (krok 9) |
| `*_get` na známé id vrací 502 Bad Gateway | aktivita mohla být převedena (Událost → Schůzka) nebo smazána: dohledej ji přes `activity_list(companyId=…)`, id neopakuj |
| Backend vrátí chybu u id | nezkoušej jiné id naslepo, chyba vyjmenuje platná |
| `confirmToken` vypršel | zopakuj náhled, získej nový token |
| Raynet nedostupný | zastav celou dávku, nic nezapisuj napůl |

Rate limit je 24 000 requestů denně pro MCP. `rate_limit_status` se do limitu nepočítá.

## Audit log

Každou akci zapiš do logu: zápis, dokončení, přeskočení, eskalaci i zamítnutý návrh. Štítek `AI zápis` říká, *že* záznam vznikl
ze skillu; log říká, *co* se kdy změnilo a jak to vypadalo předtím. Přes MCP neexistuje undo, takže u přepisu je uložený původní
stav jediná cesta zpět.

```bash
echo '{"action": "complete_activity", "outcome": "confirmed", "entity": "meeting", "entity_id": 12345,
       "client_id": 999, "recording_id": "…", "before": {…}, "after": {…}}' | python3 scripts/audit_log.py append
```

| Pole | Hodnoty |
|---|---|
| `action` | `create_activity`, `complete_activity`, `update_activity`, `create_task`, `create_lead`, `create_business_case`, `update_business_case`, `update_company`, `draft_email`, `complete_action_item`, `skip`, `escalate` |
| `outcome` | `confirmed` · `edited` (uživatel v náhledu něco opravil) · `rejected` · `auto` · `skipped` |
| `before` | stav polí před změnou, **povinný u přepisů** (`complete_activity`, `update_*`): bez něj skript zápis odmítne |

Log je v `~/.pocket-to-raynet/audit.jsonl` (nebo `$POCKET_RAYNET_LOG`), mimo repozitář, protože obsahuje jména klientů.
`audit_log.py stats` ukáže u každého typu akce podíl návrhů potvrzených beze změny. Je to podklad, kdyby se jednou mělo
potvrzování někde zjednodušit; tvrdé pravidlo 6 tím neplatí o nic méně a rozhoduje jen uživatel.

## Reference

Načti podle potřeby:

- **`references/sablony-zapisu.md`**: šablony S / M / L, karta OP, bonita po bankách, bankéř, souhrnný úkol, příprava,
  karta klienta s mapováním „co zaznělo → vlastní pole“, pole OP na pokyn. Otevři pokaždé před psaním textu.
- **`references/raynet-reference.md`**: uživatelé, typy aktivit (Událost bez Výsledku), fáze OP, standardní pole klienta a OP,
  všechny klíče vlastních polí s přesnými hodnotami roletek a formáty, soubory a přílohy, pasti (completed, řešitel úkolu,
  Google kalendář, `addressName`, mazání prázdnou hodnotou).
- **`references/pocket-reference.md`**: tvary odpovědí Pocketu, formáty `recordingId`, limity action items.
- **`references/html-formatting.md`**: co Raynet v HTML polích uloží (tabulky a `<pre>` ne).
- **`references/email-style.md`**: jak Adam píše e-maily, včetně pravidel naučených z jeho úprav. Otevři před návrhem e-mailu.
- **`references/podklady.md`**: jaké podklady chtít podle typu případu a kde zjistit, co už přišlo.
- **`docs/NAVRH-ZAPISY.md`** (v repozitáři): rozhodnutí Adama a jejich důvody. **`docs/RAYNET-OPTIMALIZACE.md`**: doporučené
  nastavení Raynetu.

Skripty ve `scripts/` potřebují jen Python 3 se standardní knihovnou: `match_name.py` (párování jmen), `md_to_raynet_html.py`
(Markdown → HTML, redakce), `make_email_draft.py` (koncept e-mailu), `audit_log.py` (audit log).
