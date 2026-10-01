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
- [Karta klienta: vlastní pole](#karta-klienta-vlastní-pole)

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
- **Rodná čísla a čísla účtů nikdy.** Převodní skript je rediguje, při ručním psaní taky.
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

## Karta klienta: vlastní pole

Co z hovoru jistě plyne, se zapíše i do vlastních polí klienta (`company_update`, `customFields`). Klíče z průzkumu instance
k 2026-10-01 (definice nejsou přes MCP čitelné, viz `raynet-reference.md`):

| Klíč | Obsah | Typ |
|---|---|---|
| `Pocet_deti_cf874` | počet dětí (vyživovaných) | celé číslo |
| `zamestnava_ffa65` | zaměstnavatel | text |
| `pracovni_p_f7e4d` | pracovní pozice | text |
| `Najmy_v_DP_bb662` | nájmy v daňovém přiznání | ano/ne |
| `Soucasny_c_952ff` | současný čistý nájem celkem | **text** (číslo jako řetězec) |

`Rodne_cisl_ed0da` (rodné číslo) skill **nevyplňuje** (přepisy čísla komolí a skript RČ rediguje). Pole OP (banka, výše úvěru,
účel, LTV…) skill nemění, navrhuje jen posun fáze.
