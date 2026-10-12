# Šablony zápisů do Raynetu

Otevři při skládání textu zápisu, karty OP nebo souhrnného úkolu. Pravidla vychází z Adamových rozhodnutí
z 1. 10. 2026 (zdůvodnění: `docs/NAVRH-ZAPISY.md`). **Všechna jména, čísla a sazby v ukázkách jsou fiktivní**,
ukazují jen formát.

## Obsah

- [Zásady](#zásady)
- [Výběr šablony](#výběr-šablony)
- [S: mikrozápis](#s-mikrozápis)
- [M: standardní zápis](#m-standardní-zápis)
- [L: úvodní schůzka a strategická konzultace](#l-úvodní-schůzka-a-strategická-konzultace)
- [Karta OP](#karta-op)
- [Bonita po bankách](#bonita-po-bankách)
- [Bankéř přes víc případů](#bankéř-přes-víc-případů)
- [Souhrnný úkol a návrh e-mailu](#souhrnný-úkol-a-návrh-e-mailu)
- [Příprava před schůzkou](#příprava-před-schůzkou)
- [Karta klienta: maximum údajů](#karta-klienta-maximum-údajů)
- [Pole OP z hovoru (jen na pokyn)](#pole-op-z-hovoru-jen-na-pokyn)

## Zásady

- **Stručně a strukturovaně.** Žádné vyprávění („Adam vysvětlil, že…“), žádné opakování. Fakt, číslo, rozhodnutí, kdo, do kdy.
- **Aktivita = co se v hovoru stalo nebo změnilo.** Aktuální stav případu patří do karty OP. Výjimka: úvodní schůzka
  a strategická konzultace mají plný obsah v aktivitě i v kartě OP (aktivita = snímek k datu, karta = aktuální stav).
- **Interní věci patří do zápisu.** Ladění postupu s kolegou, rozdělení práce, rizika: zápis je interní a klient ho nevidí.
  Ven jde jen text, u kterého v hovoru zaznělo „pošli klientovi…“, a to přes návrh e-mailu v souhrnném úkolu.
- **Jen HTML, které Raynet uloží.** `<p>`, `<b>`, `<i>`, `<br>`, `<ul>`, `<ol>`, `<li>`, `<a>`. **Tabulky (`<table>`) ani
  `<pre>` nepoužívat**, Raynet je při uložení odstraní a obsah slepí (ověřeno 1. 10. 2026, telefonát 37590). Tabulková data
  se píšou jako seznam s legendou: tučná legenda pořadí údajů, pod ní `<ol>`, jedna položka = jeden řádek, údaje oddělené ` · `.
- **Čísla po česku:** `3 500 000`, `4,79 %`, `3,5 mil.`; částky v Kč bez „Kč“, pokud je to z kontextu jasné.
- **Neznámé = `?`** a položka v seznamu „Doptat“. Nic nedomýšlet. Nejisté z přepisu (prohozené role, zkomolené číslo) = `[k ověření]`.
- **Rodná čísla a čísla účtů v textu nikdy.** Převodní skript je rediguje, při ručním psaní taky. Do polí karty klienta jen z dokumentu.
- **Kdo co řekl a udělal, ověř v přepisu.** Shrnutí Pocketu přisuzuje Adamovy plány a sliby klientovi (cesta do Keni 1. 10. 2026)
  a plete jména (osoba ze shrnutí, která v přepisu nezazní, do zápisu nepatří).
- **Žádné rady k fakturaci.** Jak má fakturace vypadat, komu fakturovat: nepsat. Jen to, co o své fakturaci řekl klient sám.
- **Účastníci:** když klienta vlastní jiný poradce než ten, kdo zapisuje, přidej ho do `participants`, ať zápis vidí.
- **Stopa na konci** každé aktivity: `<p><i>AI zápis · Pocket &lt;recordingId&gt;</i></p>`. K tomu štítek `AI zápis`.

## Výběr šablony

| Situace | Šablona | Kam |
|---|---|---|
| hovor do ~3 min, stav podkladů, potvrzení termínu, rychlý dotaz | **S** | aktivita k OP |
| follow-up, nabídka, průběh žádosti, čerpání, servis | **M** | aktivita k OP |
| třetí strana k případu (odhadce, makléř, developer, RK, advokát, notář, úschova, účetní, daňový poradce) | **S/M** podle obsahu | aktivita k OP klienta, bez OP ke klientovi |
| kolega: předání případu, porada k případu | **S/M** | aktivita k OP |
| úvodní schůzka, strategická konzultace, roadmapa bonity | **L** + karta OP | aktivita k OP + popis OP |
| bankéř přes víc případů | **S** × počet případů | do OP každého klienta zvlášť |
| nový zájemce, který není v CRM | **S** | nový lead (`lead_create`) |

## S: mikrozápis

Max. 3 řádky. Název aktivity: `<téma> – <výsledek>`, např. `Podklady – chybí DP 2025`.

```html
<p><b>Výsledek:</b> klient dodá DP 2025 a výpisy za 3 měsíce, ostatní podklady jsou kompletní.</p>
<p><b>Chybí:</b> DP 2025 · výpisy 7–9/2026</p>
<p><b>Další krok:</b> Katka zkontroluje podklady do 6. 10.</p>
<p><i>AI zápis · Pocket 36d473d6-…</i></p>
```

Chybí-li něco nebo není další krok, řádek vynech.

## M: standardní zápis

Max. ~12 řádků.

```html
<p><b>Výsledek:</b> jedna věta, co se rozhodlo nebo změnilo.</p>
<p><b>Co zaznělo</b></p>
<ul>
<li>fakt s číslem (kdo řekl, pokud na tom záleží)</li>
<li>…</li>
</ul>
<p><b>Rozhodnutí:</b> … (jen pokud padlo)</p>
<p><b>Chybí / doptat:</b> … · …</p>
<p><b>Další kroky:</b></p>
<ul>
<li>Adam: … · do 9. 10.</li>
<li>Eva: … · do 14. 10.</li>
<li>Klient: … · do 6. 10.</li>
</ul>
<p><i>AI zápis · Pocket …</i></p>
```

Třetí strana: na začátek `<p><b>Kdo:</b> odhadce (jméno, firma) · telefonicky</p>`. Stanovisko banky vždy jako
„stanovisko <banka> (<bankéř>, ústně, <datum>)“, protože ústní vyjádření není schválení.

## L: úvodní schůzka a strategická konzultace

Název aktivity: ponechat název naplánované schůzky. Když se zakládá nová, pak `Úvodní schůzka – <záměr v pár slovech>`.

Pořadí bloků (prázdný blok vynech):

1. **Hlavička:** `<p><b>ÚVODNÍ SCHŮZKA 29. 9. 2026 · 45 min · Google Meet · Adam + Katka</b></p>`
2. **Výsledek:** 1–2 věty: co klient chce, jestli to bonitně projde, doporučená banka, co dál.
3. **Záměr:** účel · cena · požadovaný úvěr · vlastní zdroje (odkud) · nemovitost (typ, lokalita, OV / družstvo) · zástava · termín.
4. **Žadatelé:** pro každého věk · typ příjmu a výše (čistá, průměr za období) · domácnost (vyživované osoby) · občanství nebo pobyt, jen pokud hraje roli.
5. **Příjmy** (kromě nájmů): seznam s legendou `zdroj · výše měsíčně · doložení · poznámka`.
6. **Nájmy:**

   ```html
   <p><b>Nájmy</b> <i>(nemovitost · podíl · nájem / čistý · smlouva · přes účet · DP · úvěr / splátka)</i></p>
   <ol>
   <li><b>2+1 Praha 9, OV</b> · 1/1 · 18 000 / 15 000 · DU do 6/2027 · ano od 2023 · DP 2025 ano · ČSOB 3,1 mil. / 17 900</li>
   <li><b>1+kk Brno, OV</b> · 1/1 · 14 000 / 12 000 · DN od 3/2026 · 7 plateb · ne · KB 2,4 mil. / 13 600</li>
   </ol>
   <p>DP 2025 §9: ř. 201 = 180 000 · ř. 202 = 196 000 (odpisy 90 000, úroky 98 000) · ř. 206 = −16 000</p>
   ```

   Údaje k vytěžení pro každou nemovitost (co chybí, je `?` a jde do „Doptat“): typ a lokalita (čtvrť + město) · OV / družstvo ·
   vlastník a podíl na LV · nájem včetně služeb / čistý · smlouva na dobu určitou do / neurčitou od · nájem chodí přes účet (od kdy,
   kolik plateb) · v DP (rok, řádky §9) · nájemce je spjatá osoba (ano/ne) · krátkodobý pronájem (ano/ne) · úvěr (banka, zůstatek,
   splátka, konec fixace) · zástava pro jiný úvěr · odhadní hodnota.
7. **Závazky:** seznam `banka · typ · zůstatek · splátka · konec fixace / splatnost · zajištění`, plus limity KK a KTK.
8. **Bonita po bankách:** viz [Bonita po bankách](#bonita-po-bankách).
9. **Doporučení a strategie:** 2–5 odrážek (banka, struktura, pořadí kroků, varianty A/B).
10. **Chybí doložit / doptat:** jeden řádek oddělený ` · `.
11. **Další kroky:** kdo · co · do kdy.
12. **Interní:** ladění s kolegou, rozdělení práce, rizika (volitelné).
13. Stopa.

## Karta OP

`description` obchodního případu = živý stav. Při každé změně se přepíše celá, ale **ruční text kolegy zůstává**: skill ho
přesune pod nadpis „Původní poznámky“ a nikdy ho nemaže. Před zápisem vždy `businessCase_get` a porovnání.

```html
<p><b>STAV K 1. 10. 2026</b> <i>(AI zápis, poslední změna: aktivita 37512)</i></p>
<p><b>Záměr:</b> …</p>
<p><b>Žadatelé:</b> …</p>
<p><b>Příjmy:</b> …</p>
<p><b>Nájmy</b> <i>(legenda)</i></p>
<ol>…</ol>
<p><b>Závazky</b> <i>(legenda)</i></p>
<ol>…</ol>
<p><b>Bonita k 1. 10. 2026</b> <i>(předpoklady)</i></p>
<ul>…</ul>
<p><b>Strategie:</b> …</p>
<p><b>Otevřené body / doptat:</b> …</p>
<p><b>Klíčová rozhodnutí:</b></p>
<ul>
<li>29. 9.: nákup přes FO, ne s.r.o. (Adam)</li>
</ul>
<p><b>Původní poznámky</b></p>
<p>… ruční text beze změny …</p>
```

„Klíčová rozhodnutí“ se jen doplňují (nejnovější dole), nic se z nich nemaže.

## Bonita po bankách

Počítá se **vždy pro všech 8 bank**: ČS, ČSOB, KB, RB, UCB, mBank, Oberbank, MONETA. Pravidla bere z metodiky
(`rychla-reference`, `kalkulacky-bank`, tematické stránky; viz `SKILL.md`, krok „Bonita“). Sazby z `sazby-a-slevy-bank`
(nejvýš 1 měsíc staré, starší označit `[sazba k <datum>]`), stres podle metodiky banky.

**Výjimka: podnikatelské úvěry** (MONETA SBL, úvěr pro s.r.o., Živnohypo). Bonita po 8 bankách se nepočítá. Místo ní jeden
řádek s parametry produktu a s tím, co banka započte:

```html
<p><b>Parametry:</b> SBL Mini · obrat min. 500 000 (peněžní deník) · LTV 65 % · limit 20 mil. · banka započte celý úvěr spoludlužníka · nájmy z DPFO</p>
```

Hlavička s předpoklady, pak jedna odrážka na banku, seřazeno od nejvyššího max. úvěru:

```html
<p><b>Bonita po bankách</b> <i>(příjem · max. splátka při DSTI · DTI strop · LTV strop · sazba / stres → max. úvěr, limit)</i><br>
Předpoklady: 30 let · závazky 31 500 · KK 50 000 · domácnost 1 · stávající dluh 5,5 mil. · zástava 5,0 mil.</p>
<ul>
<li><b>KB 3,50 mil. (LTV)</b> · 108 900 (mzda 90 000 + nájem 18 900 z výpisů) · 20 450 při DSTI 50 % · DTI 7: 3,65 mil. · LTV 70 %: 3,50 mil. · 4,49 % / bez stresu</li>
<li><b>RB Profit 2,51 mil. (DSTI)</b> · 108 900 · 16 355 při DSTI 45 % · DTI 7: 3,65 mil. · LTV 70 %: 3,50 mil. · 4,79 % / +2 p. b.</li>
<li><b>ČS 2,06–3,50 mil. (DTI / LTV)</b> · 90 000–108 900 · … <i>pesim.: nájem z DP = 0 (záporný ř. 206); optim.: nájem ze smluv</i></li>
</ul>
<p><b>Nejlépe:</b> KB a ČSOB 3,50 mil. (limit LTV) · <b>požadováno</b> 3,50 mil. → projde u 4 z 8</p>
```

- **Chybějící vstup → rozpětí min–max.** Pesimistická a optimistická varianta s jednou větou, co je rozdílem. Nevymýšlet střed.
- **Plný rozpad u každé banky:** uznaný příjem (z čeho), max. splátka a DSTI, strop DTI, strop LTV, sazba a stres, výsledek a co limituje.
- **Požadovaná částka:** je-li známá, na konec „projde u X z 8“ a u neprocházejících banky o kolik chybí.
- Banky, které případ principiálně nevezmou (budoucí nájem u ČSOB, UCB, mBank a MONETA; bytový dům u mBank…), mají místo čísla
  `0 – <důvod>`. Řádek zůstává, ať je vidět proč.
- **Nikdy jako schválení.** Je to orientační výpočet podle metodiky k datu, ne stanovisko banky.

## Bankéř přes víc případů

Hovor se rozdělí podle klientů. Ke každému klientovi, kterého skill jistě spáruje, vznikne mikrozápis do jeho OP:

```html
<p><b>Stanovisko KB</b> (bankéř Novák, ústně, 30. 9. 2026): nájem z výpisů uzná i při záporném §9, potřebuje 3 výpisy.</p>
<p><b>Další krok:</b> Eva pošle výpisy do 3. 10.</p>
<p><i>AI zápis · Pocket … (část hovoru 03:10–07:45)</i></p>
```

Obecné poznatky o metodice (neváží se ke klientovi) do Raynetu nepatří, jdou do týdenního snímku Pocketu ve vaultu.
Část hovoru, kterou nejde jistě přiřadit, se nezapisuje: skill se na ni zeptá.

## Souhrnný úkol a návrh e-mailu

Drobnosti po schůzce jdou do **jednoho úkolu** (pravidlo z 1. 10. 2026, vault `crm-raynet` „Práce přes MCP konektor“). Samostatný
úkol má jen věc s vlastním termínem a řešitelem, kterou je potřeba hlídat zvlášť (nabídka před další schůzkou, kontrola za několik
měsíců). Co dodá klient, patří do zápisu a do návrhu e-mailu, ne do úkolů.

- Název: `<klient> – další kroky po schůzce <datum>`, termín = nejbližší termín z checklistu, řešitel = vlastník OP.
- Popis:

```html
<p><b>Checklist</b></p>
<ul>
<li>☐ Adam: potvrdit odhadce · dnes</li>
<li>☐ Eva: bonita v kalkulaci KB a ČSOB · do 2. 10.</li>
</ul>
<p><b>Návrh e-mailu klientovi</b> <i>(odeslat z Raynetu)</i></p>
<p>Dobrý den, …</p>
```

Návrh e-mailu se přidává po úvodní schůzce, po prezentaci nabídky a vždy, když v hovoru zazní „pošlu vám shrnutí / seznam podkladů“.
E-mail je pro klienta: bez interních poznámek, bez provizí, bez bonity po bankách (jen závěr), s tím, co potřebujeme a do kdy.

## Příprava před schůzkou

Ranní běh: pro dnešní naplánované schůzky a telefonáty poradce **připojí** na konec `description` blok (nic nepřepíše):

```html
<p><b>PŘÍPRAVA (AI, 2. 10. 2026)</b></p>
<p><b>Doptat:</b> čistý nájem byt 2 · spjatá osoba nájemce · zůstatek KB</p>
<p><b>Ověřit:</b> DP 2025 podáno? · konec fixace ČSOB</p>
<p><b>Mít po ruce:</b> bonita 2,1–3,5 mil. (ČS DP vs. smlouvy) · nabídka KB z 30. 9.</p>
```

Zdroj: karta OP (otevřené body, rozpětí bonity) a poslední aktivity. Když už blok s dnešním datem v popisu je, nepřidává se znovu.

## Karta klienta: maximum údajů

Adam, 1. 10. 2026: **na kartu klienta doplnit maximum údajů.** Karta klienta drží to, co platí napříč případy a přežije uzavření OP
(kontakty, domácnost, příjmy, portfolio, úvěry a konce fixací pro servis). Karta OP drží konkrétní případ.

Postup: `company_get` → porovnat s tím, co jistě plyne z hovoru → v náhledu ukázat **prázdné → nové** a **staré → nové** →
po potvrzení jedno `company_update`. U každého pole uveď i **odkud** (krátká citace nebo čas v přepisu, u dokumentu jeho
název), ať jde hodnota rychle ověřit. Prázdné pole se doplní. Existující hodnotu přepiš, jen když je nová jistá, a změnu ukaž
v náhledu. Nejisté (zkomolené číslo, prohozený mluvčí) nezapisuj a dej do „Doptat“.

### Standardní pole (`company_update`)

| Pole | Co | Pozn. |
|---|---|---|
| `email`, `email2`, `phone` | kontakty (`phone` = Tel 1) | Jiný e-mail než stávající → `email2`, nikdy nepřepsat primární bez potvrzení. Vždy s `addressName` (níže). |
| `street`, `city`, `zipCode`, `province`, `country` | adresa bydliště | Jen adresa, kterou klient uvedl jako svou, ne adresa nemovitosti. `country` jako ISO kód (CZ). |
| `addressName` | název adresy | **Povinný, jakmile posíláš jakékoli adresní nebo kontaktní pole**, jinak update neprojde. Stávající hodnotu z `company_get` zachovej, u prázdné „Sídlo klienta“. |
| `regNumber`, `taxNumber`, `taxPayer` | IČO a DIČ (OSVČ), plátce DPH (`YES`/`NO`) | U klienta s s.r.o. patří IČO firmy k firmě, ne k osobě. |
| `contactSource` | odkud klient přišel | 156 doporučení tipaře · 82 vlastní kontakt · 81 doporučení (netipař) · 79 web/poptávka · 179 sociální sítě · 196 workshop |
| `category` | **tipař** | Číselník jmen tipařů (176 Bez tipaře, 205 Monopoly Advisory, 180 Úspěšné reality…; `raynet://codelist/companyCategory`). **Určuje dělení provize** → měnit jen prázdné, a když se tipař v hovoru výslovně jmenuje; jinak se zeptej. |
| `linkedin` a další sítě | jen když zazní | |
| `notice` | **Profil klienta** (níže) | |

Nemění se: `rating`, `state` (mění Raynet při výhře), `owner`, `name`, `companyClassification1` (VIP, tipař, bankéř… patří
partnerům, ne klientům). **`bankAccount` jen z dokumentu** (výpis, smlouva), nikdy z hovoru. MCP neumí jméno a příjmení zvlášť, titul, datum narození ani příznak fyzické
osoby: věk nebo rok narození patří do profilu, ostatní skill uvede v souhrnu „doplnit v UI“.

### Vlastní pole (`customFields`)

Co z hovoru jistě plyne, jde i do vlastních polí. Klíče, typy a přesné hodnoty roletek: `raynet-reference.md`, „Vlastní pole“.
Do `customFields` posílej **jen klíče, které měníš** (`null` nebo prázdná hodnota pole smaže). Roletky jen přesným textem.

| Co zazní v hovoru | Klíč | Zápis |
|---|---|---|
| vzdělání | `vzdelani_b79fe` | roletka, např. `vysokoškolské` |
| rodinný stav | `rodinny_st_adceb` | roletka, např. `ženatý / vdaná` |
| zúžené SJM | `Zuzeni_SJ_f0b36` | `Ano` / `Ne` |
| počet vyživovaných dětí | `Pocet_deti_cf874` | číslo |
| banka hlavního účtu | `hlavni_bez_5fef9` | `ČSOB` · `KB` · `ČS` · `RB` · `Fio` · `Airbank` · `mBank` |
| čistý měsíční příjem ze zaměstnání | `mesicni_pr_0a298` | číslo, např. `65000` |
| zaměstnavatel · pozice | `zamestnava_ffa65` · `pracovni_p_f7e4d` | text |
| nástup k zaměstnavateli | `nastup_fbbb1` | datum `"2019-03-01"` |
| druh pracovního poměru | `Druh_fcd16` | `HPP` · `DPČ` · `DPP` |
| náklady na bydlení · výdaje domácnosti (měsíčně) | `DruhBankaJ_57559` · `DruhBankaJ_f41e1` | text |
| stávající úvěry | `DruhBankaJ_a886e`, `_4de8f`, `_6314d`, `_8f94a`, `_cae7c` (řádky 1–5) | text, jeden úvěr na řádek: `druh / banka / jistina / úrok % / splátka / měsíců / fixace / KF`; neznámý údaj `?` |
| nájmy v daňovém přiznání | `Najmy_v_DP_bb662` | `true` / `false` |
| současný čistý nájem celkem za měsíc | `Soucasny_c_952ff` | **text** `"27000"` |
| čistý nájem po koupi | `Budouci_5f2ff` | **text** `"39000"` |
| od kdy podniká · obor | `Pocatek_po_ab1d0` · `Druh_cinno_d75a7` | datum · text |
| svobodné povolání | `Svobodne_p_705f3` | roletka (lékař, advokát, IT…) |
| výdajový paušál | `Vyse_pausa_4549e` | `Bez paušálu` · `80 %` · `60 %` · `40 %` |
| režim paušální daně | `Zadatel_v__a594e` | `true` / `false` |

Řádky úvěrů plň shora a přepiš jen ty, které se v hovoru týkají stejného úvěru; řádek CELKEM (`DruhBankaJ_4c59a`) jen když
jsou známé všechny úvěry. Stejné údaje patří i do Profilu klienta (Ostatní závazky, Nemovitosti), pole jsou pro rychlý přehled.

**Nikdy z hovoru:** `Rodne_cisl_ed0da` (RČ), `cislo_OP_d2c59`, `OP_vydal_abab5`, `platnost_O_5ac2f`, `rodne_prij_1de2b`,
`statni_pri_8265e` a `bankAccount`. Jen z dokumentu (DP, doklad, výpis, smlouva) a v náhledu se zdrojem (tvrdé pravidlo 5).
**Jen z výpočtu BT kredit, nikdy odhad:** `Radek_101__b1dea` (ČS), `Radek_102__56301` (ČSOB HB), `Radek_37_z_d1a4d` (RB),
`Radek_74_z_a6a87` (KB), `mBank_9af71`, `VysledekCS_a6436`, `Alternativ_b3c97`. **Nevyplňovat:** `Doplnujici_a57c0`
(profil je v `notice`), `Bety_8f936` (význam neznámý). **Pole typu soubor** (DPFO, DPPO, výkazy, rozvahy, Přehled úvěrů) jen čti:
říkají, co už v CRM je (`podklady.md`); nahrává je člověk v UI.

### Profil klienta (`notice`)

HTML, přepisuje se celý jako karta OP. Ruční text zůstává pod nadpisem „Původní poznámky“ (např. „Fyzická osoba – přepnout typ
v Raynetu“).

```html
<p><b>PROFIL KLIENTA K 1. 10. 2026</b> <i>(AI zápis, zdroj: aktivita 37512)</i></p>
<p><b>Osoba:</b> 38 let (nar. 1988) · ženatý · 2 děti (4, 7) · Praha · občan ČR</p>
<p><b>Vazby:</b> manželka = klientka id 1234 (spolužadatelka) · firma XY s.r.o. (IČO …, 100 %)</p>
<p><b>Příjmy:</b> zaměstnanec, Firma a.s., analytik, HPP od 2019, čistá 90 000 · OSVČ IČO …, CZ-NACE 62, paušál 60 %, neplátce DPH</p>
<p><b>Nemovitosti</b> <i>(nemovitost · podíl · nájem čistý · úvěr · konec fixace)</i></p>
<ol>
<li><b>2+1 Praha 9, OV</b> · 1/1 · 15 000 · ČSOB 3,1 mil. / 17 900 · fixace do 6/2028</li>
<li><b>1+kk Brno, OV</b> · 1/1 · 12 000 · KB 2,4 mil. / 13 600 · fixace do 3/2031</li>
</ol>
<p><b>Ostatní závazky:</b> KK limit 50 000 (ČS) · leasing auto 6 500 do 2027</p>
<p><b>Cíle:</b> portfolio 5 bytů do 2030, cash flow > 0 na byt · preferuje FO, s.r.o. zvažuje</p>
<p><b>Servis:</b> konec fixace ČSOB 6/2028 → refinancování (ozvat se 3 měs. předem)</p>
<p><b>Komunikace:</b> preferuje e-mail, hovory po 17:00</p>
<p><b>Původní poznámky</b></p>
<p>… ruční text beze změny …</p>
```

Prázdný řádek vynech. Údaje o případu (záměr, bonita, strategie konkrétního úvěru) sem nepatří, jsou v kartě OP.

## Pole OP z hovoru (jen na pokyn)

Ve výchozím běhu skill pole OP nemění, jen navrhne posun fáze (Adam, 1. 10. 2026). Tato tabulka platí, když uživatel výslovně
řekne „doplň i pole OP“, a pro **nový OP** (výjimka v kroku 6), kde se při založení vyplní to, co jistě zaznělo.

| Co zazní | Pole | Zápis |
|---|---|---|
| účel a typ úvěru | `category` + `Ucel_uveru_47dd5` | 116 hypotéka · 184 podnikatelský · 169 ze stavebního spoření · 189 spotřebitelský; účel roletkou (`koupě`, `refinancování`, `rekonstrukce`…) |
| požadovaná výše | `totalAmount` + `vyse_uveru_ad8b6` | číslo, obě pole stejně |
| hodnota nemovitosti nebo zástavy | `Hodnota_za_21c14` | číslo |
| banka | `producent_6ef95` | celé obchodní jméno z roletky (`ČSOB Hypoteční banka, a.s.`); banka mimo seznam → jen do karty OP a zeptat se |
| sazba · splatnost | `urokova_sa_51229` · `Splatnost_7586b` | číslo (`4.79`) · měsíce (`360`, ne roky) |
| fixace · začátek a konec fixace | `Doba_fixac_172ca` · `platnost_f_e63c5` · `konec_fixa_65281` | roletka slovně (`5 let`) · datum · datum |
| výše splátky | `vyse_splat_fff50` | číslo |
| pojištění k úvěru | `Pojisteni_1b7ae` | `ANO` · `NE` · `ČSOB - Náš život` |
| LTV | `LTV_eedee` | jen spočítané z řečených čísel: výše ÷ hodnota zástavy × 100, vzorec v náhledu |
| datum představení nabídky | `Predstaven_47ad0` | datum (plní ho i workflow při fázi Nabídnuto, nepřepisovat) |
| datum podpisu žádosti · vyjádření banky | `Datum_podp_02aa4` · `Vyjadreni__d8106` | datum |
| typ provize | `Provize_dc7d2` | `Jednorázová` · `Postupná` · `Mimo BT (podnikatelský úvěr)` |
| doporučení od tipaře | `source` | 156 |
| očekávané dokončení | `scheduledEnd` | `yyyy-MM-dd` |
| číslo smlouvy | `cislo_smlo_60eb1` | jen z dokumentu nebo e-mailu banky, z hovoru ne (čísla se komolí) |

Fáze (`businessCasePhase`) jde vždy jen jako návrh (krok 13). Shrnutí, varianty a rozhodnutí patří do karty OP (`description`).
V náhledu ukaž **prázdné → nové** a **staré → nové**, přepis existující hodnoty jen s potvrzením. Před zápisem ověř, že OP patří
správnému klientovi (`company` = id klienta). Po zápisu `businessCase_get` a kontrola, že pole sedí.
