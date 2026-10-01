# Návrh: stručné a přesné zápisy do Raynetu

Záznam návrhu a Adamových rozhodnutí z 1. 10. 2026. Rozhodnutí jsou zapracovaná do `pocket-to-raynet/SKILL.md`
a `pocket-to-raynet/references/sablony-zapisu.md`. Platí pravidla tam; tento dokument vysvětluje, proč.

## 1. Co jsem zjistil

Skill (`pocket-to-raynet/SKILL.md`) a audit jsem porovnal se zápisy, které v Raynetu vznikly za posledních 14 dní.

| # | Zjištění | Dopad |
|---|---|---|
| 1 | **Úvodní schůzky a konzultace jsou v Raynetu `Meeting`**, naplánované předem s pozvánkou v `description`. Skill umí jen `PhoneCall`. | Zápis by vznikl jako duplicitní telefonát vedle naplánované schůzky. Skill musí umět dokončit existující schůzku (`meeting_update`, `solution`). |
| 2 | Dnešní zápisy z Pocketu mají **4 až 9 tis. znaků**, píšou se jako vyprávění a opakují se. | Přesně to, co Adam nechce. Je potřeba stanovit délku a pevnou kostru podle typu hovoru. |
| 3 | V zápisu klienta se mísí klientská fakta s **interními poznámkami**: provize, hodnocení klienta, rozhovor s kolegyní po hovoru. | Zápis je při žádosti klienta o přístup k údajům (GDPR) vydatelný. Interní věci patří jinam. |
| 4 | `description` obchodního případu už dnes slouží jako **karta případu** (stručné shrnutí). | Vhodné místo pro živý stav (nájmy, závazky, bonita), aktivita pak nese jen změnu. |
| 5 | Vlastní pole OP (banka, LTV, sazba…) jsou ve vzorku **nevyplněná**. | Skill je může navrhovat z hovoru, a tím opravit forecast ([[crm-raynet]] ve vaultu: banka chybí u 78 % pipeline). |
| 6 | **Úkoly pro tým** (Eva, Katka) už v Raynetu vznikají, skill má `owner = 2` napevno. Podle pravidla z 1. 10. ([[crm-raynet]] ve vaultu, „Práce přes MCP konektor“) jdou **drobnosti do jednoho úkolu** jako checklist, co dodá klient, patří do zápisu a follow-up e-mailu, a řešitel se mění jen přes `participants` (`resolverPerson` nefunguje). | Skill musí slučovat action items z Pocketu do jednoho úkolu na schůzku a umět předat úkol kolegovi (Eva = 13). |
| 7 | Krátké hovory do 3 minut tvoří **6 z 15** klientských nahrávek v týdnu 28.–30. 9. | Bez úrovně „mikrozápis“ buď zahltí CRM, nebo vypadnou. |
| 8 | Značka `<table>` v Raynetu **není ověřená**. | Tabulka nájmů a bonity potřebuje jeden zkušební zápis, nebo náhradní formát. |

## 2. Scénáře: kdo volá a co zapsat

Úrovně: **S** = mikrozápis do 3 řádků, **M** = standard do 12 řádků, **L** = plná šablona (cca 1 obrazovka) a aktualizace karty OP.

