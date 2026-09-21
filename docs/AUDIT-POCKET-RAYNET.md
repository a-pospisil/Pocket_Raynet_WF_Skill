# AUDIT MCP: Hey Pocket + Raynet

**Datum auditu:** 21. 9. 2026
**Rozsah:** technický a funkční audit MCP nástrojů skutečně dostupných v relaci
**Režim:** READ-ONLY — do Raynetu ani Pocketu nebyl proveden žádný zápis

## Prostředí (ověřeno)

| Systém | Hodnota |
|---|---|
| Pocket účet | `adam.pospisil@egfin.cz`, plán **pro**, userId `YfCtPkCSuWOVnbQ17GjKwkJfTAF3` |
| Raynet instance | `evergreen`, id `c6372ff4e24448e9b72ff4e24418e9b8` |
| Raynet rate limit | 24 000 req/den, čerpáno 365, zbývá 23 635 |
| Raynet locale | `cs_CZ`, datum `d.M.yyyy`, čas `H:mm` |
| **Adam Pospíšil = owner id `2`** | ověřeno přes `offer_list.owner` + `person_list` |

> **Poznámka k zápisu:** všechny Raynet `*_create` / `*_update` nástroje jsou v této relaci blokovány permission gate (`External System Writes`). Pokus o volání `phonecall_create` byl odmítnut ještě před odesláním do Raynetu. Read-only charakter auditu je tím technicky vynucen, ne jen deklarován.

---

## A. AVAILABLE POCKET TOOLS

| Tool | R/W | Účel | Parametry | Výstup | Využijeme |
|---|---|---|---|---|---|
| `get_account_info` | R | Identita účtu, plán | — | displayName, email, plan, tier, userId | Ne (jen health-check) |
| `list_pocket_folders` | R | Složky / spaces | — | folders[] (id, name, kind, parent, counts) | **Ne — 0 složek** |
| `search_pocket_conversations` | R | Hledání nahrávek, 2 režimy | `query?`, `folderIds?`, `recordingDateAfter?`, `recordingDateBefore?`, `recordingDateBeforeExclusive?`, `tags?` | viz níže | **ANO — hlavní vstup** |
| `get_pocket_conversation` | R | Detail: Summary + audio | `recording_ids[]` | recordingId, recordingTitle, recordingDate, recordingTags[], transcriptSegments[], **summary{markdown,version}**, **audioUrl{}** | **ANO — zdroj obsahu** |
| `search_pocket_actionitems` | R | Action items | `query?`, `actionType?`, `status?`, `priority?`, `dueAfter?`, `dueBefore?`, `recordingDateFrom?`, `recordingDateTo?` | actions[] + limit/total | **ANO — follow-up aktivity** |
| `update_pocket_actionitem` | **W** | Změna stavu/termínu/priority | `actionItemId` + `label?`,`context?`,`status?`,`priority?`,`dueDate?`,`assignee?` | — (netestováno) | ANO — uzavření smyčky |
| `query_pocket_meetings` | R | NL dotaz nad nahrávkami | `query`, `language?` | syntetizovaná odpověď + zdrojová recording ids | **NETESTOVÁNO** |

### Režimy `search_pocket_conversations`

