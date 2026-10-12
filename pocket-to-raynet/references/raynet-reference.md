# Raynet — referenční přehled

Ověřeno na instanci `evergreen` dne 21. 9. 2026 čtením reálných dat.
Plný audit: `docs/AUDIT-POCKET-RAYNET.md` v repozitáři.

## Obsah

- [Konstanty](#konstanty)
- [Typy aktivit](#typy-aktivit)
- [Stavy aktivit](#stavy-aktivit)
- [Založení leadu](#založení-leadu)
- [Soukromé aktivity](#soukromé-aktivity)
- [Fáze obchodního případu](#fáze-obchodního-případu)
- [Kategorie aktivit](#kategorie-aktivit)
- [Číselníky klienta a prohry](#číselníky-klienta-a-prohry)
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

OP skill zakládá jen ve výjimce z kroku 6 (běžící žádost u banky bez OP), vždy po potvrzení:

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
| `Rodne_cisl_ed0da` | rodné číslo | text, **jen z dokumentu, nikdy z hovoru** |
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

**Prázdný string nemaže ani text.** `event_update` / `meeting_update` se `solution=""` pole nevyprázdní, náhled změnu
vůbec neukáže (ověřeno 12. 10. 2026).

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
- ❌ **Nahrát binární přílohu** — jen `attachmentLink` (URL) nebo `attachmentFolderId`.
- ❌ **Smazat cokoli** — žádný `delete` nástroj. Zápis je nevratný.
- ❌ **Nastavit `businessCase.status` přímo** — jen přes `businessCasePhase`.
- ❌ **Lookup pro `owner` a `securityLevel`** — id se musí znát.