| # | Kdo / situace | Úroveň | Kam | Co zachytit navíc |
|---|---|---|---|---|
| 1 | Nový lead, první kontakt (kvalifikace) | S | lead nebo OP „Identifikace“ | záměr, částka, termín, zdroj (tipař), další krok |
| 2 | **Úvodní schůzka / call** | **L** | Meeting + karta OP | šablona v kap. 4: tabulka nájmů, závazky, bonita po bankách, chybí doložit |
| 3 | Strategická konzultace (portfolio, OSVČ → s.r.o., roadmapa bonity) | L | Meeting + karta OP | varianty A/B/C, rozhodnutí, plán v čase |
| 4 | Prezentace nabídky / modelací | M | aktivita k OP | varianty (banka, sazba, fixace, splátka, LTV, poplatky), co si klient vybral |
| 5 | Stav podkladů, potvrzení termínu, rychlý dotaz | S | aktivita k OP | co dorazilo, co chybí, termín |
| 6 | Průběh žádosti: scoring, odhad, schválení, podpis | S–M | aktivita k OP | změna stavu, návrh posunu fáze OP |
| 7 | Čerpání (pojistka, bezdlužnost, výpis z KN, faktury) | S | aktivita k OP | checklist podmínek čerpání ✅/⏳ |
| 8 | Servis: konec fixace, refinancování, navýšení, roční revize | M | aktivita + nový OP | nová fixace, zůstatek, cíl klienta |
| 9 | Klient odstupuje / prohra | S | aktivita + návrh fáze „Prohra“ | důvod prohry z číselníku |
| 10 | Hovor s partnerem, rodičem, spolužadatelem (dlužník je jiný) | dle obsahu | **k dlužníkovi** | kdo mluvil (`participants`) |
| 11 | Bankéř ke konkrétnímu případu | S–M | aktivita k OP | stanovisko banky: „ústně, bankéř, datum“; metodické poznatky do vaultu |
| 12 | Bankéř přes víc případů | S × N | rozdělit do jednotlivých OP | dnes se přeskakuje celý hovor |
| 13 | Odhadce | S | aktivita k OP | termín, hodnota, výhrady |
| 14 | Makléř, developer, RK | S | aktivita k OP | cena, rezervace, lhůty |
| 15 | Advokát, notář, úschova, katastr | S | aktivita k OP | podmínky a termíny pro čerpání |
| 16 | Účetní nebo daňový poradce klienta | S–M | aktivita k OP | řádky DP, termín podání, úpravy (odpisy, výdaje) |
| 17 | Tipař, partner (Monopoly Advisory, Úspěšné reality…) | S | firma partnera | nové tipy → leady |
| 18 | Kolega: předání případu, porada k případu | S | aktivita k OP | kdo převzal, stav, další krok |
| 19 | Příprava před schůzkou (bez nahrávky) | M | `description` naplánované aktivity | co chybí doptat (z karty OP) |
| 20 | Interní porada, appka, memo, osobní, lékař, Broker Trust | – | do Raynetu nic | jde do týdenního snímku Pocketu ve vaultu |

## 3. Kam co patří (aby se CRM nezahltilo)

| Místo v Raynetu | Obsah | Pravidlo |
|---|---|---|
| **Aktivita** (`solution`) | co se v hovoru **stalo nebo změnilo** | jen delta; žádné opakování karty |
| **Karta OP** (`description`) | **aktuální stav případu**: záměr, žadatelé, příjmy, nájmy, závazky, bonita, strategie | přepisuje se celá, nahoře datum „stav k“; starý stav zůstává v aktivitách |
| **Fáze OP** | posun fáze | jen návrh v náhledu, zápis po potvrzení; ostatní pole OP skill nemění (Adam 1. 10.) |
| **Karta klienta** | **maximum údajů** (Adam 1. 10.): kontakty, adresa, IČO/DIČ, DPH, zdroj, tipař, vlastní pole a Profil klienta v `notice` (domácnost, příjmy, portfolio, závazky, konce fixací, cíle) | co jistě plyne z hovoru; změny staré → nové v náhledu |
| **Úkoly** | 1 souhrnný úkol na schůzku (checklist: kdo, co, do kdy) + samostatně jen věci s vlastním termínem a řešitelem | co dodá klient, jde do zápisu a e-mailu, ne do úkolů (Adam 1. 10.) |
| **Vault** | metodika bank z hovorů, interní know-how | ne do Raynetu |

## 4. Šablona L: úvodní schůzka (první náhled)

