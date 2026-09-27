# Katalog scénářů — podklad pro protokoly

Podklad ke schůzce 28. 9. 2026 ve 14:00.

Z hovoru 27. 9.: *„vyzkoušet všechny možný věci, co bys tomu mohl říkat, a z toho
vytvořit protokoly, který pak půjdou do hlavního promptu. Aby ty věci nedělal náhodně,
ale podle protokolu."*

Tohle je ten seznam. Každý řádek je situace, která reálně nastala nebo nastane,
a co s ní má robot udělat. Rozhodnuté situace jsou zapsané ve skillu
(`pocket-to-raynet/SKILL.md`) — ten je „hlavním promptem". Nerozhodnuté se musí
rozhodnout, než se jim dá protokol.

| Stav | Význam |
|---|---|
| ✅ | ve skillu, ověřeno na reálných datech |
| 🟡 | ve skillu, zatím neověřeno v ostrém provozu |
| ❓ | **k rozhodnutí** — skill to zatím neřeší nebo řeší provizorně |

## Obsah

- [A. Jaká je to nahrávka](#a-jaká-je-to-nahrávka)
- [B. Kdo je klient](#b-kdo-je-klient)
- [C. Co už v Raynetu je](#c-co-už-v-raynetu-je)
- [D. Obchodní případ](#d-obchodní-případ)
- [E. Co z hovoru vyplynulo](#e-co-z-hovoru-vyplynulo)
- [F. E-maily](#f-e-maily)
- [H. Podklady od klienta](#h-podklady-od-klienta)
- [G. Bezpečnost a audit](#g-bezpečnost-a-audit)
- [Otevřené otázky na zítřek](#otevřené-otázky-na-zítřek)
- [Doplň](#doplň)

## A. Jaká je to nahrávka

| # | Situace | Jak poznat | Co robot udělá | Stav |
|---|---|---|---|---|
| A1 | Hovor s klientem | protistrana řeší svůj úvěr/nemovitost | zpracuje | ✅ |
| A2 | Hovor s bankéřem přes víc případů | jeden bankéř, přeskakuje mezi klienty, metodika | nezapíše, vypíše s důvodem | ✅ |
| A3 | Hovor s bankéřem o jednom klientovi | bankéř + jeden případ | ❓ zapsat ke klientovi, nebo ne? | ❓ |
| A4 | Interní porada s kolegou | protistrana z týmu | nezapíše | ✅ |
| A5 | Diktované poznámky sobě | jeden mluvčí, „poznámky k…" | nezapíše | ✅ |
| A6 | Vývojový hovor | aplikace, issues, merge | nezapíše | ✅ |
| A7 | Nepřijatý hovor, zapomenuté nahrávání | útržky, ruch, žádná konverzace | nezapíše | ✅ |
| A8 | Prázdná / testovací nahrávka | pár desítek znaků | nezapíše | ✅ |
| A9 | Hovor za někoho jiného | „Martin G. — financování pro Fenni G." | zapíše k tomu, **čí je případ** | ✅ |
| A10 | Jeden hovor, dva klienti | manželé, spolužadatelé | ❓ ke komu? k oběma? | ❓ |
| A11 | Hovor s tipařem o jeho klientovi | tipař = protistrana, klient chybí | ❓ | ❓ |
| A12 | Hovor se slovenským klientem | slovenština v přepisu | zpracuje, shrnutí česky | 🟡 |
| A13 | **Soukromý hovor** | rodina, známí, lékař — ne klient ani kolega | osobní aktivita: `personal`, kategorie 112, **bez obsahu**, neutrální název | 🟡 |
| A14 | **Soukromý hovor s požadavkem** na úvěr nebo spolupráci | „hele, potřeboval bych hypotéku" | nový zájemce → lead (B11), hovor k leadu jen s obchodní částí | 🟡 |

## B. Kdo je klient

| # | Situace | Jak poznat | Co robot udělá | Stav |
|---|---|---|---|---|
| B1 | Hovor byl v kalendáři | naplánovaná aktivita v čase nahrávky | klient z aktivity, jméno jen ověří | 🟡 |
| B2 | Jméno přepsané správně | `match_name` → `jistý` | pokračuje | ✅ |
| B3 | Jméno zkomolené | `Balint`/`Balent`, `Semrád`/`Semerák` | `match_name` → `pravděpodobný`, v návrhu označí | ✅ |
| B4 | Cizí jméno, v CRM foneticky | „Bretschneider" = `Jan Bretšnajdr` | fonetické párování → `jistý` | ✅ |
| B5 | Jméno v pádě | „s Honzou Rumlem" | převede na 1. pád a domácké jméno | ✅ |
| B6 | Klient je v CRM dvakrát | Zbyněk Svoboda (613 a 603) | **zastaví**, předloží oba | ✅ |
| B7 | Klient v CRM není | `match_name` → `žádný` | **zastaví**, vyzve k ručnímu založení | ✅ |
| B8 | Klient je zatím lead | najde se v `lead_list`, ne v `company_list` | zapíše hovor k leadu | 🟡 |
| B9 | Osoba vs. její firma | Milan Čálek vs. Calek Invest s.r.o. | `pravděpodobný`, rozhodne podle obsahu | ✅ |
| B10 | Stejný e-mail u dvou lidí | `simkrom@seznam.cz` = Jiří i Jan Šimek | páruje e-mail + příjmení, ne e-mail sám | ✅ |
| B11 | **Nový zájemce** | první kontakt, požadavek na úvěr/spolupráci | navrhne **lead** (`leadPerson=true`); klient vznikne převodem v UI | 🟡 viz otázka 8 |
| B12 | Klient nenalezen, ale měl by tam být | hovor navazuje na dřívější jednání | zastaví a zeptá se | ✅ |

## C. Co už v Raynetu je

| # | Situace | Jak poznat | Co robot udělá | Stav |
|---|---|---|---|---|
| C1 | Hovor už zapsaný jako telefonát | aktivita klienta z téhož dne, téma sedí | přeskočí | ✅ |
| C2 | Hovor zapsaný jako **událost** | `Event`, ne `PhoneCall` (Macko) | přeskočí | ✅ |
| C3 | Hovor zapsaný ručně bez času | `scheduledFrom: null` (Čálek) | přeskočí | ✅ |
| C4 | Naplánovaný hovor po termínu, stejné téma | Tomáš Josef: plán 14:30, hovor 15:28 | **dokončí naplánovaný** | ✅ |
| C5 | Naplánovaný hovor po termínu, jiné téma | téma nesedí | založí nový, naplánovaný nechá | ✅ |
| C6 | Naplánovaný hovor v budoucnu | termín ještě nenastal | ❓ nechat, nebo zrušit, když už proběhl? | ❓ |
| C7 | Schůzka místo telefonátu | osobní schůzka nahraná na Pocket | ❓ zapsat jako `meeting`? | ❓ |

## D. Obchodní případ

| # | Situace | Jak poznat | Co robot udělá | Stav |
|---|---|---|---|---|
| D1 | Jeden otevřený OP | `businessCase_list` → 1 | naváže | ✅ |
| D2 | Víc otevřených OP | podle obsahu hovoru | vybere, nejde-li to, zeptá se | ✅ |
| D3 | Žádný OP, nová konkrétní potřeba | „chce hypotéku 10 mil." | navrhne **nový OP** | 🟡 |
| D4 | Žádný OP, jen obecné povídání | bez konkrétního záměru | zapíše hovor bez OP | 🟡 |
| D5 | OP patří jinému klientovi | Semerák → OP paní Staňkové | zeptá se | ✅ |
| D6 | Posun ve fázi | „banka schválila", „podepsáno" | ❓ má měnit fázi OP? | ❓ |
| D7 | Případ zanikl | „klient to vzdal", „jde jinam" | ❓ má OP uzavřít jako prohru? | ❓ |
| D8 | Změna částky | „nakonec 8 mil. místo 10" | ❓ má měnit `totalAmount`? | ❓ |

## E. Co z hovoru vyplynulo

| # | Situace | Jak poznat | Co robot udělá | Stav |
|---|---|---|---|---|
| E1 | Mám klientovi poslat seznam podkladů | action item `draft_email` | **koncept e-mailu** | 🟡 |
| E2 | Mám zavolat zpět | „zavolám vám ve čtvrtek" | naplánovaný telefonát | 🟡 |
| E3 | Mám něco zjistit / ověřit | „prověřím u ČSOB" | úkol | 🟡 |
| E4 | Klient má něco poslat | `assignee: Other` | nezakládá úkol | ✅ |
| E5 | Zpráva přes SMS / WhatsApp | action item `send_message` | text ke zkopírování | 🟡 |
| E6 | Úkol už založila automatika OP | „Zaslat nabídku_", „EPP 2" | neduplikuje | 🟡 |
| E7 | Domluvená schůzka | „uvidíme se v úterý v 10" | ❓ založit `meeting`? zapsat do kalendáře? | ❓ |

## F. E-maily

| # | Situace | Co robot udělá | Stav |
|---|---|---|---|
| F1 | Jakýkoli e-mail | **nikdy neodešle**, připraví koncept `.eml` | 🟡 |
| F2 | Koncept otevřený v Apple Mail | otevře se k úpravě (`X-Unsent: 1`) | 🟡 ověřit na Macu |
| F3 | Adresa příjemce | vezme z Raynetu, **ne z Pocketu** (Pocket si ji vymýšlí) | 🟡 |
| F4 | Kolega do kopie | podle hovoru, typicky přidělený poradce | ❓ podle čeho poznat? |
| F5 | Klient, se kterým si tyká | pozná z hovoru („Ahoj Martine") | 🟡 |
| F6 | Uživatel koncept upraví | pravidlo z rozdílu → `email-style.md` | 🟡 |
| F7 | Příloha | jen soubor, který existuje; nic nevymýšlí | 🟡 |
| F8 | Koncept přímo ve schránce místo souboru | ❓ běží egfin.cz na Microsoft 365? Pak jde `outlook_create_draft` | ❓ |

## H. Podklady od klienta

| # | Situace | Co robot udělá | Stav |
|---|---|---|---|
| H1 | V hovoru se řeší úvěr | sestaví seznam podkladů podle typu příjmu, účelu a fáze | 🟡 |
| H2 | Existující klient | zjistí, co už přišlo: oddíl „PODKLADY OD KLIENTA" v popisu OP, e-maily od klienta v Raynetu, hovor | 🟡 |
| H3 | Nový zájemce (lead) | nic nemá → e-mail s celým seznamem podle případu | 🟡 |
| H4 | Nejasné, jestli dokument přišel | vyžádá podmíněně („pokud jste ještě neposílal…") | 🟡 |
| H5 | LV, kupní smlouva | **nežádá** — Adam si zajistí z katastru | 🟡 |
| H6 | Po vyžádání | připíše do popisu OP řádek „vyžádáno e-mailem: …" (přepis → stav před změnou do logu) | 🟡 |
| H7 | Kde fyzicky leží soubory | ❓ v Raynetu ani na Drive nejsou — e-mailová schránka? Broker Trust? | ❓ |

## G. Bezpečnost a audit

| # | Situace | Co robot udělá | Stav |
|---|---|---|---|
| G1 | Každá akce | řádek do audit logu | 🟡 |
| G2 | Přepis existujícího záznamu | uloží stav **před** změnou; bez něj přepis odmítne | 🟡 |
| G3 | Uživatel návrh opraví | zapíše `outcome: edited` | 🟡 |
| G4 | Rodné číslo, číslo účtu v přepisu | do CRM nezapíše (v e-mailu ponechá) | ✅ |
| G5 | Vypnutí potvrzování | rozhoduje uživatel podle `audit_log.py stats` | 🟡 |
| G6 | Smazání záznamu | **nemožné** — MCP nemá delete | ✅ |
| G7 | Založení klienta | přes `company_create` **nemožné** (umí jen firmu) → místo toho lead | ✅ |

## Otevřené otázky na zítřek

Rozhodnutí, bez kterých některé ❓ řádky nemají protokol:

1. **Kdy vypnout potvrzování u zápisu hovorů?** Návrh: jakmile z posledních 20 návrhů
   budete opravovat nejvýš jeden. `audit_log.py stats` to ukáže sám.
2. **Má robot posouvat fáze OP** podle toho, co v hovoru zazní (D6–D8)? Je to užitečné,
   ale je to přepis — a v Raynetu na fázi visí automatika.
3. **Leady (B8):** zapsat hovor k leadu, nebo lead nejdřív převést na klienta?
4. **Schůzky (C7, E7):** zapisovat osobní schůzky jako `meeting`? Zakládat domluvené
   schůzky i do kalendáře?
5. **E-maily (F8):** koncept jako soubor, nebo přímo ve schránce? Pokud egfin.cz běží
   na Microsoft 365, jde koncept vložit rovnou do Konceptů v Outlooku.
6. **Kde Hermes povede audit log** a kdo ho bude číst? Při stovce akcí denně se
   nikdo nebude dívat do JSONL — chce to denní souhrn (Telegram/e-mail).
7. **Hovor s bankéřem o jednom klientovi (A3)** — do CRM, nebo ne?
8. **Nový zájemce: lead, nebo rovnou klient?** Pokyn zněl „zakládá se klient". Přes MCP
   jde klient jako fyzická osoba založit jen oklikou: `company_create` vyrobí firmu,
   u které se pak ručně přepne typ — přesně tak vzniklo ~80 špatně označených záznamů
   z importů. Skill proto zakládá **lead** (umí fyzickou osobu), klient vznikne jeho
   převodem v Raynet UI. Pokud chcete rovnou klienta i za cenu ručního přepnutí typu,
   jde to změnit.
9. **Kde leží doklady klientů (H7)?** Pro seznam „co chybí" stačí evidence v OP
   a e-maily v Raynetu. Kdyby šlo dohledat i samotné soubory (schránka egfin.cz,
   Broker Trust), byla by kontrola přesnější.
10. **Seznam podkladů** v `references/podklady.md` — položky označené *(obecně)* jsou
   běžná bankovní praxe, ve vašich e-mailech zatím nedoložená. Projít a opravit.

## Doplň

Situace, které tu chybí — sem je připište, ať se do protokolu dostanou:

| # | Situace | Co má robot udělat | Poznámka |
|---|---|---|---|
| | | | |
