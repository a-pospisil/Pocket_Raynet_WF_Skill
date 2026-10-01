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
   tu původní (krok 5, větev A). Aktivitu naplánovanou na jiný den ani nenaplánovanou nedokončuj (Adam, 1. 10. 2026).
3. **Při nejistotě se zeptej** (klient, OP, aktivita k dokončení, rozdělení hovoru, posun fáze). Zápis přes MCP nejde smazat.
4. **Nic nemaž a nic neruš.** Zrušení schůzky v Raynetu ji smaže i v Google kalendáři.
5. **Rodná čísla a čísla účtů nikdy.** Ani v textu, ani ve vlastním poli `Rodne_cisl`.
6. **Bez potvrzení se nic nezapíše.** Nejdřív náhled, pak zápis.

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
| „zapiš hovor s Balentem" | konkrétní nahrávka, klient zadaný ručně (nejbezpečnější varianta) |
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

Pocket komolí jména (`Balint`/`Balent`, `Hasová`/`Hasolová`, `Pejro`/`Pejřil`). Zkoušej varianty, jméno z přepisu je nápověda, ne klíč.

| Výsledek | Co udělat |
|---|---|
| právě 1 zásah se dvěma shodnými znaky | pokračuj |
| víc kandidátů nebo jen jeden znak | **zastav**, vypiš kandidáty (id, jméno, e-mail, vlastník), nech vybrat |
| 0 zásahů | navrhni **lead** (`lead_create`: `topic`, `firstName`, `lastName`, `leadPerson=true`, kontakt, zdroj). Po potvrzení založ a zápis naváž na lead. Klienta (fyzickou osobu) přes MCP nezakládej. |

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

| Situace | Co udělat |
|---|---|
| 1 otevřená aktivita téhož dne, téma sedí | větev A: dokončit ji |
| víc kandidátů téhož dne nebo nejasné téma | **zeptej se**, kterou dokončit |
| žádná aktivita téhož dne | větev B: nová realizovaná aktivita |

Otevřené aktivity z **jiných dní** a nenaplánované (`NEW`) nech beze změny. Uveď je jen v náhledu jako „visí otevřené:
<typ, název, datum>“, ať je uživatel může vyřídit ručně.

### 6. Najdi obchodní případ

```
businessCase_list(companyId=<id>, status="B_ACTIVE")
```

1 otevřený OP: naváž. Víc OP: vyber podle obsahu, a když to nejde jistě, zeptej se. Žádný: zápis bez OP a zmiň to.
OP sám nezakládej.

⚠️ OP se jmenují podle banky a produktu, ne podle klienta, a případ z hovoru může být vedený na spolužadateli nebo manželce.
Když z obsahu plyne případ, který mezi OP klienta není, **zeptej se**.

### 7. Připrav obsah

`get_pocket_conversation(recording_ids=[…])` vrátí `summary.markdown` a `recordingDate` = **konec** hovoru (→ `scheduledTill`).

Text piš podle `references/sablony-zapisu.md` (S / M / L). Pocket Summary je surovina, ne výsledek: zkrať, uspořádej, ověř
proti přepisu (diarizace prohazuje mluvčí). Když potřebuješ převést hotový Markdown, použij `scripts/md_to_raynet_html.py`
(odstraní `<pocket:*>` bloky a rediguje RČ a čísla účtů).

Do textu patří i interní věci: další postup, rozdělení práce, ladění s kolegou. Zápis je interní, klient vidí jen návrh e-mailu.

**Bonita (u šablony L, a kdykoli se v hovoru mění příjmy, závazky nebo záměr).** Pro **všech 8 bank** (ČS, ČSOB, KB, RB, UCB,
mBank, Oberbank, MONETA) podle metodiky:

- Zdroj pravidel: metodika bank na jednom místě v **Evergreen app** (napojení se připravuje). Do té doby Adamův vault `wiki/metodiky/`.
  U kolegy bez přístupu k metodice skill bonitu nepočítá a napíše „bonita: chybí přístup k metodice“.
  Začni `rychla-reference.md`, postup výpočtu a vzorce v `kalkulacky-bank.md` („Postup výpočtu krok za krokem“, „Kontrolní čísla“).
  Velké stránky nečti celé: blok „⚡ Rychle“, pak `grep -n "^## "` a jen potřebná sekce.
- Sazby z `temata/sazby-a-slevy-bank.md` (nejvýš 1 měsíc staré, jinak označit), stres podle metodiky banky.
- Chybějící vstup → **rozpětí min–max** s jednou větou, co je rozdílem. Nic nedomýšlet.
- Výstup: plný rozpad u každé banky a „projde u X z 8“ (formát v šablonách). Je to orientační výpočet, ne schválení.

### 8. Ukaž náhled a nech potvrdit

```
Klient:     Peter Balent (id 599, e-mail + příjmení ✓, vlastník Adam)
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

U dávky souhrn a jedna otázka na celek, ale položka s nejistým klientem, OP nebo aktivitou se potvrzuje zvlášť.

### 9. Zapiš aktivitu

Zápisové nástroje Raynetu běží na dva kroky: první volání vrátí náhled a `confirmToken`, druhé se stejnými argumenty plus tokenem
zápis provede. Token platí 60 s a nikdy se nevymýšlí.

**Větev A: dokončení naplánované aktivity** (`phonecall_update` / `meeting_update` / `event_update` podle typu):

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

### 10. Aktualizuj kartu OP

Jen když se změnil stav případu (vždy u šablony L). `businessCase_get` → sestav kartu podle šablony → `businessCase_update(description=…)`.
Ruční text, který v popisu napsal člověk, **zachovej** pod nadpisem „Původní poznámky“. „Klíčová rozhodnutí“ jen doplňuj.
Pole OP (banka, výše, LTV…) neměň.

### 11. Doplň kartu klienta (maximum údajů)

Na kartu klienta patří **maximum toho, co z hovoru jistě plyne** a platí napříč případy. Jedno `company_update` po potvrzení:

- **standardní pole:** e-mail a telefon, adresa bydliště, IČO a DIČ (OSVČ), plátce DPH, zdroj kontaktu, tipař (`category`,
  určuje dělení provize, proto jen prázdné a výslovně jmenovaný tipař, jinak se zeptej), sociální sítě;
- **vlastní pole:** počet dětí, zaměstnavatel, pozice, nájmy v DP, čistý nájem;
- **Profil klienta v `notice`:** osoba a domácnost, vazby (spolužadatel, firma), příjmy, nemovitosti, závazky, konce fixací,
  cíle, servisní příležitosti, preferovaná komunikace. Ruční text zůstane pod „Původní poznámky“.

Před zápisem `company_get`. Prázdné doplň, existující přepiš jen jistou hodnotou a změnu „staré → nové“ ukaž v náhledu.
Nikdy RČ ani číslo účtu. Co MCP neumí (jméno a příjmení zvlášť, titul, datum narození, příznak fyzické osoby), uveď v souhrnu
jako „doplnit v UI“. Pole, klíče a šablona profilu: `references/sablony-zapisu.md`, „Karta klienta“.

### 12. Souhrnný úkol

Drobnosti z hovoru jdou do **jednoho úkolu** (checklist: kdo · co · do kdy). Samostatný úkol jen pro věc s vlastním termínem
a řešitelem, kterou je potřeba hlídat zvlášť. Co dodá klient, je v zápisu a v návrhu e-mailu, ne v úkolech.

- `task_create(title, deadline, owner=<krok 0>, company=<id>, businessCase=<id>, description=<checklist + návrh e-mailu>, tags="AI zápis")`.
- Řešitel jiný než zapisující: po založení `task_get` a přepsat osobu u druhého účastníka v `participants`
  (`resolverPerson` nefunguje). Výsledek ověř přes `task_get`.
- Návrh e-mailu klientovi patří do popisu úkolu po úvodní schůzce, po nabídce a vždy, když v hovoru zazní „pošlu vám…“.
- Action items z Pocketu (`search_pocket_actionitems`, filtr na `recordingId`) slouč do checklistu. Po zápisu je v Pocketu uzavři
  (`update_pocket_actionitem(status="COMPLETED")`; priorita se při zápisu píše velkými písmeny).

### 13. Posun fáze OP (jen návrh)

Když hovor jasně posunul případ (nabídka odeslána → „Nabídnuto“, žádost podána → „Podaná žádost + EPP 2.0“, schváleno, podepsáno),
navrhni posun v náhledu. Po potvrzení `businessCase_update(businessCasePhase=<id>)`. Id fází: `references/raynet-reference.md`.
Nic jiného na OP neměň. Výjimka: k návrhu **Prohry** (fáze 5) patří i kategorie prohry (`losingCategory`) a jedna věta důvodu
(`losingReason`); „jiná“ nikdy bez důvodu. Číselník: `references/raynet-reference.md`.

### 14. Shrň, co vzniklo

Tabulka: co bylo zapsáno nebo dokončeno (id), karta OP, karta klienta, úkol, fáze, co přeskočeno a proč, co zůstalo na uživateli.

## Příprava před schůzkou (ranní běh)

Hermes ráno, nebo pokyn „připrav dnešní schůzky":

1. `activity_list(ownerId=<krok 0>, scheduledFrom=<dnes 00:00>, scheduledTill=<dnes 23:59>)`, jen schůzky a telefonáty s klientem.
2. U každé: karta OP (otevřené body, rozpětí bonity), poslední 2–3 aktivity, otevřené úkoly.
3. **Připoj** na konec `description` blok „PŘÍPRAVA (AI, <datum>)“ podle šablony (Doptat · Ověřit · Mít po ruce). Původní text,
   pozvánku a odkaz na Meet nech beze změny. Když blok s dnešním datem už existuje, nepřidávej ho.
4. Náhled všech příprav a jedno potvrzení na celek.

## Když něco nesedí

| Situace | Reakce |
|---|---|
| Klient nenalezen | navrhni lead; klienta fyzickou osobu zakládá člověk v UI |
| Víc kandidátů na klienta, OP nebo aktivitu k dokončení | zastav, předlož seznam, nech vybrat |
| Bankéřský hovor, část nejde přiřadit | zapiš jen jisté části, na zbytek se zeptej |
| Případ z hovoru není mezi OP klienta | zeptej se, nesahej po jiném OP |
| Pocket prohodil mluvčí | oprav podle obsahu, nejisté označ `[k ověření]` |
| Backend vrátí chybu u id | nezkoušej jiné id naslepo, chyba vyjmenuje platná |
| `confirmToken` vypršel | zopakuj náhled, získej nový token |
| Raynet nedostupný | zastav celou dávku, nic nezapisuj napůl |

Rate limit je 24 000 requestů denně pro MCP. `rate_limit_status` se do limitu nepočítá.

## Reference

Načti podle potřeby:

- **`references/sablony-zapisu.md`**: šablony S / M / L, karta OP, bonita po bankách, bankéř, souhrnný úkol, příprava, vlastní pole klienta.
  Otevři pokaždé před psaním textu.
- **`references/raynet-reference.md`**: uživatelé, fáze OP, kategorie, povinná pole, vlastní pole, pasti (completed, řešitel úkolu,
  Google kalendář).
- **`references/pocket-reference.md`**: tvary odpovědí Pocketu, formáty `recordingId`, limity action items.
- **`references/html-formatting.md`**: co Raynet v HTML polích uloží (tabulky a `<pre>` ne).
- **`docs/NAVRH-ZAPISY.md`** (v repozitáři): rozhodnutí Adama a jejich důvody. **`docs/RAYNET-OPTIMALIZACE.md`**: doporučené
  nastavení Raynetu.