> **Překonáno:** Raynet tabulky neuloží, platná podoba (seznam s legendou, plný rozpad bonity, rozpětí) je
> v `references/sablony-zapisu.md`. Tady zůstává první návrh, nad kterým padla rozhodnutí.
> Čísla jsou **ilustrační** a slouží jen k ukázce formátu. Pravidla bank podle vaultu k 2026-09-28
> ([[rychla-reference]], [[prijem-z-pronajmu-podle-bank]]); v ostrém zápisu by se počítala z aktuální metodiky.

**ÚVODNÍ SCHŮZKA 29. 9. 2026 · 45 min · Google Meet · Adam + Katka**

**Výsledek:** investiční byt 5,0 mil. Kč, úvěr 3,5 mil. Kč (LTV 70 %); bonitně projde u ČSOB, KB, ČS a mBank, limituje LTV. Doporučení KB přes výpisy nebo ČSOB.

**Záměr:** koupě 3. bytu k pronájmu · cena 5 000 000 · úvěr 3 500 000 · vlastní zdroje 1 500 000 (hotovost) · podpis RS do 11/2026

**Žadatel:** 38 let · zaměstnanec, čistá mzda 90 000 (průměr 12 M) · domácnost 1 osoba · KK limit 50 000

**Nájmy** (? = neznámé, doptat)

| | Byt 1 | Byt 2 |
|---|---|---|
| Nemovitost | 2+1, Praha 9, OV | 1+kk, Brno, OV |
| Vlastník / podíl | žadatel 1/1 | žadatel 1/1 |
| Nájem celkem / čistý | 18 000 / 15 000 | 14 000 / 12 000 |
| Smlouva | doba určitá do 6/2027 | doba neurčitá od 3/2026 |
| Přes účet | ano, od 2023 | ano, 7 plateb |
| V DP 2025 | ano | ne (nový nájem) |
| Nájemce spjatá osoba | ne | ? |
| Úvěr / zástava | ČSOB 3,1 mil., spl. 17 900 | KB 2,4 mil., spl. 13 600 |

DP 2025 §9: ř. 201 = 180 000 · ř. 202 = 196 000 (odpisy 90 000, úroky 98 000) · ř. 206 = −16 000

**Bonita po bankách** · předpoklady: sazba 4,79 %, 30 let, DTI 7 (investiční), závazky 31 500 + KK

| Banka | Uznaný nájem | Max. úvěr | Limituje | Poznámka |
|---|---|---|---|---|
| KB (výpisy) | 18 900 | **3,50 mil.** | LTV | DTI 3,65 mil.; přes DP by ztráta snížila příjem |
| ČSOB | 18 900 | **3,50 mil.** | LTV | add-back odpisů a úroků; rezerva splátky +2 p. b. |
| mBank | 18 900 | **3,50 mil.** | LTV | do 5 smluv ze smlouvy, DP netřeba |
| ČS (smlouvy) | 18 900 | 3,50 mil. | LTV | DP a smlouvy nejdou souběžně `[k ověření]` |
| ČS (DP) | 0 | 2,06 mil. | DTI | záporný ř. 206 = 0 |
| RB Profit | 18 900 | 2,51 mil. | DSTI 45 % | stres +2 p. b. |
| UCB | 0 | 2,06 mil. | DTI | nájem jen z DP, záporný §9 = 0 |

**Chybí doložit:** nájemní smlouva byt 2 · výpisy 3 M (nájem byt 2) · DP 2025 · potvrzení zůstatků ČSOB a KB

**Další kroky:**
- Katka: bonita v kalkulaci KB a ČSOB · do 2. 10.
- Klient: podklady výše · do 6. 10.
- Adam: nabídka 2 variant · do 9. 10.

## 4a. Tvrdá pravidla (Adam, 1. 10.)

1. **Nikdy nezapsat pod jiného klienta.** Klient je jistý, jen když sedí dva nezávislé znaky: e-mail nebo telefon + příjmení, případně
   klient a OP výslovně jmenovaný v pokynu. Náhled vždy ukáže jméno, id a e-mail klienta a název a kód OP. U dávky nesmí položka
   s nejistým klientem projít hromadným potvrzením, ptá se zvlášť.
