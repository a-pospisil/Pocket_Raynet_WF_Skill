# Podklady od klienta

Otevři, když se v hovoru řeší úvěr a je potřeba zjistit, co od klienta ještě chybí.

## Obsah

- [Postup](#postup)
- [Kde zjistit, co už je](#kde-zjistit-co-už-je)
- [Co je potřeba](#co-je-potřeba)
- [Evidence v popisu OP](#evidence-v-popisu-op)

## Postup

1. **Co je potřeba** — z hovoru urči typ příjmu, účel úvěru a fázi případu a poskládej
   seznam z bloků níže. Nežádej všechno vždycky; seznam má odpovídat případu.
2. **Co už je** — projdi zdroje v [následující sekci](#kde-zjistit-co-už-je).
3. **Rozdíl** — každou položku označ: ✓ máme · ✗ chybí · ? nejasné.
4. **Koncept e-mailu** — jen ✗ položky, seskupené po blocích (viz `email-style.md`).
   Položky ? vyžádej podmíněně: „pokud jste ještě neposílal, prosím i o …".
   Položky, které si Adam zajišťuje sám, po klientovi **nechtěj**.
5. **Evidence** — do popisu OP připiš, co bylo vyžádáno (viz
   [Evidence v popisu OP](#evidence-v-popisu-op)).

U nového zájemce (lead) nic není — e-mail obsahuje celý seznam podle případu.

## Kde zjistit, co už je

Ověřeno 27. 9. 2026: doklady **nejsou** v Raynetu jako přílohy (`attachments: []`
u klienta i OP) a **nejsou** ani na Google Drive — tam jsou jen exporty nahrávek
z Pocketu. Co od klienta přišlo, se proto zjišťuje z těchto zdrojů:

| Zdroj | Jak | Co v něm je |
|---|---|---|
| **Popis OP** | `businessCase_get(id)` → `description` | oddíl „PODKLADY OD KLIENTA": co přišlo, kdy, a řádek **„Chybí:"** |
| **E-maily od klienta** | `activity_list(companyId=<id>)` → řádky `_entityName: "Email"`, kde je klient v roli `FROM` | text e-mailu — „v příloze posílám DPFO za rok 2025" |
| **Dřívější hovory a schůzky** | `solution` a `description` aktivit klienta | co bylo slíbeno, co domluveno |
| **Tento hovor** | přepis | „už jsem vám to poslal", „pošlu zítra" |

Samotné soubory k dispozici nejsou — rozhoduje, co o nich říkají zdroje výše.
Když si nejsi jistý, jestli dokument přišel, označ ho ? a zeptej se podmíněně,
ne jako by chyběl.

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

## Evidence v popisu OP

Stávající praxe (ověřeno na OP-26-0462): v `description` obchodního případu je
oddíl, který eviduje podklady:

```
PODKLADY OD KLIENTA (email 20.–21. 9. 2026, klient@example.cz):
- DPFO 2025 zasláno (příloha emailu). …
- Chybí: DPPO <firma> vč. příloh (rozvaha, VZZ v plném rozsahu) za 2 roky.
```

Po odeslání požadavku (tj. po vytvoření konceptu e-mailu) do oddílu připiš řádek:

```
- <datum>: vyžádáno e-mailem: <položky>
```

`businessCase_update` pole `description` **přepisuje celé**. Postup je proto vždy:
načti aktuální popis přes `businessCase_get`, připoj řádek, zapiš — a původní
popis ulož do audit logu jako `before` (akce `update_business_case`).
Když oddíl „PODKLADY OD KLIENTA" v popisu ještě není, založ ho na konci popisu.

Formát oddílu drž stejný jako výše — je čitelný pro lidi i pro příští běh skillu.
