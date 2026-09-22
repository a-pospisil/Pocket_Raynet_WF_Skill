# Hey Pocket — referenční přehled

Ověřeno na účtu `adam.pospisil@egfin.cz` (plán **pro**) dne 21. 9. 2026.
Plný audit: `docs/AUDIT-POCKET-RAYNET.md` v repozitáři.

## Obsah

- [Nástroje](#nástroje)
- [Dva režimy hledání](#dva-režimy-hledání)
- [Detail nahrávky](#detail-nahrávky)
- [Nekonzistence recordingDate](#nekonzistence-recordingdate)
- [Formáty recordingId](#formáty-recordingid)
- [Mluvčí](#mluvčí)
- [Action items](#action-items)
- [Co Pocket neumí](#co-pocket-neumí)

## Nástroje

| Nástroj | R/W | K čemu |
|---|---|---|
| `search_pocket_conversations` | R | hledání nahrávek, dva režimy |
| `get_pocket_conversation` | R | Summary, plné segmenty, audio URL |
| `search_pocket_actionitems` | R | úkoly vytěžené z hovorů |
| `update_pocket_actionitem` | **W** | uzavření úkolu v Pocketu |
| `list_pocket_folders` | R | složky — **v tomto účtu žádné nejsou** |
| `get_account_info` | R | identita, plán |
| `query_pocket_meetings` | R | dotaz v přirozeném jazyce (neověřeno) |

`get_pocket_conversation` a `query_pocket_meetings` vyžadují plán Pro.

## Dva režimy hledání

`search_pocket_conversations` se chová **jinak podle toho, jestli dostane `query`**,
a to včetně tvaru odpovědi.

### Recency režim (bez `query`)

Nejnovější první, plné přepisy.

```
data { limit, total, recordings[], meta { hasMore, matchedCount, remainingCount,
       returnedCount, pageSize, oldestReturnedRecordingDate,
       nextRecordingDateBeforeExclusive } }
```

Pole nahrávky: `content` (plný přepis s prefixy „Speaker N:"), `contentSnippet`
(500 znaků), `documents[]`, `language`, `recordingDate`, `recordingId`,
`recordingTitle`, `relevanceScore` (vždy 0), `transcriptSegments[]`, `transcriptionId`.

- **`pageSize` je pevně 5.** Další stránka: `recordingDateBeforeExclusive` =
  `meta.nextRecordingDateBeforeExclusive` z předchozí odpovědi.
- Neobsahuje Summary, action items, audio ani tagy.

Tohle je režim pro dávkové zpracování — dá se filtrovat `recordingDateAfter`
a `recordingDateBefore` a spolehlivě projít celé období.

### Query režim (se `query`)

Sekční hybridní hledání. **Jiný tvar odpovědi, bez stránkování:**

```
data { queryUsed, recordings[], timing, total }
```

Navíc pole: `metadata { matchType, source }`, `sectionStartMs`, `sectionEndMs`,
`sectionSummary`, `sectionTitle`, `speakers` (string, ne pole).

⚠️ **Dvě věci, na které se dá naletět:**

1. **Vrací duplicitní řádky téže nahrávky.** Měřeno: 8 řádků = 4 unikátní
   `recordingId`, jedna nahrávka se opakovala 4× se shodným skóre. Vždy deduplikuj.
2. **Na hledání podle jména klienta se nedá spolehnout.** Dotaz „Peter Balent
   financování pozemku na Slovensku" nenašel nahrávku s názvem
   „Konzultace a výpočet [Peter Balent]". Všechny zásahy se vrátily jako
   `matchType: "bm25"`, tedy keyword, ne vektorově.

Query režim používej na dohledání nahrávky podle **tématu**, ne podle osoby.

## Detail nahrávky

`get_pocket_conversation(recording_ids=[…])` — zvládne víc id najednou, funguje
na oba formáty id.

Vrací: `recordingId`, `recordingTitle`, `recordingDate`, `recordingTags[]`,
`transcriptSegments[{text, start, end, speaker}]`, `summary { markdown, version }`,
`audioUrl { signed_url, expires_in, expires_at }`.

**`summary.markdown` obsahuje proprietární bloky Pocketu**, které mimo Pocket nedávají
smysl a do CRM nepatří:

```
<pocket:chart type="bar" title="…">popisek | hodnota</pocket:chart>
<pocket:decision-tree title="…">uzel::otázka …</pocket:decision-tree>
```

Odstraní je `scripts/md_to_raynet_html.py`.

**`audioUrl.signed_url` expiruje za 3600 s.** Do CRM se dá vložit jen jako
`attachmentLink`, tedy jako odkaz, který za hodinu přestane fungovat. Trvalá archivace
audia přes MCP možná není.

## Nekonzistence recordingDate

Tentýž `recordingId` vrací **jiné datum podle nástroje**. Není to chyba měření,
je to ověřené na dvou nahrávkách:

| recordingId | `search_*` | `get_pocket_conversation` | rozdíl | délka přepisu |
|---|---|---|---|---|
| `36d473d6-…` | 13:48:28.000Z | 13:57:32Z | +9:04 | 494 s (8:14) |
| `desktop_1789996938017_u1rl1v` | 13:22:18.017Z | 13:37:36Z | +15:18 | 911 s (15:11) |

**`search_*` vrací začátek, `get_pocket_conversation` konec.** Rozdíl odpovídá délce
hovoru. Potvrzuje to i epoch v desktopovém id: `desktop_**1789996938017**_…`
= `2026-09-21T13:22:18.017Z`, přesně hodnota ze `search_*`.

Pro Raynet tedy:
- `scheduledFrom` ← `recordingDate` ze `search_pocket_conversations`
- `scheduledTill` ← `recordingDate` z `get_pocket_conversation`

Záměna posune aktivitu v kalendáři o délku hovoru.

## Formáty recordingId

Dva tvary, oba stabilní a použitelné jako klíč:

| Tvar | Příklad | Původ |
|---|---|---|
| UUID | `36d473d6-c7c5-46fc-8d55-1211085af00c` | mobilní / serverová nahrávka |
| `desktop_<epochMs>_<rand>` | `desktop_1789996938017_u1rl1v` | desktopový klient |

U desktopového tvaru je epoch v milisekundách přesný čas začátku.

`transcriptionId` je samostatné 32znakové hex id bez pomlček — pro párování se nehodí,
používej `recordingId`.

## Mluvčí

Identifikace je částečná a nekonzistentní:

- V `transcriptSegments` z `get_pocket_conversation` bývá vlastník rozpoznaný jménem
  („Adam Pospíšil"), protistrana skoro vždy jen `SPEAKER_01`.
- V poli `content` (recency režim) jsou tytéž labely normalizované na „Speaker 1:".
- V query režimu je `speakers` prostý string, např. `"SPEAKER_00, SPEAKER_01"`.

**Jméno protistrany z mluvčích vytěžit nejde.** Klient se musí identifikovat z obsahu
hovoru a z názvu nahrávky, a pak ověřit proti CRM.

## Action items

`search_pocket_actionitems` — filtry `query`, `actionType`, `status`, `priority`,
`dueAfter`, `dueBefore`, `recordingDateFrom`, `recordingDateTo`.

Pole: `actionItemId` (UUID), `actionType` (`create_reminder` / `draft_email` /
`send_message`), `assignee` (`me` / `Other`), `context`, `dueDate` (ISO nebo null),
`label`, `payload` (typovaný podle actionType), `priority`, `recordingDate`,
`recordingId`, `recordingTitle`, `status` (`TODO` / `COMPLETED`).

⚠️ **Strop 50 položek a `offset` neexistuje.** Test vrátil `total: 50, limit: 50`,
tedy uříznuto. Dávku je nutné zúžit přes `recordingDateFrom` / `recordingDateTo`
nebo `status`, jinak se starší položky nedostanou ke slovu.

⚠️ **Priorita je asymetrická.** Čtení vrací malá písmena (`high`, `medium`, `low`),
`update_pocket_actionitem` vyžaduje velká (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).

Každá položka nese `recordingId`, takže se spolehlivě naváže na zdrojový hovor.

## Co Pocket neumí

- ❌ **Zapsat tagy k nahrávce.** `recordingTags[]` se čte, ale žádný nástroj je
  nenastaví → nahrávku nelze v Pocketu označit jako zpracovanou.
- ❌ **Stránkovat action items** přes 50 položek.
- ❌ **Složky** — účet jich má nula, takže `folderIds` filtr je bezpředmětný.
- ❌ **Trvalý odkaz na audio** — podepsaná URL platí hodinu.
