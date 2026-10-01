# Raynet — referenční přehled

Ověřeno na instanci `evergreen` dne 21. 9. 2026 čtením reálných dat.
Plný audit: `docs/AUDIT-POCKET-RAYNET.md` v repozitáři.

## Obsah

- [Konstanty](#konstanty)
- [Stavy aktivit](#stavy-aktivit)
- [Fáze obchodního případu](#fáze-obchodního-případu)
- [Kategorie aktivit](#kategorie-aktivit)
- [Povinná pole při zakládání](#povinná-pole-při-zakládání)
- [Vlastní pole](#vlastní-pole)
- [Vazby mezi entitami](#vazby-mezi-entitami)
- [Pasti, které nejsou vidět ze schématu](#pasti-které-nejsou-vidět-ze-schématu)
- [Hledání a filtry](#hledání-a-filtry)
- [Co MCP neumí](#co-mcp-neumí)

## Konstanty

| Co | Hodnota |
|---|---|
| Vlastník (`owner`) | **zjistit za běhu**: `user_info` → `username` → `person_list(email=…)` → `id` (Adam = 2) |
| Uživatelé (id osoby) | Adam Pospíšil 2 · Michal Čakovský 9 · Eva Hofmanová 13 · Kateřina Háblová 21 · Martin Fiedor 42 (k 2026-10-01; další přes `person_list`) |
| `securityLevel` „Sdílená" | 1 |
| Jediný `businessCaseType` — „Úvěrový proces" | 64 |
| Měna Kč (`currency`) | 40 |
| Rate limit | 24 000 req/den; `rate_limit_status` se nepočítá |
| Formát data pro API | `yyyy-MM-dd HH:mm` nebo ISO 8601 **s milisekundami** |

Formát ISO bez milisekund je odmítnut. `2026-01-01T12:00:00+01:00` neprojde,
`2026-01-01T12:00:00.000+01:00` ano.

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

| id | Fáze |
|---|---|
| 10 | Identifikace požadavku |
| 1 | Nabídnuto |
| 2 | Podaná žádost + EPP 2.0 |
| 3 | Kompletace dokumentů + odhad |
| 7 | Čeká na schválení |
| 11 | Schváleno |
| 8 | Podepsáno |

Uzavřené fáze (dohledány na reálných OP):

| id | Fáze | Odvozený `status` |
|---|---|---|
| 4 | Výhra | `E_WIN` |
| 5 | Prohra | `F_LOST` |
| 6 | Zrušeno | `G_STORNO` |

Platná id celkem: 1–8, 10–14. Názvy 12, 13, 14 zůstávají neověřené. Neplatné id vrátí
chybu, která vyjmenuje platná — toho se dá využít místo hádání.

**Případy se jmenují podle banky a produktu**, ne podle klienta — „Moneta SBL",
„Podnikatelský úvěr Moneta – nemovitost 2–3 mil. Kč". Stejný název se opakuje
u různých klientů (11 OP s „Moneta" v názvu napříč různými firmami), takže název
sám o sobě klienta neurčuje.

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

## Vlastní pole

MCP **nevrací definice** vlastních polí, klíč (`název_hash`) je vidět jen u záznamu, kde je pole vyplněné. Seznam polí je v UI
v Nastavení » Vlastní pole, přes REST v `GET /api/v2/customField/config/`. Průzkum instance k 2026-10-01 (69 OP, 50 klientů,
30 leadů, 80 aktivit):

**Klient (`company`)**, vyplněno u 18 % klientů, hlavně z webového formuláře /analyza-portfolia:

| Klíč | Obsah | Typ |
|---|---|---|
| `Pocet_deti_cf874` | počet dětí | celé číslo |
| `zamestnava_ffa65` | zaměstnavatel | text |
| `pracovni_p_f7e4d` | pracovní pozice | text |
| `Najmy_v_DP_bb662` | nájmy v daňovém přiznání | ano/ne |
| `Soucasny_c_952ff` | současný čistý nájem | **text** (číslo jako řetězec) |
| `DPFO_posle_46c18`, `DPFO_predp_6db0e` | DPFO za poslední a předposlední rok | soubor (MCP nenahraje) |
| `Rodne_cisl_ed0da` | rodné číslo | text, **skill nevyplňuje** |
| `Zadatel_v__a594e`, `Alternativ_b3c97` | význam nejasný | ano/ne, nevyplňovat |

**Obchodní případ.** Skill pole OP **nemění** (Adam, 1. 10. 2026: jen návrh posunu fáze), ale čte je pro kartu OP a bonitu:
`producent_6ef95` (banka, celé obchodní jméno), `vyse_uveru_ad8b6`, `Ucel_uveru_47dd5`, `Hodnota_za_21c14` (hodnota zajištění),
`Splatnost_7586b` (měsíce), `konec_fixa_65281`, `urokova_sa_51229`, `LTV_eedee`, `Provize_dc7d2`, `cislo_smlo_60eb1`,
`Predstaven_47ad0` (datum nabídky, plní ho workflow při fázi „Nabídnuto“), `Datum_podp_02aa4`, `Vyjadreni__d8106` (schválení).

**Lead a aktivity:** vlastní pole ve vzorku nevyplněná. Web všechno píše do `notice`.

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
se nevymýšlí. (Mechanismus je doložen ze schémat, empiricky neověřen.)

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
  ověřeném případě dva různí lidé (`simkrom@seznam.cz` = Jiří i Jan Šimek).
- `regNumber` — jen u 29 % fyzických osob, duplicitní (`21697728` na dvou záznamech)
  a obsahuje nesmysly jako `"0"`, `"4"`, `"6"`.

Proto se páruje **e-mail + příjmení**, ne jedním klíčem.

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
- ❌ **Založit e-mail nebo dopis jako aktivitu.** Feed `activity_list` je vrací
  (`_entityName: "Email"`), ale `email_*` ani `letter_*` nástroje neexistují
  a `entityType` připouští jen `task`, `meeting`, `event`, `phonecall`.
- ❌ **Generický `activity_get`** — detail se čte podle subtypu.
- ❌ **Nahrát binární přílohu** — jen `attachmentLink` (URL) nebo `attachmentFolderId`.
- ❌ **Smazat cokoli** — žádný `delete` nástroj. Zápis je nevratný.
- ❌ **Nastavit `businessCase.status` přímo** — jen přes `businessCasePhase`.
- ❌ **Lookup pro `owner` a `securityLevel`** — id se musí znát.
