# Jak Adam píše e-maily

Otevři před sestavením jakéhokoli návrhu e-mailu.

Vychází ze skutečných e-mailů Adama Pospíšila klientům, uložených v Raynetu
(vlákno z 18. a 20. 9. 2026), a z analýzy 444 jeho e-mailů za 05–10/2026 s jeho
rozhodnutími z 29. 10. 2026. Převzatá je stavba a formulace, ne obsah.

Sjednoceno s vaultem (29. 10. 2026): stejná pravidla jsou na stránkách
`wiki/profil/styl-komunikace.md` a `wiki/profil/komunikacni-vzory.md` v repozitáři
`a-pospisil/vault`. Když se změní jedno, uprav i druhé.

## Obsah

- [Stavba](#stavba)
- [Formulace, které používá](#formulace-které-používá)
- [Pravopis a čísla](#pravopis-a-čísla)
- [Tykání a vykání](#tykání-a-vykání)
- [Rozhodnutí Adama (29. 10. 2026)](#rozhodnutí-adama-29-10-2026)
- [Naučená pravidla](#naučená-pravidla)

## Stavba

Typický e-mail po hovoru se seznamem podkladů má tuhle kostru:

```
Dobrý den, pane <příjmení v 5. pádě>,

navazuji na náš dnešní hovor. Abych Vám mohl přesně spočítat, na jakou výši
úvěru se dostaneme, poprosím Vás o následující podklady:

<Nadpis skupiny>
- položka
- položka

<Nadpis skupiny>
- položka

Pro rekapitulaci varianty, o kterých jsme mluvili:
- <Varianta>: <parametry — splatnost, sazba, LTV, poplatky>
- <Varianta>: …

Do kopie uvádím i kolegu, pro rychlejší řešení prosím o „odpovědět všem".
Po dodání podkladů vše přepočítáme a ozvu se s konkrétním návrhem.

Děkuji a přeji hezký den
```

**Podpis** je vždy celý blok z `assets/signature.txt` (Bc. / Jednatel / Evergreen finance + kontakty;
titul Bc. platí). Pošta ho sama nevkládá, takže ho do návrhu vždy přidá agent:
- koncept `.eml` přes `scripts/make_email_draft.py`: připojí ho skript, do těla ho nepiš;
- e-mail do chatu nebo karta k odeslání: napiš celý blok pod rozloučení sám;
- interní e-mail kolegovi: jen „Díky, Adam“ bez bloku (`--no-signature`).

**Podklady seskupuj podle toho, k čemu slouží**, ne v jednom dlouhém seznamu.
Skupiny, které se opakují: *Příjmy fyzické osoby*, *Stávající hypotéka*,
*Finanční výkazy – <název firmy>*, *Nemovitost do zástavy*.

**Rekapitulace variant** je samostatný blok na konci. U každé varianty konkrétní
parametry, ne obecný popis — klient si z e-mailu má umět vybrat bez dalšího hovoru.

**Odpověď na zprávu klienta** je kratší: poděkování, jedna věcná otázka nebo
doplnění, co ještě chybí, a co bude následovat.

```
Dobrý den, pane <příjmení>,

děkuji za zprávu, <věcná otázka nebo upřesnění>.

Dále prosím o zaslání zbývajících podkladů z předchozího e-mailu, a to:
<skupina>
- položka

Následně dáme dohromady Vaši bonitu a zašleme finální nabídku.

Děkuji a přeji hezký den
```

## Formulace, které používá

| Účel | Formulace |
|---|---|
| Navázání | „navazuji na náš dnešní hovor" |
| Žádost | „poprosím Vás o následující podklady", „prosím o zaslání" |
| Proč to potřebuje | „Abych Vám mohl přesně spočítat, na jakou výši úvěru se dostaneme, …" |
| Shrnutí | „Pro rekapitulaci varianty, o kterých jsme mluvili:" |
| Kopie kolegy | „Do kopie uvádím i kolegu, pro rychlejší řešení prosím o „odpovědět všem"." |
| Další krok | „Po dodání podkladů vše přepočítáme a ozvu se s konkrétním návrhem." |
| Rozloučení | „Děkuji a přeji hezký den" (vykání), „Díky a měj se" (tykaný klient), „Díky, Adam" (kolega). „S pozdravem" ne: v e-mailech ho Adam skoro nepoužívá. |

Tón je věcný a stručný. Žádné „Doufám, že se máte dobře", žádné zdvořilostní
vatování. Každá věta buď něco žádá, nebo něco vysvětluje. Omluva jen za pozdní
reakci (viz Rozhodnutí níže), jinak ne.

## Pravopis a čísla

- **Vykání s velkým V** v osobních zájmenech: *Vám, Vás, Vaši, Vaše*.
- **České uvozovky**: „…", ne "…".
- **Procenta s mezerou**: *6,2 %*, *LTV 75 %*.
- **Desetinná čárka**: *6,5–6,8 %*.
- **Částky**: *do 20 mil. Kč*, *1,5 % z výše úvěru*, *cca 5,5 mil.*
- **Rozsahy pomlčkou bez mezer**: *6,5–6,8 %*, *12–13 mil. Kč*.

## Tykání a vykání

**Striktní pravidlo (Adam, 12. 10. 2026):** u každého příjemce hlídej, jestli mu pisatel tyká, nebo vyká, a podle toho
piš celou zprávu. Platí pro návrh e-mailu, e-mail do chatu, koncept `.eml`, SMS a WhatsApp. Zápisy do Raynetu jsou
ve 3. osobě a pravidlo se jich netýká. Omylem tykat klientovi je chyba, kterou nejde vzít zpět.

### Tři registry

| Registr | Oslovení | Tvary | Rozloučení |
|---|---|---|---|
| **V1 vykání + příjmení** (výchozí u klientů) | „Dobrý den, pane Nováku,“ / „Dobrý den, paní Nováková,“ | Vy, Vás, Vám, Váš **s velkým V**; máte, pošlete, dejte vědět | „Děkuji a přeji hezký den“ + celý podpis |
| **V2 vykání + křestní jméno** (bližší klienti) | „Dobrý den, Petře,“ | stejné jako V1, velké V | stejné jako V1 |
| **T tykání** (známí, kolegové, partneři, část bankéřů) | „Ahoj Petře,“ | Ty, Ti, Tě, Tebe, Tobě, Tvůj, Tvoje **s velkým T** (Adam, 12. 10. 2026); máš, pošli, dej vědět | klient: „Díky a měj se“ + celý podpis (Adam, 29. 10. 2026); kolega: „Díky, Adam“ bez bloku |

Jméno v oslovení je vždy v 5. pádě (Petře, Honzo, pane Nováku, paní Nováková). Tvar jména ověř v Raynetu, ne v Pocketu.

### Jak registr určit (v tomto pořadí)

Posuzuje se vztah **pisatele** (poradce z kroku 0, který zprávu podepíše) a příjemce. Když píše kolega, rozhoduje jeho vztah,
ne Adamův. **Tykání je vzájemné** (Adam, 12. 10. 2026: „pokud mi klient tyká, já jemu také tykám“): T platí, když tyká
aspoň jedna strana, V jen když si vykají obě.

1. **Pokyn v chatu** („Petrovi tykám“) má přednost. Zapiš ho do karty (bod 5).
2. **Uložený záznam v Raynetu:** řádek `Komunikace:` v Profilu klienta (`notice`), u kontaktní osoby (bankéř, partner)
   v její `notice`, např. `Komunikace: Adam tyká (Ahoj Petře) · Eva vyká (V1)`. Pole `salutation` nepoužívej: je jedno
   pro celý tým, ale tykání je vztah jednoho poradce.
3. **Poslední e-maily mezi pisatelem a dotyčným, oběma směry** (`email_list(companyId=…)` → `email_get`): oslovení
   („Ahoj Adame“ od klienta, „Ahoj Petře“ od pisatele) a tvary v textu. Platí ten nejnovější.
4. **Přepis hovoru, věty mezi pisatelem a dotyčným v obou směrech:** „ahoj, čau, máš, pošli, ty“ = T; „dobrý den, máte,
   pošlete, Vy“ = V. Prohozené mluvčí mezi nimi dvěma tu nevadí (tykání kterékoli strany = T). **Důkazem není tykání
   třetí osobě** (klient tyká manželce, kolegovi nebo makléři v místnosti): počítá se jen věta s oslovením pisatele
   („Adame, pošli…“) nebo zjevně jemu určená. Shrnutí Pocketu ani návrhy e-mailů od Pocketu nejsou důkaz.
5. **Nic z toho:** V1 a v náhledu `Oslovení: V1 – neověřeno`.

Neformálnější registr (V1 → V2 → T) jen na důkaz z bodů 1–4, nikdy odhadem. Když se zdroje rozcházejí (karta říká V,
dnešní hovor T), navrhni v náhledu změnu karty a e-mail napiš podle nejnovějšího důkazu z bodu 3 nebo 4; když ani to
není jisté, zeptej se.

**Víc oslovených najednou** (manželé, spolužadatelé): když všem pisatel tyká, „Ahoj Petře a Jano,“ a množné „vy“ malým.
Když aspoň jednomu vyká, celý e-mail ve vykání („Dobrý den, pane Nováku, paní Nováková,“) a v náhledu na to upozorni.
Kolegové v kopii registr neurčují.

**Vlákno klient + partner** (tipař nebo tým Martina Kořenka tyká Adamovi, klient je v kopii nebo osloven): „Dobrý den, všem,“
a celý text ve vykání (Adam, 29. 10. 2026). „Dobrý den, ahoj,“ nepiš.

### Kontrola před ukázáním návrhu (povinná)

Hotový text (bez podpisu) prožeň skriptem:

```bash
python3 scripts/check_tykani.py --rezim vykani|tykani --prijemcu <počet oslovených> navrh.txt
```

Skript najde tvary druhého registru (tykací zájmena a slovesa ve vykání, velké V a vykací slovesa v tykání, malé „vám“
při vykání jednomu člověku, nesedící oslovení). **Návrh s jediným nálezem uživateli neukazuj**, oprav ho a pusť skript
znovu. Bez Pythonu projdi text ručně podle tabulky výše. V náhledu uveď řádek
`Oslovení: T – „Ahoj Petře,“ (zdroj: klient tyká, e-mail 3. 10. „Ahoj Adame“) · kontrola OK`.

### Uložení do karty

Když registr zjistíš z bodu 1, 3 nebo 4 a v kartě chybí nebo je jiný, navrhni v náhledu doplnit řádek `Komunikace:`
v Profilu klienta (krok 11) nebo v `notice` kontaktní osoby. Příště se pak registr bere z karty.

## Rozhodnutí Adama (29. 10. 2026)

Odpovědi z artefaktu otázek, mají přednost před starším textem výše. Stejné znění je ve vaultu (`styl-komunikace`, sekce
„Rozhodnutí ke komunikaci“).

**Klienti**
- Krátký dotaz = krátká odpověď (2–4 věty); odrážky a mezititulky jen u shrnutí po hovoru a nabídek.
- Vykaným spisovně, tykaným investorům hovorově smí („mrknout“, „refin“, „neúčel“). Smajlíky podle tónu vlákna.
- Špatná zpráva: jedna krátká lidská věta + konkrétní důvod + cesta ven.
- Omluva za pozdní reakci na začátek, když od zprávy klienta uplynuly ≥ 3 pracovní dny.
- Návrh hovoru: 2 konkrétní termíny v pracovní době (po–pá), Google Meet.
- Placenou konzultaci smí agent nabídnout (po workshopu 10 000 Kč, jinak 15 000 Kč).
- Upomínka faktury den po splatnosti, věcně: „Ještě neeviduji úhradu faktury, splatnost byla do včera, prosím o úhradu.“
- Jazyk: Čechům a Slovákům česky, ostatním anglicky.
- Předmět nového e-mailu (mimo vlákno): „<Téma> – <klient/firma>“.
- Daňové a právní rady jen orientačně, vždy s větou, ať si to klient ověří u specialisty z oboru, a s nabídkou doporučení.
  Dál nikdy: slib schválení, úprava příjmů, interní metodika bank.

**Banky**
- Dotaz na metodiku vždy anonymně (bez jména, RČ, kontaktů), osobní údaje až v žádosti přes portál.
- Sazbu smí agent vyjednávat schválením u jiného klienta, bez identifikace klienta.
- Urgence po 3 pracovních dnech bez odpovědi, při blížící se lhůtě (rezervace, čerpání) hned.
- Eskalace (nadřízený bankéře, stížnost na pomalé vyřízení) jen na Adamův pokyn, agent připraví návrh.
- Do ČSOB Adam nepíše napřímo: odesílatel je `info@egfin.cz` nebo poradce, který případ zpracovává.

**Kolegové a partneři**
- Tón ke kolegům jako Adam (stručně, neformálně). V zadání vždy konkrétní datum, u urgentních i čas.
- K přeposlání vždy 1 věta s úkolem. Výtky a kontrolu práce kolegů agent jen navrhne, odesílá Adam.
- Tipařům a partnerům (výplata tipařské provize, stav případu) agent jen navrhne, odesílá Adam.
- Komu předat klienta: rotace podle vytížení, jednoduché případy primárně Fiedor a Fáber; Fiedorovi teď nic (v 1/2027 měsíc pryč).

## Naučená pravidla

Sem se zapisují pravidla, která vyplynou z Adamových úprav návrhů.
Jedno pravidlo na řádek, s datem a konkrétním příkladem — obecná pravidla
bez příkladu se špatně uplatňují.

Když Adam návrh upraví a řekne, co změnil (nebo vloží finální verzi),
vytáhni z rozdílu pravidlo a připiš ho sem. Pravidlo, které odporuje
něčemu výše v tomhle souboru, má přednost — je novější a vychází z praxe.

<!-- Formát: - 2026-09-28: <pravidlo> — příklad: „<před>" → „<po>" -->