**Recency mode** (bez `query`) — vrací plné přepisy, nejnovější první:
```
data.limit, data.total, data.recordings[], data.meta{
  hasMore, matchedCount, remainingCount, returnedCount,
  pageSize, oldestReturnedRecordingDate, nextRecordingDateBeforeExclusive }
```
Pole nahrávky: `content` (plný přepis, prefix „Speaker N:"), `contentSnippet` (500 zn.), `documents[]`, `language`, `recordingDate`, `recordingId`, `recordingTitle`, `relevanceScore` (0), `transcriptSegments[{text,start,end,speaker}]`, `transcriptionId`.

- **`pageSize` je pevně 5.** Stránkuje se přes `recordingDateBeforeExclusive = meta.nextRecordingDateBeforeExclusive`.
- Test: `recordingDateAfter=2026-09-15` → `matchedCount: 48`, vráceno 5.
- **Neobsahuje:** Summary, action items, audio, tagy.

**Query mode** (se `query`) — sekční hybridní hledání. **Jiný tvar odpovědi:**
```
data{ queryUsed, recordings[], timing, total }   // žádné meta, žádné stránkování
```
Navíc pole: `metadata{matchType, source}`, `sectionStartMs`, `sectionEndMs`, `sectionSummary`, `sectionTitle`, `speakers` (**string**, např. `"SPEAKER_00, SPEAKER_01"`).

⚠️ **Dvě zásadní zjištění:**
1. **Vrací duplicitní řádky téže nahrávky.** Test: 8 řádků = **4 unikátní** `recordingId` (jedno ID 4×, se shodným skóre i sekcí). Nutná deduplikace podle `recordingId`.
2. **Sémantické hledání není spolehlivé pro hledání podle jména klienta.** Dotaz „Peter Balent financování pozemku na Slovensku" **nenašel** nahrávku s názvem `Konzultace a výpočet [Peter Balent]`. Všechny zásahy se vrátily s `matchType: "bm25"` (keyword), nikoli vektorově.

### Struktura `summary.markdown`

Markdown **s proprietárními pseudo-tagy Pocketu**, které je nutné před zápisem do Raynetu odstranit nebo převést:
```
<pocket:chart type="bar" title="...">popisek | hodnota</pocket:chart>
<pocket:decision-tree title="...">uzel::otázka …</pocket:decision-tree>
```

### Action items — tvar a limity

Pole: `actionItemId` (UUID), `actionType` (`create_reminder` | `draft_email` | `send_message`), `assignee` (`me` | `Other`), `context`, `dueDate` (ISO nebo `null`), `label`, `payload` (typovaný: `reminder{title,dueDateTime}` / `email{subject,body,to}` / `message{body}`), `priority`, `recordingDate`, `recordingId`, `recordingTitle`, `status` (`TODO` | `COMPLETED`).

⚠️ **Limity:**
- **Strop 50 položek, `offset` neexistuje** → nelze stránkovat přes 50. Test vrátil `total: 50, limit: 50` (uříznuto). Nutno filtrovat přes `recordingDateFrom/To` nebo `status`.
- **Asymetrie priority:** čtení vrací **malá písmena** (`high`, `medium`, `low`), zápis vyžaduje **velká** (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- Každý action item nese `recordingId` → lze je spolehlivě navázat na zdrojovou nahrávku.

---

## B. AVAILABLE RAYNET TOOLS

### Klient (company)

| Tool | R/W | Parametry (výběr) | Poznámka |
|---|---|---|---|
| `company_list` | R | `name`, `fulltext`, `email`, `regNumber`, `taxNumber`, `city`, `ownerId`, `tags`, `category`, `createdFrom/Till`, `updatedFrom/Till`, `limit≤50`, `offset` | **Hlavní nástroj pro hledání klienta i kontrolu duplicit** |
| `company_get` | R | `id` | Plný detail vč. všech adres, `customFields`, `tags`, `attachments` |
| `company_create` | **W** | **povinné:** `name`, `rating`, `state`, `role` | Nevytvoří person-type záznam; bez loga a příloh |
| `company_update` | **W** | `id` + libovolná pole (partial) | Umí přílohu jen jako URL/odkaz na složku |

**Ověřeno na datech:** klienti jsou `company` záznamy s `person: true` (`firstName`/`lastName` vyplněné). Celkem **1050** firem.

### Aktivity

| Tool | R/W | Poznámka |
|---|---|---|
| `activity_list` | R | Smíšený feed; `entityType` ∈ {`event`,`meeting`,`phonecall`,`task`}; filtry `companyId`, `personId`, `leadId`, `businessCaseId`, `status`, `category`, `scheduledFrom/Till`, `tags`, `fulltext`, `ownerId` |
| `phonecall_list` / `_get` / `_create` / `_update` | R/R/W/W | `create` **povinné:** `title`, `owner` |
| `task_list` / `_get` / `_create` / `_update` | R/R/W/W | `create` **povinné:** `title`, `deadline`, `owner` + alespoň jedno z `personal=true`/`person`/`company`/`lead` |
| `meeting_list` / `_get` / `_create` / `_update` | R/R/W/W | `create` **povinné:** `title`, `owner`; navíc `meetingPlace` + adresa |
| `event_list` / `_get` / `_create` / `_update` | R/R/W/W | stejné jako meeting |
| `activity_completedActivityAnalysis` | R | Počty realizovaných aktivit per zaměstnanec |

⚠️ **`activity_list` vrací i `_entityName: "Email"`**, ačkoliv `entityType` tuto hodnotu nepřipouští a **žádný `email_*` ani `letter_*` nástroj neexistuje**. Stejně tak `activity_completedActivityAnalysis` zná typy `Email` a `Letter`. → **E-maily a dopisy lze číst ve feedu, ale nelze je přes MCP zakládat ani načítat detailem.**

### Obchodní případy

| Tool | R/W | Poznámka |
|---|---|---|
| `businessCase_list` | R | `companyId`, `status`, `businessCasePhase`, `businessCaseType`, `code`, `name`, `validFrom*`, `scheduledEnd*`, `tags`, `fulltext` |
| `businessCase_get` | R | Plný detail vč. položek, příloh, `customFields` |
| `businessCase_create` | **W** | **povinné:** `name`, `company`. **`status` nelze nastavit** — odvozuje se z `businessCasePhase` |
| `businessCase_update` | **W** | Změna fáze = změna stavu |
| 12× `businessCase_*Analysis` | R | pipeline, ABC, forecast, profitability, stateAnalysis, … |

### Ostatní entity

| Entita | Nástroje | Stav v instanci |
|---|---|---|
| Kontaktní osoby | `person_list/_get/_create/_update` | Používá se (interní tým i kontakty) |
| Leady | `lead_list/_get/_create/_update/_convert` | **30 aktivních** — používá se pro follow-up |
| Nabídky | `offer_list/_get/_create/_update` | **2 záznamy** — prakticky nepoužívá |
| Projekty | `project_list/_get/_create/_update` | **1 záznam (zrušený)** — nepoužívá |
| Objednávky | `salesOrder_list/_get/_create/_update` | **0 záznamů** — nepoužívá |
| Přílohy | jen jako `attachmentLink` (URL) nebo `attachmentFolderId` | **Binární upload nelze** |
| Vlastní pole | `customFields` u všech entit | **Žádné definované — `{}` všude** |
| Štítky | `tags` (zápis = string, čtení = pole) | **Prázdné u všech vzorků** |
| Kategorie | `raynet://codelist/{entity}` | Viz níže |

### Číselníky a enumerace (ověřeno)

**`EActivityStatus`** — klíč pro sekci 7:

| key | caption |
|---|---|
| `NEW` | Nenaplánován |
| `SCHEDULED` | **Naplánován** |
| `COMPLETED` | **Realizován** |
| `CANCELLED` | **Zrušen** |

**`EDocumentBaseStatus`** (OP): `B_ACTIVE`=Aktivní(otevřený), `E_WIN`=Akceptována, `F_LOST`=Zamítnuto, `G_STORNO`=Zrušeno.

**Fáze OP** (`businessCaseType` 64 „Úvěrový proces", otevřené; 85 OP / 764 153 618 Kč):

| id | Fáze | Počet | avgAge |
|---|---|---|---|
| 10 | Identifikace požadavku | 33 | 19 d |
| 1 | Nabídnuto | 17 | 17 d |
| 2 | Podaná žádost + EPP 2.0 | 9 | 23 d |
| 3 | Kompletace dokumentů + odhad | 6 | 22 d |
| 7 | Čeká na schválení | 12 | 17 d |
| 11 | Schváleno | 7 | 11 d |
| 8 | Podepsáno | 1 | 0 d |

Platná id fází celkem: `1,2,3,4,5,6,7,8,10,11,12,13,14`. Názvy id **4, 5, 6, 12, 13, 14** = **NEOVĚŘENO** (nejsou v otevřené pipeline — pravděpodobně uzavřené stavy).

**`activityCategory`:** 111 prioritní · 110 dohodnuto napevno · 183 Předběžný termín · 151 výroční schůzka · 152 zpracování administrativy · 112 soukromá aktivita · 154 Nepotvrzeno · 181 Vypracování nabídky

**`businessCaseType`:** jediný — **64 „Úvěrový proces"**. `businessCase_pipelineAnalysis` jej **vyžaduje** jako povinný filtr.

**`securityLevel`:** id `1` = „Sdílená" (jediné pozorované).

**`EActivityPriority`:** ⚠️ **v resource `raynet://enumerations` CHYBÍ**, ačkoli se na něj popisy nástrojů odvolávají. V reálných datech pozorováno `DEFAULT` a `CRITICAL`. `ELeadPriority` = `MINOR`/`DEFAULT`/`CRITICAL`. Shodnost obou enumerací = **NEOVĚŘENO**.

---

## C. ENTITY MAP — Pocket → Raynet

```
Pocket recording                    Raynet
─────────────────────────────────────────────────────────────────────
recordingId              ─────────▶ (žádné nativní pole) → idempotenční klíč
recordingTitle           ─────────▶ phonecall.title
recordingDate (search)   ─────────▶ phonecall.scheduledFrom      ← ZAČÁTEK
recordingDate (get)      ─────────▶ phonecall.scheduledTill      ← KONEC
transcriptSegments[]     ─────────▶ phonecall.description (HTML)
summary.markdown         ─────────▶ phonecall.solution (HTML, po převodu)
speakers                 ─────────▶ phonecall.participants  (nespolehlivé)
audioUrl.signed_url      ─────────▶ attachmentLink  (expiruje za 3600 s!)
recordingTags[]          ─────────▶ phonecall.tags
─────────────────────────────────────────────────────────────────────
action item (create_reminder) ────▶ task_create / phonecall_create SCHEDULED
action item (draft_email)     ────▶ ✗ nelze (email_create neexistuje) → task
action item (send_message)    ────▶ ✗ nelze → task
actionItemId             ─────────▶ idempotenční klíč follow-upu
dueDate                  ─────────▶ task.deadline / phonecall.scheduledFrom
priority (low/med/high)  ─────────▶ MINOR / DEFAULT / CRITICAL (NEOVĚŘENO)
```

### ⚠️ Nekonzistence `recordingDate` — ověřeno měřením

Tentýž `recordingId` vrací **různé datum** podle nástroje:

| recordingId | `search_*` | `get_pocket_conversation` | Δ | Délka přepisu |
|---|---|---|---|---|
| `36d473d6-…` | 13:48:28.000Z | 13:57:32Z | +9:04 | 494 s (8:14) |
| `desktop_1789996938017_u1rl1v` | 13:22:18.017Z | 13:37:36Z | +15:18 | 911 s (15:11) |

**Závěr:** `search_*` vrací **začátek** nahrávky, `get_pocket_conversation` **konec**. Rozdíl ≈ délka hovoru. Pro `scheduledFrom` používat hodnotu ze `search_*`, pro `scheduledTill` hodnotu z `get_*`.

Potvrzeno i formátem desktopového id: `desktop_**1789996938017**_u1rl1v` → epoch ms = `2026-09-21T13:22:18.017Z` = přesně hodnota ze `search_*`.

---

## D. IDENTIFICATION STRATEGY

### Identifikátory

| Systém | ID | Formát | Stabilní |
|---|---|---|---|
| Pocket | `recordingId` | UUID **nebo** `desktop_<epochMs>_<rand>` | ✅ |
| Pocket | `transcriptionId` | 32 hex bez pomlček | ✅ |
| Pocket | `actionItemId` | UUID | ✅ |
| Pocket | `folderId` | — | **0 složek** |
| Pocket | `tagId` | ✗ neexistuje — jen názvy (`tags: string[]`) | — |
| Raynet | `clientId` (company) | int | ✅ |
| Raynet | `contactPersonId` | int | ✅ |
| Raynet | `activityId` | int (per subtyp) | ✅ |
| Raynet | `businessCaseId` | int + `code` `OP-26-0462` | ✅ |
| Raynet | `leadId` | int + `code` `L-26-289` | ✅ |
| Raynet | `ownerId` / user | int — **Adam = 2** | ✅ |

### Identifikace klienta — doporučené pořadí

1. **`company_list(email=…)`** — nejsilnější signál, pokud e-mail z hovoru známe.
2. **`company_list(regNumber=…)`** — exact match, pro OSVČ/firmy.
3. **`company_list(name="Příjmení")`** — case-insensitive **substring**, spolehlivější než fulltext.
4. **`company_list(fulltext=…)`** — pouze celá slova / prefixy, **ne libovolný substring**; zásah může přijít z nečekaného pole.
5. Pokud 0 zásahů → zkusit **`lead_list`** (30 aktivních leadů; nový zájemce bývá nejdřív lead).

⚠️ **Ověřený problém s přepisem jmen:** Pocket přepisuje totéž jméno různě — `Balint` / `Balent` / `Balent Peter`, `Hasová` / `Hasolová`, `Pejro` / `Pejřil` / `Pejza`. `fulltext="Hasová"` vrátil **0 zásahů**, přestože klientka v hovorech figuruje. **Název z Pocketu nelze použít jako vyhledávací klíč napřímo.**

### Nalezení aktivity / OP

- Aktivity klienta: `activity_list(companyId=…)` — `companyId` filtruje podle **účastníka**, ne jen primární vazby (širší záběr, správné chování).
- Konkrétní telefonát v čase: `phonecall_list(companyId=…, scheduledFrom=…, scheduledTill=…)` — pozor, jde o **overlap okna**, ne přesnou shodu.
- OP klienta: `businessCase_list(companyId=…, status="B_ACTIVE")` → otevřené OP.
- Detail OP: `businessCase_get(id)`.

### Ověřený referenční řetězec (klient id 599)

```
company 599 ──┬─ businessCase 469 (OP-26-0462, fáze 10, 9 000 000 Kč, prob. 60 %)
              │       ├─ PhoneCall 30208  COMPLETED  completed=2026-09-18 11:25
              │       ├─ Task      30209  COMPLETED  deadline=2026-09-23 12:00
              │       ├─ Task      30210  NEW        deadline=2026-09-25 12:00
              │       └─ Meeting   32195  COMPLETED  meetingPlace=Google Meet
              ├─ PhoneCall 29304 COMPLETED (bez vazby na OP)
              └─ Email 30216 / 35683 / 35685  ← čitelné, ale přes MCP nezaložitelné
```
Celkem 12 aktivit. Vazba `aktivita → OP` i `OP → klient` je **ověřeně funkční**.

---

## E. DUPLICITY — „Byla tato nahrávka už zpracována?"

### Vyhodnocení kandidátů na idempotenční klíč

| Kanál | Zápis | Čtení / filtr | Verdikt |
|---|---|---|---|
| `customFields` | ✅ API podporuje | ✅ v `*_get` | ⚠️ **V instanci nejsou definována žádná** (`{}` u company, phonecall, task, meeting, businessCase). Popisy nástrojů varují „reuse exact keys… rather than inventing names" → **vyžaduje založení pole v Raynet UI**. Nejčistší řešení, ale až po ruční přípravě. |
| `tags` | ✅ string | ✅ `tags=` filtr (OR, comma-sep.) | ⚠️ Zápis **přepisuje celou hodnotu** (ne aditivní). Zda lze založit nový název tagu přes API = **NEOVĚŘENO**. |
| `description` / `solution` marker | ✅ HTML | ⚠️ `fulltext` = celá slova/prefixy | UUID s pomlčkami se pravděpodobně tokenizuje; dohledatelnost celého UUID = **NEOVĚŘENO**. Číselné tokeny fungují (test `fulltext="2856"` → 2 zásahy). |
| **Kompozitní dotaz** `companyId` + `scheduledFrom` | — | ✅ `phonecall_list` | ✅ **Funguje dnes, bez úprav Raynetu** |

### Doporučený idempotenční mechanismus (3 vrstvy)

**Vrstva 1 — primární, funguje okamžitě:**
```
phonecall_list(companyId=<id>, scheduledFrom=<start−2min>, scheduledTill=<start+2min>)
```
Existuje-li telefonát překrývající se s časem nahrávky → **nahrávka už zpracována, přeskočit**. Čas nahrávky je přesný na sekundy a z Pocketu nepřepisovatelný → velmi silný klíč.

**Vrstva 2 — viditelná stopa pro člověka i pro kontrolu:**
Do `description` vkládat na konec deterministický řádek:
```html
<p>— Zdroj: Pocket recording 36d473d6-c7c5-46fc-8d55-1211085af00c —</p>
```
Slouží k auditu a ručnímu dohledání; **ne** jako jediný dedup mechanismus.

**Vrstva 3 — lokální ledger (doporučeno):**
Soubor `state/processed.json` v repozitáři skillu: `recordingId → {activityId, businessCaseId, companyId, processedAt}`. Jediný 100% spolehlivý zdroj pravdy nezávislý na indexaci Raynetu.

**Vrstva 4 — cílový stav (po přípravě v Raynet UI):**
Založit custom field `pocket_recording_id` u aktivity → pak `customFields` jako nativní klíč. **Vyžaduje ruční krok mimo MCP.**

> Pro action items platí totéž s klíčem `actionItemId`; navíc lze po zpracování nastavit `update_pocket_actionitem(status="COMPLETED")` a uzavřít tak smyčku přímo v Pocketu.

---

## F. VAZBY — co lze skutečně vytvořit

Požadovaný řetězec:

| Krok | Přes MCP | Jak |
|---|---|---|
| Klient | ✅ | `company_create` (povinné `name`,`rating`,`state`,`role`) |
| ↓ OP | ✅ | `businessCase_create(name, company=<id>)` — vazba na klienta je **povinná** |
| ↓ Telefonát | ✅ | `phonecall_create(title, owner, company, businessCase)` — vazba na OP i klienta rovnou při zakládání |
| ↓ **Dopis** | ❌ | **Neexistuje `letter_create` ani `email_create`.** Náhrada: `task_create` nebo `meeting_create` |
| ↓ Follow-up telefonát | ✅ | `phonecall_create(status="SCHEDULED", scheduledFrom=…, businessCase=…)` |

**Další ověřené možnosti vazeb:** aktivita → `company`, `lead`, `project`, `businessCase`, `offer`, `salesOrder`, `securityLevel`, `category`; `participants[]` (person / company / lead, role `FROM`/`TO`/`CC`/`BCC`).

⚠️ **Omezení vazeb:**
- **`phonecall` / `meeting` / `event` NEMAJÍ přímé pole `person`** — CRM to strukturálně zakazuje. Kontaktní osobu lze navázat **jen přes `participants`**. (`task` přímé pole `person` má.)
- `phonecall_update` **neumí změnit `owner`** — backend pole ignoruje.
- `participants` na update **nahrazují celý seznam** — vynechaný účastník je smazán. Nutné nejdřív `phonecall_get`.
- `lead_convert` **nikdy nic nevytváří** — pouze propojí lead s **už existující** company/person/businessCase.
- Přílohy: jen `attachmentLink` (URL) nebo `attachmentFolderId`. **Binární soubor nelze nahrát** → Pocket audio lze připojit jen jako odkaz, a ten **expiruje za 3600 s**.

---

## G. REALIZOVANÁ AKTIVITA — zpětný zápis hovoru

### Rozlišení stavů (ověřeno na reálných datech)

| Stav | `status` | `completed` | `scheduledFrom/Till` | `solution` |
|---|---|---|---|---|
| Naplánovaná | `SCHEDULED` | `null` | v budoucnu | `null` |
| **Realizovaná** | `COMPLETED` | **timestamp** | v minulosti | vyplněno HTML |
| Zrušená | `CANCELLED` | timestamp | — | — |
| Nenaplánovaná | `NEW` | `null` | `null` | — |

### Mechanika

- **Neexistuje boolean „hotovo"** — `completed` je **timestamp**, ne flag. V `*_list` proto **není** filtr completed/uncompleted; filtruje se přes `status`.
- **Nastavení `status` přepisuje `completed` server-side:**
  - `→ NEW` / `→ SCHEDULED` : `completed` se **vymaže**
  - `→ COMPLETED` / `→ CANCELLED` : `completed` se nastaví na `scheduledTill` (nebo now)
  - ⇒ Vlastní hodnotu `completed` a `status` v jednom volání **nekombinovat** — vyhraje `status`.
- **Zpětný zápis hovoru = jedno volání `phonecall_create`** s `status="COMPLETED"`, `scheduledFrom`/`scheduledTill` v minulosti, `company`, `businessCase`, `owner=2`, `description`, `solution`.
- Pole pro poznámku: **`description`** (kontext / vstup) a **`solution`** (výstup / co se dohodlo). V reálné praxi instance se `solution` používá pro shrnutí hovoru → **sem patří Pocket Summary**.
- `category` přepisuje `color` server-side — `color` vedle `category` nemá smysl posílat.

---

## H. FORMÁTOVÁNÍ POLÍ

**Ověřeno čtením reálných záznamů** (nikoli odhad):

| Pole | Formát | Důkaz |
|---|---|---|
| `phonecall.solution` | **HTML** | `<p>Úvodní schůzka s…</p>`, `<ul><li style="margin: 0"><p><b>…</b></p></li></ul>` |
| `phonecall.description` | **HTML** | `Záměr: …<br><br>Bonita: …` |
| `task.solution` | **HTML** | `<p>zaslána nabídka účelové…</p>` |
| `meeting.description` | **HTML** | `<p>lepší komentář k yoy nárůstu…</p>` |
| `company.notice` | **HTML** | `"<p>\n<br>\n</p>"` |
| `businessCase.name`, `*.title` | **prostý text** | bez značek ve všech vzorcích |
| `tags` | **string při zápisu, pole při čtení** | `"tags":[]` vs. param „tags as a single string" |

**Závěry k formátování:**
- **Odstavce:** `<p>…</p>` ✅ · **Odrážky:** `<ul><li>` ✅ · **Číslované:** `<ol><li>` ✅ · **Tučně:** `<b>` ✅ · **Zalomení:** `<br>` ✅ · **Odkazy:** `<a href>` ✅
- **Markdown NENÍ podporován** — Pocket `summary.markdown` je nutné **převést na HTML**. Zápis syrového Markdownu skončí jako doslovné `###` a `**` v CRM.
- Inline `style` atributy jsou v datech přítomné (`<li style="margin: 0">`) → HTML se nesanitizuje agresivně.
- Maximální délka polí `description` / `solution` = **NEOVĚŘENO**.
- Chování `title` při délce > X znaků = **NEOVĚŘENO**.

---

## I. LIMITATIONS — co MCP neumí

1. ❌ **Nelze zakládat e-maily ani dopisy** (`Email`/`Letter` aktivity) — chybí nástroje, byť je feed vrací.
2. ❌ **Žádný generický `activity_get`** — nutno volat `phonecall_get`/`task_get`/`meeting_get`/`event_get` podle `_entityName`.
3. ❌ **Binární upload příloh nelze** — jen URL odkaz nebo id složky Documents.
4. ❌ **Pocket audio nelze trvale archivovat** — `signed_url` expiruje po **3600 s**.
5. ❌ **Pocket action items: strop 50, bez `offset`** — nelze stránkovat.
6. ❌ **`businessCase.status` nelze nastavit přímo** — jen přes `businessCasePhase`.
7. ❌ **`phonecall_update` neumí změnit `owner`.**
8. ❌ **Žádný lookup nástroj pro `owner` ani `securityLevel`** — id se musí znát (Adam = 2, securityLevel 1 = Sdílená).
9. ❌ **Nelze vytvořit person-type company** přes `company_create`.
10. ❌ **Pocket složky nejsou k dispozici** (0 složek) → `folderIds` filtr je dnes bezcenný.
11. ⚠️ **Limit 50 záznamů na stránku** u všech Raynet `*_list`.

### Explicitně NEOVĚŘENO

| Položka | Proč |
|---|---|
| **Mechanismus `confirmToken`** | Schémata dokumentují two-phase preview → confirm s TTL **60 s** (`lead_convert`: „call again … within 60 seconds"). Empiricky **netestováno** — zápisové nástroje blokuje permission gate. |
| `EActivityPriority` hodnoty | Chybí v `raynet://enumerations`; pozorováno jen `DEFAULT`, `CRITICAL` |
| Názvy fází OP id 4, 5, 6, 12, 13, 14 | Nejsou v otevřené pipeline |
| Zda lze přes API založit **nový** název tagu | Netestováno (jen zápisem) |
| Dohledatelnost celého UUID přes `fulltext` | Žádný záznam zatím UUID neobsahuje |
| Maximální délky textových polí | Netestováno |
| `query_pocket_meetings` | Nevoláno |
| `update_pocket_actionitem` | Nevoláno (zákaz zápisu) |

---

## J. RISKS — kde AI udělá chybu

| # | Riziko | Dopad | Mitigace |
|---|---|---|---|
| 1 | **Špatné spárování klienta** kvůli přepisu jména (`Balint`/`Balent`, `Hasová`/`Hasolová`) | Hovor u cizího klienta | Párovat přes **e-mail/IČO**, ne jméno. Při <1 jistém zásahu **eskalovat na člověka** |
| 2 | **Duplicitní klienti už v CRM** — ověřeno: `Zbyněk Svoboda` id **613** i **603**, shodný e-mail | Zápis k nesprávné kopii | Při >1 zásahu nikdy nehádat — předložit uživateli k výběru |
| 3 | **Založení nového klienta místo nalezení stávajícího** | Další duplicita v 1050 záznamech | `company_create` **nikdy automaticky**; jen po potvrzení |
| 4 | **Markdown zapsaný do HTML pole** | `###` a `**` viditelné v CRM | Povinný převod MD→HTML + odstranění `<pocket:*>` tagů |
| 5 | **Záměna `recordingDate`** ze `search_*` vs `get_*` | Aktivita posunutá o délku hovoru | `scheduledFrom` = `search_*`, `scheduledTill` = `get_*` |
| 6 | **Duplicitní řádky v query mode** (8 řádků = 4 nahrávky) | Vícenásobné zpracování | Deduplikace podle `recordingId` před zpracováním |
| 7 | **`status` přepíše `completed`** | Ztráta skutečného času hovoru | Neposílat obě pole současně |
| 8 | **`participants` / `tags` update = přepis** | Ztráta účastníků a štítků | Vždy nejdřív `*_get` a sloučit |
| 9 | **Halucinace číselníkových id** | Backend error nebo špatná kategorie | Jen id z tohoto auditu nebo z `raynet://codelist/*` |
| 10 | **Zpracování nahrávky bez klienta** (interní porady, testy) | Balast v CRM | Whitelist/klasifikace typu hovoru před zápisem |
| 11 | **Únik citlivých dat** — přepisy obsahují rodná čísla, zůstatky úvěrů | GDPR | Nezapisovat r.č. do CRM polí; redigovat před zápisem |
| 12 | **Vyčerpání rate limitu** | Zastavení workflow | 24 000/den je dostatek; `rate_limit_status` je zdarma |

---

## K. RECOMMENDED SKILL ARCHITECTURE

```
pocket-raynet-wf/
├── SKILL.md                     # vstupní bod, rozhodovací strom, kdy se spouští
├── references/
│   ├── raynet-entities.md       # číselníky, enumerace, povinná pole, id (owner=2)
│   ├── pocket-api.md            # režimy search, tvary odpovědí, nekonzistence dat
│   ├── field-mapping.md         # Pocket → Raynet mapa polí
│   └── html-formatting.md       # MD→HTML převod + strip <pocket:*>
├── scripts/
│   ├── md_to_raynet_html.py     # deterministický převod (ne LLM)
│   ├── dedup_check.py           # 3vrstvá idempotence
│   └── client_match.py          # skórování kandidátů klienta
└── state/
    └── processed.json           # recordingId → {activityId, companyId, businessCaseId, ts}
```

### Workflow (fáze)

```
1. FETCH     search_pocket_conversations (recency, od last_run)
             → dedup podle recordingId
2. FILTER    ledger + phonecall_list(companyId, ±2 min) → přeskočit zpracované
3. CLASSIFY  klientský hovor? interní? test? → jen klientské pokračují
4. ENRICH    get_pocket_conversation → summary + přesný scheduledTill
5. MATCH     company_list: email → IČO → name → fulltext → lead_list
             0 zásahů → ESKALACE   |   >1 zásah → ESKALACE   |   1 → pokračuj
6. CONTEXT   businessCase_list(companyId, status=B_ACTIVE) → vybrat OP
7. RENDER    MD→HTML, strip <pocket:*>, redakce r.č./citlivých údajů
8. PREVIEW   předložit uživateli: klient, OP, title, časy, náhled textu
9. WRITE     phonecall_create(status=COMPLETED, company, businessCase, owner=2)
10. FOLLOWUP action items → task_create / phonecall_create(SCHEDULED)
11. LEDGER   zápis do processed.json + update_pocket_actionitem(COMPLETED)
```

### Validační pravidla (tvrdá)

| # | Pravidlo |
|---|---|
| V1 | `owner` = **2** vždy explicitně (create bez něj selže) |
| V2 | `status` ∈ {`NEW`,`SCHEDULED`,`COMPLETED`,`CANCELLED`} — nikdy český překlad |
| V3 | `status` a `completed` **nikdy v jednom volání** |
| V4 | Text do `description`/`solution` **jen HTML**, nikdy Markdown |
| V5 | Řetězec `<pocket:` se **nesmí** objevit ve výstupu |
| V6 | Klient jednoznačný (přesně 1 zásah), jinak **stop + dotaz** |
| V7 | `company_create` / `businessCase_create` **nikdy bez potvrzení** |
| V8 | Číselníková id **jen** z `references/raynet-entities.md` nebo `raynet://codelist/*` |
| V9 | Rodná čísla a čísla účtů se do CRM **nezapisují** |
| V10 | Před každým `*_update` předchází `*_get` (kvůli přepisu participants/tags) |

### Error handling

| Situace | Reakce |
|---|---|
| Klient nenalezen | **Stop**, nabídnout založení — nezakládat sám |
| >1 kandidát | **Stop**, předložit seznam s id, e-mailem, ownerem |
| Žádný otevřený OP | Založit telefonát **bez** vazby na OP (je volitelná) + upozornit |
| Backend validation error | Nezkoušet znovu s hádaným id — vypsat chybu, ta jmenuje platná id |
| Rate limit | `rate_limit_status` (zdarma) před dávkou; zbývá 23 635 |
| Aktivita už existuje | Tiše přeskočit + zaznamenat do ledgeru |
| `confirmToken` expiroval (60 s) | Zopakovat preview, **nikdy token nevymýšlet** |

### Idempotence — shrnutí

Klíč: **`recordingId`**. Kontrola v pořadí `ledger` → `phonecall_list(companyId, ±2 min)` → marker v `description`.
Cílový stav: custom field `pocket_recording_id` (vyžaduje **ruční založení v Raynet UI** — mimo MCP).

---

## L. POSSIBLE WORKFLOW — maximum technicky proveditelné

```
Pocket nahrávka
   │
   ├─ ✅ dohledání podle data / recency / sémanticky (s deduplikací)
   ├─ ✅ plný přepis + timestampy + speaker labely
   ├─ ✅ AI Summary (Markdown → převod na HTML)
   ├─ ✅ action items s termíny a prioritami
   └─ ⚠️ audio jen jako odkaz s platností 60 minut
   │
   ▼
Raynet
   ├─ ✅ nalezení klienta (email / IČO / jméno / fulltext / lead)
   ├─ ⚠️ založení klienta (jen s potvrzením)
   ├─ ✅ nalezení otevřeného OP
   ├─ ⚠️ založení OP (jen s potvrzením; status řídí fáze)
   ├─ ✅ REALIZOVANÝ telefonát s vazbou na klienta i OP     ← jádro workflow
   ├─ ✅ účastníci (participants)
   ├─ ✅ NAPLÁNOVANÝ follow-up telefonát
   ├─ ✅ úkol s deadlinem (náhrada za e-mail/dopis)
   ├─ ✅ posun fáze OP
   ├─ ❌ e-mail / dopis jako aktivita
   └─ ❌ binární příloha
   │
   ▼
Zpětně do Pocketu
   └─ ✅ update_pocket_actionitem(status="COMPLETED") — uzavření smyčky
```

**Závěr:** požadovaný řetězec *Klient → OP → Telefonát → Dopis → Follow-up telefonát* je přes MCP realizovatelný **s jedinou výjimkou — „Dopis" nelze založit**. Náhradou je `task` nebo `meeting`. Všechny ostatní vazby lze vytvořit přímo při zakládání aktivity, v jednom volání.
