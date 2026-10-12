# Raynet — referenční přehled

Ověřeno na instanci `evergreen` dne 21. 9. 2026 čtením reálných dat. Pole klienta a OP, klíče vlastních polí a hodnoty roletek
doplněny 12. 10. 2026 z Adamova manuálu (pole přečtená v UI v Nastavení » Nastavení evidence, klíče ověřené zápisem a čtením
přes MCP) a z kontroly reálných OP.
Plný audit: `docs/AUDIT-POCKET-RAYNET.md` v repozitáři.

## Obsah

- [Konstanty](#konstanty)
- [Typy aktivit](#typy-aktivit)
- [Stavy aktivit](#stavy-aktivit)
- [Založení leadu](#založení-leadu)
- [Soukromé aktivity](#soukromé-aktivity)
- [Fáze obchodního případu](#fáze-obchodního-případu)
- [Obchodní případ: standardní pole](#obchodní-případ-standardní-pole)
- [Kategorie aktivit](#kategorie-aktivit)
- [Číselníky klienta a prohry](#číselníky-klienta-a-prohry)
- [Povinná pole při zakládání](#povinná-pole-při-zakládání)
- [Klient: standardní pole](#klient-standardní-pole)
- [Vlastní pole](#vlastní-pole)
  - [Klient (`company`)](#klient-company)
  - [Obchodní případ (`businessCase`)](#obchodní-případ-businesscase)
  - [Hodnoty roletek](#hodnoty-roletek)
  - [Formáty hodnot](#formáty-hodnot)
- [Soubory a přílohy](#soubory-a-přílohy)
- [Vazby mezi entitami](#vazby-mezi-entitami)
- [Pasti, které nejsou vidět ze schématu](#pasti-které-nejsou-vidět-ze-schématu)
- [Hledání a filtry](#hledání-a-filtry)
- [Co MCP neumí](#co-mcp-neumí)

## Konstanty

| Co | Hodnota |
|---|---|
| Vlastník (`owner`) | **zjistit za běhu**: `user_info` → `username` → `person_list(email=…)` → `id` (Adam = 2) |
| Uživatelé (id osoby) | Adam Pospíšil 2 · Michal Čakovský 9 · Michal Kutina 10 · Eva Hofmanová 13 · Kateřina Háblová 21 · Martin Fiedor 42 (k 2026-10-12; další přes `person_list`) |
| `securityLevel` „Sdílená" | 1 |
| `businessCaseType` „Úvěrový proces" (jediný používaný) | 64; historický typ „Provize“ 188 (Q1 2026) nepoužívat |
| Měna Kč (`currency`) | 40 |
| Rate limit | 24 000 req/den; `rate_limit_status` se nepočítá |
| Formát data pro API | `yyyy-MM-dd HH:mm` nebo ISO 8601 **s milisekundami** |

Formát ISO bez milisekund je odmítnut. `2026-01-01T12:00:00+01:00` neprojde,
`2026-01-01T12:00:00.000+01:00` ano.

## Typy aktivit

Ověřeno 12. 10. 2026 prvním ostrým zápisem ke klientovi.

| Typ (`_entityName`) | MCP | Pole „Výsledek“ (`solution`) v UI | Pro AI zápis |
|---|---|---|---|
| Schůzka (`Meeting`) | `meeting_*` | ano | **ano** (osobní nebo online schůzka) |
| Telefonát (`PhoneCall`) | `phonecall_*` | ano | **ano** (hovor) |
| Událost (`Event`) | `event_*` | **ne** | **ne**: zápis v `solution` se na kartě klienta nezobrazí, časová osa ukáže jen název |
| Úkol (`Task`) | `task_*` | – | jen souhrnný úkol (checklist + návrh e-mailu v `description`) |

- **Typ přes MCP změnit nejde** (žádný nástroj). Převod dělá člověk v UI v detailu aktivity.
- **Převod Událost → Schůzka v UI vytvoří novou Schůzku s novým id.** Přenese název, čas, klienta, účastníky, štítky
  i `solution`, původní Událost zanikne. `event_get` na staré id pak vrací **502 Bad Gateway** (ne „nenalezeno“) a Událost
  zmizí i z `activity_list`. Novou Schůzku najdeš přes `activity_list(companyId=…, entityType="meeting")`.
- **Naplánované schůzky z kalendáře bývají Události.** 12. 10. 2026 byly všechny položky dne v kalendáři Adama typu `Event`,
  nejspíš je zakládá obousměrná synchronizace s Google kalendářem `[k ověření]`. Postup skillu: `SKILL.md`, tvrdé pravidlo 7
  a větev A2.
- K ověření: dá se v nastavení synchronizace Google kalendáře zvolit import jako Schůzka? Umí REST API změnit typ aktivity?
  Zachová převod v UI vazbu na událost v Google kalendáři?

## Stavy aktivit

`EActivityStatus`:

| key | caption | `completed` |
|---|---|---|
| `NEW` | Nenaplánován | null |
| `SCHEDULED` | Naplánován | null |
| `COMPLETED` | **Realizován** | timestamp |
| `CANCELLED` | Zrušen | timestamp |

Neexistuje boolean „hotovo" — `completed` je časová značka, ne příznak. Proto v žádném
`*_list` není filtr dokončeno/nedokončeno; filtruje se přes `status`.

`EActivityPriority` **chybí v resource `raynet://enumerations`**, i když se na něj
popisy nástrojů odvolávají. V datech pozorováno `DEFAULT` a `CRITICAL`. Analogická
`ELeadPriority` má `MINOR` / `DEFAULT` / `CRITICAL`. Shodnost obou = neověřeno,
takže při zápisu priority drž se `DEFAULT` a `CRITICAL`, které jsou doložené.

`EDocumentBaseStatus` (obchodní případy): `B_ACTIVE` = otevřený, `E_WIN` = akceptován,
`F_LOST` = zamítnut, `G_STORNO` = zrušen.

## Fáze obchodního případu

Pro `businessCaseType` 64. Stav OP se odvozuje z fáze — `status` nelze nastavit přímo.

| id | Fáze | Výchozí `probability` |
|---|---|---|
| 10 | Identifikace požadavku | 60 |
| 1 | Nabídnuto | 70 |
| 2 | Podaná žádost + EPP 2.0 | 80 |
| 3 | Kompletace dokumentů + odhad | 85 |
| 7 | Čeká na schválení | 90 |
| 11 | Schváleno | 95 |
| 8 | Podepsáno | 100 |

Když `probability` neposíláš, Raynet ji přepočítá z fáze. Poslaná hodnota (0–100) se zaokrouhlí na 5.

Uzavřené fáze (dohledány na reálných OP):

| id | Fáze | Odvozený `status` | Výchozí `probability` |
|---|---|---|---|
| 4 | Výhra | `E_WIN` | 100 |
| 5 | Prohra | `F_LOST` | – |
| 6 | Zrušeno | `G_STORNO` | – |

Platná id celkem: 1–8, 10–14. Názvy 12, 13, 14 zůstávají neověřené. Neplatné id vrátí
chybu, která vyjmenuje platná — toho se dá využít místo hádání.

### Kategorie OP

`raynet://codelist/businessCaseCategory`:

| id | Kategorie |
|---|---|
| 116 | hypoteční úvěr |
| 184 | Podnikatelský úvěr |
| 189 | Spotřebitelský úvěr - neúčelový |
| 169 | úvěr ze stavebního spoření |
| 118 | investice |
| 119 | životní pojištění |
| 117 | pojištění vozidel |
| 147 | pojištění majetku |
| 148 | pojištění odpovědnosti |
| 149 | penzijní spoření |
| 150 | stavební spoření |

### Založení OP

OP skill navrhne založit, když hovor evidentně řeší konkrétní případ a klient pro něj OP nemá (krok 6, Adam 12. 10. 2026), vždy po potvrzení:

```
businessCase_create(
  name             = "<banka/produkt> – <popis>",  # OP se jmenují podle banky a produktu
  company          = <clientId>,                    # povinné, OP bez klienta nejde
  businessCaseType = 64,                            # Úvěrový proces, jediný typ
  category         = <viz Kategorie OP>,
  businessCasePhase= <id fáze>,                     # u běžící žádosti typicky 2 „Podaná žádost + EPP 2.0"
  totalAmount      = <výše>,                        # a stejná částka do vlastního pole vyse_uveru
  customFields     = {producent: <banka>, vyse_uveru: <výše>}   # klíče viz Vlastní pole
)
```

Výši neznáš → zeptej se. `status` se z fáze odvozuje a nastavit přímo nejde.

### Automatika při založení OP

Založení OP spustí v Raynetu automatiku (`createdBy: SYSTEM_USER`), která ve stejnou
minutu vytvoří dva úkoly navázané na nový OP:

- `Zaslat nabídku_ <název OP>` — priorita `CRITICAL`
- `EPP 2 - připravit k žádosti <klient> <kód OP> <název OP>`

Ověřeno na OP-26-0462 (18. 9.) a OP-26-0480 (22. 9.). Skill tyhle úkoly nezakládá
ani do souhrnného úkolu nepřebírá — vznikly by dvakrát.

### Názvy OP

**Případy se jmenují podle banky a produktu**, ne podle klienta — „Moneta SBL",
„Podnikatelský úvěr Moneta – nemovitost 2–3 mil. Kč". Stejný název se opakuje
u různých klientů (11 OP s „Moneta" v názvu napříč různými firmami), takže název
sám o sobě klienta neurčuje.

## Obchodní případ: standardní pole

Z manuálu 12. 10. 2026 (UI » Nastavení evidence). „Povinné v UI“ hlídá formulář, ne API: `businessCase_create` vyžaduje jen
`name` a `company` `[k ověření: jestli povinná pole fáze platí i pro API]`.

| Pole (UI) | Parametr | Poznámka |
|---|---|---|
| Předmět | `name` | povinné, název podle banky a produktu ([Názvy OP](#názvy-op)) |
| Klient | `company` | povinné (id); `person` = kontaktní osoba, nepovinné |
| Vlastník | `owner` | id osoby |
| Typ obchodu | `businessCaseType` | 64 |
| Fáze | `businessCasePhase` | `status` se z ní odvodí ([Fáze](#fáze-obchodního-případu)) |
| Otevřeno od / Odhad uzavření / Uzavřeno | `validFrom` / `scheduledEnd` / `validTill` | `yyyy-MM-dd` |
| Pravděpodobnost | `probability` | 0–100, zaokrouhlí se na 5; bez ní se dopočítá z fáze |
| Zdroj | `source` | **povinné v UI**; stejný číselník jako `contactSource` (156 doporučení tipaře…) |
| Typ produktu | `category` | **povinné v UI** ([Kategorie OP](#kategorie-op)) |
| Popis | `description` | HTML, karta OP |
| Částka / zisk / náklad | `totalAmount`, `tradingProfit`, `estimatedValue` | bez položek se zisk dopočítá jako částka − náklad; `estimatedValue` nemusí vidět uživatel bez oprávnění k nákladům |
| Důvod / kategorie prohry | `losingReason`, `losingCategory` | číselník v [Číselníky klienta a prohry](#číselníky-klienta-a-prohry) |
| Štítky | `tags` | přepisují se celé |
| Klasifikace 1–3 | `businessCaseClassification1-3` | skryté, nepoužívat |

`businessCase_create` nepřidá přílohy ani položky (`items`). Přílohu (`attachmentLink`) lze přidat až `businessCase_update`.

## Založení leadu

Povinná a vhodná pole jsou v [Povinná pole při zakládání](#povinná-pole-při-zakládání), zdroje kontaktu
v [Číselníky klienta a prohry](#číselníky-klienta-a-prohry). Navíc:

- `owner` z kroku 0 skillu, nikdy napevno.
- `leadCategory` (`raynet://codelist/leadCategory`) jsou jména poradců a tipařů (např. 195 Bez tipaře) — stejná logika jako
  `category` u klienta: kdo dostane podíl na provizi. Jen výslovně jmenovaný tipař, jinak prázdné nebo se zeptej.
- `priority`: `ELeadPriority` = `MINOR` / `DEFAULT` / `CRITICAL`.
- Klient z leadu vznikne **převodem v Raynet UI**. `lead_convert` přes MCP jen napojí lead na už existující firmu, osobu nebo OP
  a nic nezakládá. Hovor mezitím zapiš k leadu: `phonecall_create(lead=<id>, …)`.

## Soukromé aktivity

Skill je nezakládá: osobní hovory do Raynetu nepatří (rozhodnutí 1. 10. 2026, `docs/NAVRH-ZAPISY.md`). Kdyby se to změnilo,
ustálená podoba v datech je `personal: true`, `category` 112 „soukromá aktivita", bez `company`, bez `description`
i `solution`, krátký neutrální název. `securityLevel` zůstává 1 „Sdílená" — záznam vidí celý tým.

## Kategorie aktivit

`raynet://codelist/activityCategory`:

| id | Název |
|---|---|
| 111 | prioritní |
| 110 | dohodnuto napevno |
| 183 | Předběžný termín |
| 151 | výroční schůzka |
| 152 | zpracování administrativy |
| 112 | soukromá aktivita |
| 154 | Nepotvrzeno |
| 181 | Vypracování nabídky |

Nastavení `category` přepíše `color` server-side podle barvy kategorie, takže posílat
`color` vedle `category` nemá smysl.

## Číselníky klienta a prohry

Stav k 2026-10-01 (`raynet://codelist/<entity>`; při chybě id vždy načíst znovu, číselníky se mění).

| Číselník | Položky (id) |
|---|---|
| `contactSource` (zdroj kontaktu) | 156 doporučení tipaře · 82 vlastní kontakt · 81 Doporučení (netipař) · 79 web/poptávka · 179 sociální sítě · 196 workshop |
| `companyCategory` (= **tipař**, určuje dělení provize) | 176 Bez tipaře · 193 Adam Pospíšil · 205 Monopoly Advisory · 180 Úspěšné reality · 113, 175, 197, 190, 153, 155, 157, 186, 208 = jednotliví tipaři (jména v číselníku) |
| `companyClassification1` (role kontaktu, ne klienta) | 172 VIP · 171 Tipař · 177 Hypoteční specialista · 174 Key account manager · 178 Firemní bankéř · 173 Obchodní partner |
| `companyClassification2`, `3` | prázdné |
| `economyActivity` (obor) | jen 202 architekt, nepoužívat |
| `losingCategory` (kategorie prohry) | 203 nezvedá · 191 Nedostatečná bonita · 124 cena · 125 konkurence · 126 termín · 198 Zamítnuto bankou · 200 klientovi nevyšel záměr koupě, vada nemovitosti · 127 jiná |

## Povinná pole při zakládání

| Entita | Povinné |
|---|---|
| `phonecall_create` | `title`, `owner` |
| `meeting_create` / `event_create` | `title`, `owner` |
| `task_create` | `title`, `deadline`, `owner` + alespoň jedno z `personal=true`, `person`, `company`, `lead` |
| `businessCase_create` | `name`, `company` |
| `company_create` | `name`, `rating`, `state`, `role` |
| `person_create` | `lastName` |

`owner` nemá default a neexistuje pro něj lookup nástroj. Skill ho zjistí za běhu z přihlášeného uživatele
(`user_info` vrátí `username` = e-mail, `person_list(email=…)` vrátí id; ověřeno 1. 10. 2026: adam.pospisil@egfin.cz → 2).
Každý kolega má vlastní instanci Herma a zapisuje sám za sebe.

`lead_create` funguje (na rozdíl od fyzické osoby): povinné je jen `topic`, vhodné `firstName`, `lastName`, `leadPerson=true`,
`email`, `tel1`, `contactSource`. Použij, když volající v CRM není.

## Klient: standardní pole

Z manuálu 12. 10. 2026. Klient je vždy `company` (organizace); jak skill pole plní, je v `sablony-zapisu.md`, „Karta klienta“.

| Pole (UI) | Parametr | Poznámka |
|---|---|---|
| Název | `name` | povinné; u fyzické osoby „Jméno Příjmení“ (jméno a příjmení zvlášť jen v UI nebo CSV importem) |
| Vztah / Stav / Rating | `role` / `state` / `rating` | povinné při založení: `role` A_SUBSCRIBER = klient; `state` A_POTENTIAL · B_ACTUAL · C_DEFERRED · D_UNATTRACTIVE; `rating` A / B / C |
| Vlastník | `owner` | id osoby |
| Kategorie | `category` | **tipař** (`companyCategory`, určuje dělení provize) |
| Zdroj kontaktu | `contactSource` | číselník výše |
| Poznámka | `notice` | HTML; Profil klienta |
| IČO / DIČ / plátce DPH | `regNumber` / `taxNumber` / `taxPayer` | `taxPayer` = `YES` / `NO` |
| Adresa | `street`, `city`, `province`, `zipCode`, `country` (ISO, `CZ`), `territory`, **`addressName`** | ⚠️ `addressName` je **povinný, jakmile posíláš jakékoli adresní nebo kontaktní pole** (i jen `phone` nebo `email`); v instanci se používá „Sídlo klienta“ |
| Kontakt | `phone` (Tel 1), `email`, `email2`, `www` | v UI je Tel 1 povinný |
| Sítě | `facebook`, `instagram`, `linkedin`, `whatsapp`, `tiktok`, `threads`, `skype`, `youtube`, `pinterest`, `twitter` | |
| Další | `bankAccount`, `legalForm`, `turnover`, `employeesNumber`, `paymentTerm`, `economyActivity`, `companyClassification1-3` | číselníky (id); `bankAccount` jen z dokumentu |
| **Přes MCP nejde** | logo, typ subjektu (fyzická osoba), jméno a příjmení zvlášť, binární přílohy | jen UI nebo import. Štítky klienta manuál uvádí také jako „nejde přes MCP“, u aktivit štítky fungují `[k ověření u klienta]` |

Výchozí „preference subjektu“ v UI instance je *Fyzická osoba*; přes MCP vznikne vždy organizace, typ se přepíná v UI.

## Vlastní pole

**Obecně.** `customFields` se klíčují **technickým klíčem**, ne popiskem. Tvar `<popisek bez diakritiky, ~10 znaků>_<5 hex>`
(např. `Provize_dc7d2`); hash nejde odvodit. MCP **nevrací definice** polí, klíč je vidět jen u záznamu, kde je pole vyplněné
(`company_get` / `businessCase_get`). UI (Nastavení » Nastavení evidence » Nastavení polí) klíče neukazuje, REST je vrací
v `GET /api/v2/customField/config/`. Neznámý klíč: vyplnit pole v UI na jednom záznamu → `*_get` → doplnit sem.

- Update je částečný: posílej jen měněné klíče. **`null` nebo prázdná hodnota v `customFields` pole smaže.**
- Roletka: zapisuj **přesný text volby** (diakritika, mezery, „a.s.“). Hodnota mimo seznam se uloží, ale v UI se nezobrazí jako
  výběr. Reálně: importované OP z Broker Trust mají `Provize_dc7d2 = "BT"`, což v seznamu není.
- Po zápisu vždy `*_get` a kontrola, že pole mají očekávané hodnoty.

Průzkum instance k 2026-10-01 (69 OP, 50 klientů, 30 leadů, 80 aktivit): vlastní pole klienta vyplněná u 18 % klientů, hlavně
z webového formuláře /analyza-portfolia. Lead a aktivity vlastní pole ve vzorku nemají, web všechno píše do `notice`.

### Klient (`company`)

Všechna pole jsou nepovinná a všechny klíče jsou ověřené zápisem a čtením přes MCP (pole typu soubor nahráním v UI a čtením).
Sloupec **Skill** říká, odkud smí skill hodnotu vzít: *hovor* = z přepisu, jen když jistě zazní; *dokument* = jen z dokumentu
(DP, doklad, výpis, smlouva), nikdy z hovoru; *BT kredit* = jen hodnota z výpočtu BT kredit, ne odhad; *číst* = pole typu
soubor, MCP ho nevyplní; *ne* = nevyplňovat.

**Osobní údaje**

| Popisek | Typ | Klíč | Skill |
|---|---|---|---|
| rodné číslo | text | `Rodne_cisl_ed0da` | dokument (tvrdé pravidlo 5) |
| rodné příjmení | text | `rodne_prij_1de2b` | dokument |
| státní přísl. | text | `statni_pri_8265e` | dokument |
| číslo OP | text | `cislo_OP_d2c59` | dokument |
| OP vydal | text | `OP_vydal_abab5` | dokument |
| platnost OP | datum | `platnost_O_5ac2f` | dokument |
| vzdělání | roletka | `vzdelani_b79fe` | hovor |
| rodinný stav | roletka | `rodinny_st_adceb` | hovor |
| Zúžení SJ | roletka | `Zuzeni_SJ_f0b36` | hovor |
| Počet dětí | číslo | `Pocet_deti_cf874` | hovor (vyživované děti) |
| hlavní běžný ú. | roletka | `hlavni_bez_5fef9` | hovor (banka hlavního účtu) |

**Výdaje.** Textová pole mají všechna prefix `DruhBankaJ_` (pole se původně jmenovala „Druh/Bnk/Jist/…“) a **liší se jen hashem**.
Řádek = jeden úvěr, údaje v pořadí popisku: `druh / banka / jistina / úrok % / splátka / měsíců / fixace / KF`.

| Popisek / pozice | Typ | Klíč | Skill |
|---|---|---|---|
| Bydlení | text | `DruhBankaJ_57559` | hovor (měsíční náklady bydlení) |
| Domácnost | text | `DruhBankaJ_f41e1` | hovor (měsíční výdaje domácnosti) |
| Přehled úvěrů | soubor | `Prehled_uv_6cdfe` | číst |
| úvěr řádek 1 (nejvýš) | text | `DruhBankaJ_a886e` | hovor |
| úvěr řádek 2 | text | `DruhBankaJ_4de8f` | hovor |
| úvěr řádek 3 | text | `DruhBankaJ_6314d` | hovor |
| úvěr řádek 4 | text | `DruhBankaJ_8f94a` | hovor |
| úvěr řádek 5 | text | `DruhBankaJ_cae7c` | hovor |
| CELKEM | text | `DruhBankaJ_4c59a` | hovor, jen když jsou známé všechny řádky |

**Zaměstnání**

| Popisek | Typ | Klíč | Skill |
|---|---|---|---|
| měsíční příjem | číslo | `mesicni_pr_0a298` | hovor; **vždy čistý** měsíční příjem ze závislé činnosti. Zazní-li hrubý, přepočet na čistý (`sablony-zapisu.md`), doložená hodnota ho přepíše (Adam, 12. 10. 2026) |
| zaměstnavatel | text | `zamestnava_ffa65` | hovor |
| pracovní pozice | text | `pracovni_p_f7e4d` | hovor |
| nástup | datum | `nastup_fbbb1` | hovor (měsíc a rok → 1. den měsíce; jen rok → do profilu, pole prázdné) |
| Druh | roletka | `Druh_fcd16` | hovor (HPP / DPČ / DPP) |

**Nájmy**

| Popisek | Typ | Klíč | Skill |
|---|---|---|---|
| Nájmy v DPFO | zatržítko | `Najmy_v_DP_bb662` | hovor (`true` / `false`) |
| Současný čistý nájem | **text** | `Soucasny_c_952ff` | hovor (číslo jako řetězec, např. `"27000"`) |
| Budoucí čistý příjem | **text** | `Budouci_5f2ff` | hovor (čistý nájem po koupi, jako řetězec) |

**Příjmy z podnikání dle BT kredit 2.** Bankovní řádky nesou částku, kterou daná banka podle výpočtu BT kredit (z DPFO nebo
alternativním výpočtem) uznává klientovi jako příjem z podnikání. Nikdy odhad.

| Popisek | Typ | Klíč | Skill |
|---|---|---|---|
| Počátek podnikání | datum | `Pocatek_po_ab1d0` | hovor |
| Druh činnosti | text | `Druh_cinno_d75a7` | hovor |
| DPFO poslední | soubor | `DPFO_posle_46c18` | číst |
| DPFO předposlední | soubor | `DPFO_predp_6db0e` | číst |
| Svobodné povolání | roletka | `Svobodne_p_705f3` | hovor |
| Výše paušálu | roletka | `Vyse_pausa_4549e` | hovor |
| Žadatel v režimu paušální daně | zatržítko | `Zadatel_v__a594e` | hovor (`true` / `false`) |
| Alternativní výpočet ČSOB | zatržítko | `Alternativ_b3c97` | BT kredit |
| Česká spořitelna | text | `Radek_101__b1dea` | BT kredit |
| ČSOB Hypoteční banka | text | `Radek_102__56301` | BT kredit |
| Raiffeisenbank | text | `Radek_37_z_d1a4d` | BT kredit |
| Komerční banka | text | `Radek_74_z_a6a87` | BT kredit |
| mBank | text | `mBank_9af71` | BT kredit |

**Právnická osoba**

| Popisek | Typ | Klíč | Skill |
|---|---|---|---|
| Výsledek: ČS/ČSOB/RB/UCB/mBank | text | `VysledekCS_a6436` | BT kredit |
| DPPO poslední | soubor | `DPPO_posle_fd646` | číst |
| DPPO předposlední | soubor | `DPPO_predp_a7809` | číst |
| Výkaz zisků a ztrát – poslední | soubor | `Vykaz_zisk_85c88` | číst |
| Výkaz zisků a ztrát – předposlední | soubor | `Vykaz_zisk_bbbbe` | číst |
| Účetní rozvaha – poslední | soubor | `Ucetni_roz_6defa` | číst |
| Účetní rozvaha – předposlední | soubor | `Ucetni_roz_cdbc0` | číst |

**Doplňující údaje**

| Popisek | Typ | Klíč | Skill |
|---|---|---|---|
| Doplňující údaje | velké textové pole | `Doplnujici_a57c0` | ne (profil klienta je v `notice`, ať nevzniknou dvě místa) |
| Bety | text | `Bety_8f936` | ne (význam neznámý) |

### Obchodní případ (`businessCase`)

Skill pole OP čte pro kartu OP a bonitu. Když hovor evidentně řeší případ, doplní prázdná pole podle `sablony-zapisu.md`,
„Pole OP z hovoru“ (Adam, 12. 10. 2026); výši existujícího OP mění jen na pokyn, fázi jen navrhuje. Klíč `?` = pole zatím nikde vyplněné, klíč
neznámý (zjistit postupem výše). Sloupec „Vyplněno“ = počet OP s vyplněným polem ve vzorku 119 OP k 2026-10-12.

**Hypotéky**

| Popisek | Typ | Klíč | Vyplněno |
|---|---|---|---|
| Žádost (BEZ HESLA) | soubor | `Zadost_fc4dc` (jen číst) | 49 |
| výše úvěru | číslo | `vyse_uveru_ad8b6` | 50 |
| úroková sazba | číslo (desetinné) | `urokova_sa_51229` | 5 |
| Doba fixace v měsících | roletka | `Doba_fixac_172ca` (hodnoty slovně: `3 roky`) | 5 |
| platnost fixace od | datum | `platnost_f_e63c5` | 2 |
| konec fixace | datum | `konec_fixa_65281` | 26 |
| výše splátky | číslo (desetinné) | `vyse_splat_fff50` | 5 |
| Splatnost (v měsících) | číslo | `Splatnost_7586b` (měsíce: 30 let = `360`, v datech se objevil i omyl `30`) | 28 |
| Hodnota zástavy | měna (číslo) | `Hodnota_za_21c14` (u nezajištěných `0`) | 37 |
| LTV | procenta (číslo) | `LTV_eedee` | 3 |
| Účel úvěru | roletka | `Ucel_uveru_47dd5` | 48 |
| Pojištění | roletka | `Pojisteni_1b7ae` | 25 |
| Představení nabídky klientovi | datum | `Predstaven_47ad0` (plní ho i workflow při fázi „Nabídnuto“) | 69 |
| Datum podpisu žádosti | datum | `Datum_podp_02aa4` | 48 |
| Vyjádření o ne/schválení | datum | `Vyjadreni__d8106` | 28 |
| Hypoteční smlouva | soubor | `Hypotecni__f694a` (jen číst) | 25 |
| Doplňující údaje | velké textové pole | ? (možná `ucel_62c65`, viz níže) | – |

`ucel_62c65` je víceřádkové textové pole s výplní „.“ nebo slovem účelu (6 OP). Odpovídá buď dnešním „Doplňujícím údajům“
s jiným popiskem, nebo starému textovému poli „účel“ `[k ověření v UI]`. Skill ho nevyplňuje.

**Obecné**

| Popisek | Typ | Klíč | Vyplněno |
|---|---|---|---|
| producent | roletka | `producent_6ef95` (banka, celé obchodní jméno) | 62 |
| číslo smlouvy | text, **povinné v UI** | `cislo_smlo_60eb1` (v datech i zástupné `xxx`) | 67 |
| číslo nabídky | text | ? | 0 |
| počátek | datum | `pocatek_5c097` | 1 |
| pojistné | číslo | ? | 0 |
| frekvence | roletka | ? | 0 |
| EPP 2 odesláno klientovi | datum | ? | 0 |
| Faktura vystavena | datum | `Faktura_vy_5d61f` (OP z 8–10/2026) | 10 |
| Číslo žádosti | text | ? | 0 |
| Tipař | roletka | ? (samostatné pole, ne `company.category`) | 0 |

**Provize**

| Popisek | Typ | Klíč | Vyplněno |
|---|---|---|---|
| Provize | roletka, **povinné v UI** | `Provize_dc7d2` | 64 |
| 1. provize | číslo | ? | 0 |
| vyplaceno | datum | ? | 0 |
| další provize | číslo | ? | 0 |

**Pojištění majetku a nemovitosti:** PČ nemovitost · PČ domácnost · PČ odpovědnost (čísla, klíče ?).
**Pojištění osob:** produkt (roletka, číselník prázdný) · konec pojištění (datum, klíč ?) · daňově uznatelné (zatržítko,
`danove_uzn_21bf3`, 2× `false` u hypoték, nejspíš omylem). Pojistné OP v CRM prakticky nejsou (kategorie 147, 119, 117 bez OP).

Kdo co plní (vzorek 12. 10. 2026): plnou sadu (smlouva, pojištění, fixace, splatnost, vyjádření) mají hlavně vyhrané OP
z 1–8/2026; rozpracované OP většinou jen Představení a Fakturu, 21 ze 119 nemá vyplněné nic. Historické OP typu „Provize“
(`businessCaseType` 188, Q1 2026, automatizace) mají jen producenta a číslo smlouvy, importy z Broker Trust jen `Provize = "BT"`
a číslo smlouvy.

### Hodnoty roletek

Přesné řetězce z Nastavení polí (k 2026-10-12). Zapisuj 1:1.

| Pole | Povolené hodnoty |
|---|---|
| vzdělání (`vzdelani_b79fe`) | `základní` · `střední` · `střední s maturitou` · `vyšší odborné` · `vysokoškolské` |
| rodinný stav (`rodinny_st_adceb`) | `svobodný / svobodná` · `ženatý / vdaná` · `rozvedený / rozvedená` · `vdovec / vdova` |
| Zúžení SJ (`Zuzeni_SJ_f0b36`) | `Ano` · `Ne` |
| hlavní běžný ú. (`hlavni_bez_5fef9`) | `ČSOB` · `KB` · `ČS` · `RB` · `Fio` · `Airbank` · `mBank` |
| Druh zaměstnání (`Druh_fcd16`) | `HPP` · `DPČ` · `DPP` |
| Svobodné povolání (`Svobodne_p_705f3`) | `Advokát` · `Auditor` · `Autorizovaný architekt` · `Autorizovaný inženýr` · `Daňový poradce` · `Exekutor` · `Finanční zprostředkovatel` · `Insolvenční správce` · `Lékárník` · `Notář` · `Odhadce` · `Patentový zástupce` · `Poradce v oblastni IT / programátor` (překlep je v číselníku) · `Praktický lékař a specialista` · `Právník` · `Profesionální sportovec` · `Správce konkurzní podstaty` · `Stomatolog` · `Účetní činnost` |
| Výše paušálu (`Vyse_pausa_4549e`) | `Bez paušálu` · `80 %` · `60 %` · `40 %` |
| Doba fixace (`Doba_fixac_172ca`) | `Bez fixu` · `1 rok` · `2 roky` · `3 roky` · `5 let` · `7 let` · `8 let` (slovně, přestože popisek říká „v měsících“) |
| Účel úvěru (`Ucel_uveru_47dd5`) | `neúčelový` · `koupě` · `výstavba/dostavba` · `rekonstrukce` · `refinancování` · `vypořádání` · `Americká Hypotéka` · `KTK`. ⚠️ V datech je 8× `(zajištěný) – neúčelový` a jen podle Nastavení polí `neúčelový`: volba se možná přejmenovala `[k ověření v UI]`; 1× `Rekonstrukce` s velkým R (mimo seznam) |
| Pojištění (`Pojisteni_1b7ae`) | `ANO` · `NE` · `ČSOB - Náš život` |
| frekvence (OP) | `měsíčně` · `kvartálně` · `ročně` |
| producent (`producent_6ef95`) | `Česká spořitelna, a.s.` · `ČSOB Hypoteční banka, a.s.` · `Komerční banka, a.s.` · `mBank S.A., organizační složka` · `Moneta Money Bank, a.s.` · `Modrá pyramida stavební spořitelna, a.s.` · `Oberbank AG pobočka Česká republika` · `Raiffeisenbank a.s.` · `Raiffeisen Stavební Spořitelna` · `Stavební spořitelna České spořitelny, a.s.` · `UniCredit Bank Czech Republic and Slovakia, a.s.` · `ČSOB Stavební Spořitelna` |
| Provize (`Provize_dc7d2`) | `Jednorázová` · `Postupná` · `Mimo BT (podnikatelský úvěr)`. Importy z BT mají `BT` (mimo seznam) |
| Tipař (OP) | jména tipařů a partnerů; seznam je v UI (Nastavení polí) a v Adamově vaultu, sem se kvůli veřejnému repozitáři nepíše. Není totožný s `companyCategory` |
| produkt (pojištění osob) | číselník prázdný, roletkou nejde vyplnit |

Producent, který v seznamu není (např. Partners Banka, leasingové společnosti, nebankovní věřitelé), do pole nepiš: uveď ho
v kartě OP a zeptej se, jestli má admin hodnotu do roletky přidat.

### Formáty hodnot

Ověřeno z reálných záznamů:

| Typ | Zápis |
|---|---|
| datum | `"2026-06-24"` (řetězec ISO, bez času) |
| číslo | `7280000` (bez mezer, bez „Kč“) |
| zatržítko | `true` / `false` |
| roletka | přesný text volby jako řetězec |
| text s číslem (`Soucasny_c_952ff`, `Budouci_5f2ff`) | `"27000"` (web ho píše i s mezerou `"27 000"`) |
| soubor | čtení `{"fileName", "id", "size"}`; zápis přes MCP nejde |

Příklad (hodnoty fiktivní):

```json
{ "id": <id OP>, "customFields": {
  "producent_6ef95": "Komerční banka, a.s.",
  "Provize_dc7d2": "Jednorázová",
  "vyse_uveru_ad8b6": 5000000,
  "Ucel_uveru_47dd5": "koupě",
  "Doba_fixac_172ca": "5 let",
  "Predstaven_47ad0": "2026-01-15",
  "Datum_podp_02aa4": "2026-01-20" } }
```

## Soubory a přílohy

| Co | Přes MCP | Jak |
|---|---|---|
| Pole typu **Soubor** (klient: DPFO, DPPO, výkazy, rozvahy, Přehled úvěrů; OP: Žádost, Hypoteční smlouva) | **jen číst** | `*_get` vrací `{fileName, id, size}`. Nahrát jde jen v UI do pole, případně REST API v2 (multipart; neověřeno, nutný API klíč z Nastavení » API klíče) |
| Obecná příloha klienta nebo OP | částečně | `attachmentLink` (+ `attachmentLinkName`) = odkaz na URL (sdílený soubor na Disku), **nebo** `attachmentFolderId` = složka z knihovny Dokumenty. Vzájemně se vylučují |
| Binární upload | ne | UI (drag & drop na kartu) nebo XLSX/CSV import |

**Pole typu Soubor jsou zdroj „co už máme“.** Vyplněné `DPFO_posle_46c18` znamená, že DPFO za poslední rok v CRM je; skill ho
po klientovi nechce znovu (`podklady.md`). Název souboru nemusí odpovídat poli (do pole se občas nahraje jiný doklad), proto
„✓ máme“ jen při názvu, který obsahu odpovídá, jinak „? nejasné“.

Postup u dokumentů z hovoru: co je k dispozici a co chybí, napiš do karty OP (`description`) nebo profilu klienta (`notice`);
soubor nahrává člověk v UI. Sdílený odkaz jde přidat přes `attachmentLink` (u OP až v `businessCase_update`).

## Vazby mezi entitami

Aktivita se dá při zakládání navázat rovnou na: `company`, `lead`, `project`,
`businessCase`, `offer`, `salesOrder`, plus `participants[]` (person / company / lead
s rolí `FROM` / `TO` / `CC` / `BCC`).

Ověřený řetězec z reálných dat:

```
company 599 ── businessCase 469 (OP-26-0462)
                 ├─ PhoneCall 30208  COMPLETED
                 ├─ Task      30209  COMPLETED
                 ├─ Task      30210  NEW
                 └─ Meeting   32195  COMPLETED
```

## Pasti, které nejsou vidět ze schématu

**Telefonát, schůzka ani událost nemají pole `person`.** CRM to strukturálně zakazuje.
Kontaktní osobu lze navázat jen přes `participants`. Úkol (`task`) pole `person` má.

**`status` přepisuje `completed`.** Při `→ COMPLETED` nebo `→ CANCELLED` se `completed`
nastaví na `scheduledTill` (nebo aktuální čas). Při `→ NEW` / `→ SCHEDULED` se vymaže.
Posílat `completed` a `status` v jednom volání znamená přijít o vlastní hodnotu.

**`participants` při update nahrazují celý seznam.** Účastník, jehož `id` v poli
nepošleš, je smazán. Před každou změnou načti `phonecall_get` a stávající zachovej.

**`tags` při update nahrazují celou hodnotu.** Zápis je jeden string, čtení pole
(`company_get`) nebo string (`company_list`) — počítej s obojím. `null` maže vše,
prázdný string ne.

**Prázdný string nemaže ani text.** `event_update` / `meeting_update` se `solution=""` pole nevyprázdní, náhled změnu
vůbec neukáže (ověřeno 12. 10. 2026).

**U vlastních polí je to naopak: `null` nebo prázdná hodnota v `customFields` pole smaže** (manuál 12. 10. 2026). Do
`customFields` proto posílej jen klíče, které opravdu měníš, nikdy celý objekt z `*_get` s prázdnými hodnotami.

**`addressName` je povinný u každého adresního nebo kontaktního pole klienta.** `company_update` jen s `phone` nebo `email`
bez `addressName` neprojde; v instanci se používá „Sídlo klienta“ (manuál 12. 10. 2026).

**Povinné v UI ≠ povinné v API.** Formulář vyžaduje u OP `source`, `category`, číslo smlouvy (`cislo_smlo_60eb1`) a typ provize
(`Provize_dc7d2`), u klienta Tel 1. MCP vyžaduje jen povinná pole z [Povinná pole při zakládání](#povinná-pole-při-zakládání).
Záznam založený přes MCP proto může při další ruční editaci v UI chtít doplnit tato pole `[k ověření]`.

**Roletka bere jen přesný text.** Jiný řetězec se uloží, ale v UI se nezobrazí jako vybraná volba (viz [Hodnoty roletek](#hodnoty-roletek)).

**Událost nezobrazuje Výsledek.** Zápis do `solution` Události je v UI neviditelný. Viz [Typy aktivit](#typy-aktivit).

**`phonecall_update` neumí změnit `owner`** — backend to pole na update ignoruje.

**`status=COMPLETED` při create nastaví `completed` na čas zápisu**, ne na `scheduledTill` (ověřeno 1. 10. 2026, telefonát 37590:
konec hovoru 18:05, `completed` 18:37). Oprava: hned potom `phonecall_update(completed=<konec hovoru>)` **bez** `status`,
ověřeno, že projde. Pro kontrolu duplicit proto ber `scheduledTill`, ne `completed`.

**Řešitel úkolu:** `resolverPerson` v `task_create` i `task_update` vrátí úspěch, ale řešitele nezmění. Funkční je přepsat osobu
u druhého účastníka v `participants` (zadavatel `owner: true, role: FROM`, řešitel druhý záznam). Viz vault `crm-raynet`,
„Práce přes MCP konektor“.

**Google kalendář je synchronizovaný obousměrně.** **Zrušení (`CANCELLED`) aktivity v Raynetu ji v Googlu smaže**, smazání
v Googlu ji smaže v Raynetu. „Hotovo“ se do Googlu nepropíše (nápověda A/203015978). Skill schůzky nikdy neruší, jen dokončuje.

**Pozvánky** na schůzky založené přes API/MCP se klientovi neodesílají. Pozvánku posílá jen ruční akce v UI.

**Zápis běží na dva kroky.** První volání vrátí náhled a `confirmToken`, druhé se
stejnými argumenty plus tokenem provede zápis. Token platí **60 sekund** a nikdy
se nevymýšlí. Ověřeno při ostrých zápisech od 1. 10. 2026.

**`businessCase_pipelineAnalysis` vyžaduje `businessCaseType`** — bez něj vrátí
chybu „Filtr neobsahuje povinný atribut Typ obchodu".

## Hledání a filtry

**Klienti jsou `company` záznamy** — z ~94 % fyzické osoby (odhad ze vzorku n=136).

**Flag `person` je nespolehlivý.** Odhadem ~80 záznamů jsou fyzické osoby s
`person: false` a prázdným `firstName`/`lastName` — vznikají z leadů, webových
formulářů a Simpleshopu. Jeden z nich má v `notice` přímo poznámku „Fyzická osoba –
přepnout typ v Raynetu". Na rozlišení typu použij regex na `name`
(`s.r.o.`, `a.s.`, `spol. s r.o.`, `o.p.s.`, `z.s.`), ne tenhle flag.

**`legalForm` je mrtvé pole** — číselník má 9 položek, ale vyplněné je u jediného
záznamu v celé bázi. Jako indikátor typu nepoužitelné.

**Identifikátory nejsou unikátní:**

- `email` — pokrytí ~97 %, ale sdílí ho majitel se svojí s.r.o., manželé, a v jednom
  ověřeném případě dva různí lidé (stejné příjmení, jiné křestní jméno).
- `regNumber` — jen u 29 % fyzických osob, duplicitní (`21697728` na dvou záznamech)
  a obsahuje nesmysly jako `"0"`, `"4"`, `"6"`.

Proto se páruje **e-mail + příjmení**, ne jedním klíčem.

**`name` filtr rozlišuje diakritiku.** Je to substring bez ohledu na velikost písmen,
ale příjmení bez háčku nenajde klienta, který ho má s háčkem (ověřeno na skutečném klientovi: dotaz vrátil jen jeho
firmu, zapsanou bez diakritiky; ilustračně `Capek` nenajde `Milan Čápek`, jen `Capek Invest s.r.o.`). Na hledání podle jména z přepisu proto použij
`scripts/match_name.py variants`, který generuje i varianty s háčkem a bez něj.

**Cizí jména bývají zapsaná foneticky.** Klient, kterého uživatel zná v německém pravopisu (ilustračně `Schneider`),
je v CRM zapsaný foneticky (`Šnajdr`). Přímé hledání originálního pravopisu nenajde nic a prefix originálu (`Sch`) také ne.
`scripts/match_name.py variants` proto přidá i český fonetický přepis (`Šnajder` → prefix `Šna`), který zápis najde.

**`fulltext`** matchuje celá slova a prefixy, **ne libovolný substring**. Číselné
tokeny funguje (test `"2856"` → 2 zásahy). Zásah může přijít z nečekaného pole.
Na konkrétní pole je spolehlivější `name`, `email`, `regNumber`.

**`companyId` / `personId` / `leadId` v `*_list` filtrují podle účastníka**, ne jen
podle primární vazby — záběr je širší, než by se čekalo, a je to správně.

**`scheduledFrom` / `scheduledTill` v `*_list` jsou okno s překryvem**, ne vlastní
hodnoty záznamu. Match = `záznam.scheduledFrom <= konec okna AND záznam.scheduledTill >= začátek okna`.

⚠️ **Ručně zapsaná aktivita má často `scheduledFrom: null`** a vyplněné jen
`completed`. Časové okno na `scheduledFrom` takový záznam **nikdy nevrátí**, ať je
jakkoli široké. Ověřeno na PhoneCall 35927 (`scheduledFrom: null`,
`completed: "2026-09-22 12:48"`). Na hledání „co vzniklo daný den" použij
`createdFrom` / `createdTill`, ne `scheduledFrom`.

⚠️ **Hovor nemusí být uložený jako `PhoneCall`.** V praxi se zapisuje i jako `Event`
nebo `Meeting` (ověřeno na Event 36006 — telefonát s klientem uložený jako událost).
Dotaz `phonecall_list` takový záznam nevrátí. Na kontrolu, jestli už je hovor
zapsaný, používej **`activity_list`** napříč subtypy.

**`tags` filtr je levné počítadlo** — `totalCount` respektuje filtr, takže velikost
libovolné podmnožiny zjistíš jedním requestem bez stahování dat.
Tagy se reálně používají: 450 záznamů nese `Broker Trust`.

**Limit stránky je 50** u všech `*_list`, stránkuje se přes `offset`.

## Co MCP neumí

- ❌ **Založit fyzickou osobu** — `company_create` vytvoří vždy organizaci.
  U ~94 % klientské báze to znamená, že nový klient je ruční krok v Raynet UI (nebo lead přes `lead_create`).
  REST API to umí (`PUT /company/` s `person=true`, `firstName`, `lastName`), MCP ne.
- ❌ **Externí ID** (`extIds`, až 10 na záznam, např. `pocket:<recordingId>`) — umí jen REST API (`/{entity}/{id}/extId/`).
  Byl by to nejspolehlivější klíč proti duplicitám, přes MCP zatím nejde.
- ❌ **Založit e-mail nebo dopis jako aktivitu.** Číst je jde (od 10/2026): `email_list` a `letter_list` vrací
  přehled bez těla, `email_get` a `letter_get` detail s tělem. `email_list` u e-mailů přijatých nebo odeslaných přes
  CRM inbox vrací i `from` a `recipients` (u IMAP importů jsou prázdné) a filtruje podle `completedFrom`/`completedTill`,
  takže najde i přijaté e-maily, které nemají plánovaný čas. Přílohy nástroje nevracejí.
- ❌ **Generický `activity_get`** — detail se čte podle subtypu.
- ❌ **Změnit typ aktivity** (Událost → Schůzka) — jen ručně v UI, převod vytvoří nový záznam s novým id.
- ❌ **Nahrát binární přílohu ani vyplnit pole typu Soubor** — jen `attachmentLink` (URL) nebo `attachmentFolderId`;
  pole typu Soubor jde jen číst (viz [Soubory a přílohy](#soubory-a-přílohy)).
- ❌ **Zjistit definice vlastních polí** — klíč je vidět jen u vyplněného záznamu (viz [Vlastní pole](#vlastní-pole)).
- ❌ **Smazat cokoli** — žádný `delete` nástroj. Zápis je nevratný.
- ❌ **Nastavit `businessCase.status` přímo** — jen přes `businessCasePhase`.
- ❌ **Lookup pro `owner` a `securityLevel`** — id se musí znát.
