# Raynet — referenční přehled

Ověřeno na instanci `evergreen` dne 21. 9. 2026 čtením reálných dat.
Plný audit: `docs/AUDIT-POCKET-RAYNET.md` v repozitáři.

## Obsah

- [Konstanty](#konstanty)
- [Stavy aktivit](#stavy-aktivit)
- [Fáze obchodního případu](#fáze-obchodního-případu)
- [Kategorie aktivit](#kategorie-aktivit)
- [Povinná pole při zakládání](#povinná-pole-při-zakládání)
- [Vazby mezi entitami](#vazby-mezi-entitami)
- [Pasti, které nejsou vidět ze schématu](#pasti-které-nejsou-vidět-ze-schématu)
- [Hledání a filtry](#hledání-a-filtry)
- [Co MCP neumí](#co-mcp-neumí)

## Konstanty

| Co | Hodnota |
|---|---|
| Adam Pospíšil — `owner` / user id | **2** |
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

Platná id celkem: 1–8, 10–14. Názvy 4, 5, 6, 12, 13, 14 neověřeny (nejsou v otevřené
pipeline, pravděpodobně uzavřené stavy). Neplatné id vrátí chybu, která vyjmenuje
platná — toho se dá využít místo hádání.

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

`owner` nemá default a neexistuje pro něj lookup nástroj — je to vždy **2**.

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

**`tags` filtr je levné počítadlo** — `totalCount` respektuje filtr, takže velikost
libovolné podmnožiny zjistíš jedním requestem bez stahování dat.
Tagy se reálně používají: 450 záznamů nese `Broker Trust`.

**Limit stránky je 50** u všech `*_list`, stránkuje se přes `offset`.

## Co MCP neumí

- ❌ **Založit fyzickou osobu** — `company_create` vytvoří vždy organizaci.
  U ~94 % klientské báze to znamená, že nový klient je vždy ruční krok v Raynet UI.
- ❌ **Založit e-mail nebo dopis jako aktivitu.** Feed `activity_list` je vrací
  (`_entityName: "Email"`), ale `email_*` ani `letter_*` nástroje neexistují
  a `entityType` připouští jen `task`, `meeting`, `event`, `phonecall`.
- ❌ **Generický `activity_get`** — detail se čte podle subtypu.
- ❌ **Nahrát binární přílohu** — jen `attachmentLink` (URL) nebo `attachmentFolderId`.
- ❌ **Smazat cokoli** — žádný `delete` nástroj. Zápis je nevratný.
- ❌ **Nastavit `businessCase.status` přímo** — jen přes `businessCasePhase`.
- ❌ **Lookup pro `owner` a `securityLevel`** — id se musí znát.