2. **Naplánovaná aktivita z téhož dne, která proběhla později (nebo dřív), se dokončí, nový záznam nevzniká.** Upřesnění Adama
   1. 10.: **jen ve stejný den.** Aktivity naplánované na jiný den a nenaplánované zůstanou beze změny, jen se uvedou v náhledu.
   Hledá se mezi telefonáty, schůzkami i událostmi klienta (`activity_list(companyId, status=SCHEDULED)` s oknem dne hovoru).
   Dokončení: `status=COMPLETED`, skutečný začátek a konec, zápis do `solution`, `description` (příprava) zůstane. Když je kandidátů víc
   nebo téma nesedí, skill se zeptá.
3. **Při jakékoli nejistotě se skill zeptá** (klient, OP, aktivita k dokončení, posun fáze, rozdělení bankéřského hovoru).
   Raději jedna otázka navíc než zápis na špatné místo, protože přes MCP nejde nic smazat.

## 5. Otevřené otázky pro Adama

Kladu je postupně v chatu, odpovědi doplním sem.

1. ✅ **Karta OP + delta.** Popis OP = živá karta případu se stavem k datu, aktivita nese jen změnu (Adam, 1. 10.).
2. ✅ **Vždy všech 7 bank + Moneta** (ČS, ČSOB, KB, RB, UCB, mBank, Oberbank, Moneta) (Adam, 1. 10.).
3. ✅ **Pravidla z vaultu za běhu** (`rychla-reference`, `kalkulacky-bank`, tematické stránky) (Adam, 1. 10.).
4. ✅ **Tabulka nájmů: nemovitost na řádek** (Adam, 1. 10.). Test 1. 10. na telefonátu 37590 („Jan Ukazkovy (TEST)“):
   - `<table>` Raynet při uložení **odstraní** (s atributy i bez), buňky se slepí do jednoho řádku. ❌
   - `<pre>` **odstraní**, řádky se slijí. ❌
   - `<p style="font-family: monospace">` s `&nbsp;` a `<br>` **uloží** včetně stylu. Vykreslení zbývá ověřit v UI. ❓
   - `<ol>` / `<ul>` s `<b>` uloží beze změny. ✅
   - Vedlejší nález: při `phonecall_create` se `status=COMPLETED` nastaví `completed` na **čas zápisu** (18:37), ne na `scheduledTill` (18:05). Kontrola duplicit „±15 min od konce nahrávky“ proto u zápisů ze skillu musí brát `scheduledTill`, ne `completed`.
5. ✅ **Krátké hovory: mikrozápis 1–3 řádky** „Výsledek · Chybí · Další krok“ (Adam, 1. 10.).
6. ✅ **Bankéř přes víc případů: rozdělit** na mikrozápisy do OP jednotlivých klientů, metodiku do vaultu (Adam, 1. 10.).
7. ✅ **Třetí strany: zapisovat vše, co je relevantní k obchodu**, a když OP není, ke klientovi. Patří sem odhadce, makléř, developer, RK, advokát, notář, úschova, účetní a daňový poradce (Adam, 1. 10.).
7a. ✅ **Formát: C – seznam**, nemovitost na řádek, pevné pořadí údajů, legenda nad seznamem (Adam, 1. 10.).
7b. ✅ **Chybějící vstupy: rozpětí min–max** (pesimistická a optimistická varianta, např. „2,1–3,5 mil.“) (Adam, 1. 10.).
7c. ✅ **Řádek banky: plný rozpad**: uznaný příjem, max. splátka, DSTI %, DTI, LTV, sazba a stres, max. úvěr a co limituje (Adam, 1. 10.).
7d. ✅ **Follow-up e-mail: návrh v popisu souhrnného úkolu** v Raynetu, jako dnes (Adam, 1. 10.).
7e. ✅ **Úvodní schůzka: plně v obou.** Aktivita = snímek k datu schůzky (historie), karta OP = aktuální stav (Adam, 1. 10.).
7f. ✅ **Interní věci:** další postup a ladění s kolegou **patří do zápisu**. Zápis je interní a klient ho uvidí, jen když zazní „pošli klientovi XY“. Co jde, zapsat vždy i na **kartu klienta** (volitelná pole) (Adam, 1. 10.). Tím odpadá původní obava z bodu 3 kap. 1.
7f2. ✅ **Karta klienta: doplnit maximum údajů** (Adam, 1. 10.): standardní pole, vlastní pole a „Profil klienta“ v poznámce.
    Hranice: RČ a číslo účtu ne; tipař (dělení provize) jen prázdný a výslovně jmenovaný.
