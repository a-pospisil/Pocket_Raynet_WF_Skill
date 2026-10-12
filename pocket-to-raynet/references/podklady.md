# Podklady od klienta

Otevři, když se v hovoru řeší úvěr a je potřeba zjistit, co od klienta ještě chybí.

## Obsah

- [Postup](#postup)
- [Kde zjistit, co už je](#kde-zjistit-co-už-je)
- [Co je potřeba](#co-je-potřeba)
- [Evidence v kartě OP](#evidence-v-kartě-op)

## Postup

1. **Co je potřeba** — z hovoru urči typ příjmu, účel úvěru a fázi případu a poskládej
   seznam z bloků níže. Nežádej všechno vždycky; seznam má odpovídat případu.
2. **Co už je** — projdi zdroje v [následující sekci](#kde-zjistit-co-už-je).
3. **Rozdíl** — každou položku označ: ✓ máme · ✗ chybí · ? nejasné.
4. **Koncept e-mailu** — jen ✗ položky, seskupené po blocích (viz `email-style.md`).
   Položky ? vyžádej podmíněně: „pokud jste ještě neposílal, prosím i o …".
   Položky, které si Adam zajišťuje sám, po klientovi **nechtěj**.
5. **Evidence** — co chybí a co bylo vyžádáno, patří do řádku „Otevřené body / doptat" v kartě OP
   (viz [Evidence v kartě OP](#evidence-v-kartě-op)).

U nového zájemce (lead) nic není — e-mail obsahuje celý seznam podle případu.

## Kde zjistit, co už je

Ověřeno 27. 9. 2026: doklady **nejsou** v Raynetu jako přílohy (`attachments: []` u klienta i OP) a **nejsou** ani na
Google Drive — tam jsou jen exporty nahrávek z Pocketu. Přílohy e-mailů nástroje Raynetu nevracejí. Co od klienta přišlo,
se proto zjišťuje z těchto zdrojů:

| Zdroj | Jak | Co v něm je |
|---|---|---|
| **Karta OP** | `businessCase_get(id)` → `description` | řádek „Otevřené body / doptat"; u starších OP ruční poznámky pod „Původní poznámky" (dřív oddíl „PODKLADY OD KLIENTA" s řádkem „Chybí:") |
| **E-maily od klienta** | `email_list(companyId=<id>, completedFrom=<začátek případu>)` → řádky, kde `from` je klient; `email_get(id)` jen u těch, které vypadají na podklady | text e-mailu — „v příloze posílám DP za rok 2025". U IMAP importů je `from` prázdné, pak rozhoduje předmět |
| **Dřívější hovory a schůzky** | `solution` a `description` aktivit klienta | co bylo slíbeno, co domluveno |
| **Tento hovor** | přepis (ne shrnutí Pocketu) | „už jsem vám to poslal", „pošlu zítra" |

`email_list` filtruje přes `completedFrom`, takže najde i přijaté e-maily, které nemají plánovaný čas; `activity_list`
s časovým oknem na `scheduledFrom` by je nevrátil. Samotné soubory k dispozici nejsou — rozhoduje, co o nich říkají zdroje
výše. Když si nejsi jistý, jestli dokument přišel, označ ho ? a zeptej se podmíněně, ne jako by chyběl.

## Co je potřeba

Označení zdroje: **(praxe)** = Adam to takhle žádá ve skutečných e-mailech nebo to
zaznělo v hovorech; **(obecně)** = běžná bankovní praxe, v Adamových datech zatím
nedoložená — ověřit a případně upravit.

### Vždy

- dva doklady totožnosti **(obecně)**

### Příjmy — podle typu

**Příjmy z nájmu** (praxe)
- daňové přiznání FO za poslední 2 roky
- výpis z účtu, kam nájmy chodí — pro začátek stačí tabulka: nemovitost, nájemce,
  měsíční nájem; případně nájemní smlouvy
- čistý nájem — bez energií a poplatků SVJ, které hradí pronajímatel

**Podíl na zisku / jednatel s.r.o.** (praxe)
- daňové přiznání PO **včetně příloh** — rozvaha a výkaz zisku a ztráty
  **v plném rozsahu** — za poslední 2 roky
- při meziročním nárůstu zisku o víc než 20 %: komentář k důvodu nárůstu —
  banka ho vyžaduje pro individuální posouzení

**OSVČ** (praxe)
- daňové přiznání FO za poslední 2 roky

**Obecný přehled příjmů** (praxe)
- přehled příchozích plateb za posledních 12 měsíců (výpisy z účtu)

**Zaměstnanec** (obecně)
- potvrzení o příjmu na formuláři banky
- výpisy z účtu za poslední 3 měsíce s příchozí mzdou

### Stávající závazky (praxe)

- ke každému úvěru: banka, aktuální zůstatek, měsíční splátka, splatnost
- přehled vlastněných nemovitostí

### Nemovitost do zástavy a odhad (praxe)

- adresa a číslo jednotky
- fotografie nemovitosti
- evidenční list nebo jiný doklad o výměře v m²
- průkaz energetické náročnosti (PENB) — u některých bank lepší sazba
- ~~list vlastnictví~~, ~~kupní smlouva~~ — **zajistí Adam z katastru, nežádat**

### Podle účelu

- **Refundace vlastních zdrojů**: doklad o úhradě kupní ceny z vlastních zdrojů;
  u ČSOB lze refundovat až 3 roky zpětně, jen když koupě nebyla financovaná
  jiným úvěrem (praxe)
- **Rekonstrukce, výstavba**: rozpočet, stavební povolení nebo ohlášení (praxe)
- **Koupě**: kupní nebo rezervační smlouva (obecně)
- **Refinancování**: úvěrová smlouva a aktuální vyčíslení zůstatku (obecně)

### Před čerpáním (praxe)

- potvrzení o bezdlužnosti
- zástavní smlouva, pojistná smlouva k nemovitosti

## Evidence v kartě OP

Co chybí, se vede v kartě OP (krok 10 skillu, šablona v `sablony-zapisu.md` → Karta OP) v řádku
**„Otevřené body / doptat"**. Samostatný oddíl pro podklady nezakládej.

Po vyžádání podkladů řádek aktualizuj při nejbližším zápisu karty, např. „DP 2025 a výpisy 7–9/2026 (vyžádáno e-mailem 12. 10.)".
Karta se přepisuje celá: před zápisem `businessCase_get`, ruční text zůstává pod „Původní poznámky" a původní `description`
ulož do audit logu jako `before` (akce `update_business_case`).