7g. ✅ **Změny OP: jen návrh posunu fáze** (v náhledu, zápis po potvrzení). Pole OP, plánované uzavření ani nové OP skill nemění (Adam, 1. 10.).
7h. ✅ **Spouštění:** teď testuje Adam, potom poběží přes **orchestrátor Hermes**, který budou mít všichni kolegové (Adam, 1. 10.). Skill proto nesmí mít napevno `owner = 2` ani spoléhat na nástroje jednoho klienta.
7i. ✅ **Hermes = Hermes Agent (Nous Research)**, skill ve formátu SKILL.md + MCP. **Každý kolega má vlastní instanci** (Adam, 1. 10.).
    Vlastník se zjistí za běhu: `user_info` → `username` → `person_list(email=…)` → id (ověřeno: adam.pospisil@egfin.cz → 2). Bez napevno zadaného `owner`.
7j. ✅ **Sazba pro bonitu: aktuální sazby bank z vaultu** (`sazby-a-slevy-bank`, max. 1 měsíc), stres podle metodiky banky (Adam, 1. 10.).
7k. ✅ **Nový volající: založit lead** (`lead_create`), zápis navázat na lead, konverze v UI (Adam, 1. 10.).
7l. ✅ **E-mail zůstává v popisu souhrnného úkolu** (Adam, 1. 10.). Koncept „přímo v Raynetu“ přes MCP nejde, konektor nemá žádný nástroj pro e-mail.
    Alternativa (koncept v Outlooku přes M365 `outlook_create_draft`) je ověřená zkušebním konceptem 1. 10., ale Adam ji zatím nechce.
    Pozor: schránka hlásí primární adresu `info@egfin.cz`.
7m. ✅ **Příprava před schůzkou: automaticky ráno.** Hermes doplní do dnešních naplánovaných aktivit poradce blok „Příprava: doptat · ověřit · mít po ruce“ z karty OP. Původní text pozvánky zůstane (Adam, 1. 10.).
7n. ✅ **Čas konce hovoru:** `phonecall_create(status=COMPLETED)` nastaví `completed` na čas zápisu. Následný `phonecall_update(completed=<konec>)` **bez** `status` ho opraví (ověřeno 1. 10. na 37590: 18:37 → 18:05).
7o. ✅ **Metodika pro Hermy kolegů: napojit na Evergreen app**, aby byla vždy na jednom místě (Adam, 1. 10., upřesnění k dřívější
    volbě samostatného repa). Samostatné repo se nezakládá. Vault s osobními údaji zůstává jen Adamovi. Do napojení čte skill metodiku
    z vaultu (`wiki/metodiky/`), běží tedy jen u Adama.
7p. ✅ **Štítek „AI zápis“** na všech aktivitách ze skillu (Adam, 1. 10.).
7q. ✅ **Ruční text v kartě OP se zachová** pod nadpisem „Původní poznámky“, strukturovaná karta jde nad něj (Adam, 1. 10.).
8. ~~Úkoly pro tým a pro klienta.~~ Vyřešeno pravidlem z 1. 10. (drobnosti do jednoho úkolu, klient do zápisu a e-mailu).
9. Návrh e-mailu klientovi se shrnutím.
10. Posun fáze a vyplnění polí OP.
11. Interní poznámky a provize.
12. Úroveň osobních údajů v zápisu (adresy, rodina, věk).
13. Kdo skill spouští a kdy.
