# Pocket → Raynet

Skill, který zapisuje hovory nahrané v **Hey Pocket** do **Raynet CRM** jako
realizované telefonáty — včetně shrnutí, vazby na klienta a obchodní případ,
navazujících aktivit z Pocket action items a konceptů e-mailů k úpravě.

Prostředí je finanční poradenství, hypotéky a investiční nemovitosti
([Evergreen finance](https://egfin.cz)).

## Jak to funguje

```
Pocket nahrávka  →  klasifikace  →  párování klienta  →  kontrola duplicity
                                                              ↓
                         Raynet: realizovaný telefonát, OP nebo lead, follow-up aktivity
                         + koncept e-mailu s chybějícími podklady (nikdy se neodesílá)
                         + řádek v audit logu za každou akci
```

Proces je **interaktivní**, ne automatický. Spustíte ho pokynem, skill připraví návrh
a před zápisem ho nechá potvrdit. Důvod je praktický: Raynet obsahuje přes 1000 klientů,
z toho ~94 % fyzických osob, mezi nimi už existující duplicity, a Pocket komolí jména
v přepisech (`Balint`/`Balent`, `Hasová`/`Hasolová`). Špatně spárovaný hovor skončí
u cizího člověka a nikdo si toho nevšimne. Zápis do CRM je navíc přes MCP **nevratný** —
žádný `delete` nástroj neexistuje.

Potvrzování se má **postupně vypínat** tam, kde se ukáže, že skill nechybuje. Podkladem
je audit log, který u každého typu akce počítá, kolik návrhů prošlo beze změny.

## Instalace

Skill je složka `pocket-to-raynet/`. Funguje ve třech prostředích — ve všech potřebuje
připojené MCP servery **Hey Pocket** a **Raynet**.

**Claude (claude.ai, desktop, mobil)** — nejjednodušší je soubor `pocket-to-raynet.skill`:
otevřete ho v Claude a klikněte na **Save skill**. Soubor vyrobíte z repozitáře takhle
(nebo si o něj řekněte Claudovi):

```bash
zip -r pocket-to-raynet.skill pocket-to-raynet -x '*/__pycache__/*'
```

**Claude Code** — zkopírujte složku mezi osobní skilly:

```bash
cp -r pocket-to-raynet ~/.claude/skills/
```

**Hermes Agent** ([Nous Research](https://hermes-agent.nousresearch.com/docs/)) — Hermes
čte skilly ve stejném formátu (standard agentskills.io), takže skill jde přenést beze
změny. Zkopírujte složku do `~/.hermes/skills/` a připojte v Hermes oba MCP servery.
Hermes navíc umí věci, které interaktivní Claude neumí: pravidelné spouštění (cron),
trvalou paměť a doručení výsledků do Telegramu nebo e-mailu. *Instalace do Hermes zatím
nebyla vyzkoušena.*

## Použití

Skill se aktivuje sám, když jde o převod hovoru do CRM. Stačí přirozený pokyn:

```
zapiš poslední hovor do Raynetu
zpracuj dnešní hovory
zapiš ten hovor s Balentem ke klientovi
připrav klientovi mail z toho hovoru
```

Nejrychlejší a nejbezpečnější je varianta, kde klienta jmenujete sám — přeskočí
se tím nejrizikovější krok celého procesu.

## Co skill nikdy neudělá

Tyhle hranice nejsou opatrnost, ale technická omezení MCP ověřená auditem:

| | Proč |
|---|---|
| **Neodešle e-mail** | Jen připraví koncept. Odeslání je vždy na člověku. |
| **Nezaloží klienta přes `company_create`** | Ten umí vytvořit jen organizaci, ne fyzickou osobu — u ~94 % klientské báze by vznikl záznam špatného typu. Nového zájemce proto založí jako **lead** (ten fyzickou osobu umí); klient z něj vznikne převodem v Raynet UI. |
| **Nezapíše obsah soukromého hovoru** | Soukromý hovor jde do CRM jen jako osobní aktivita s neutrálním názvem — CRM vidí celý tým. |
| **Nezaloží e-mail ani dopis jako aktivitu v Raynetu** | Aktivity typu `Email` a `Letter` jdou číst, ale MCP je vytvořit neumí. |
| **Nenahraje přílohu** | Jen odkaz URL. Pocket audio navíc expiruje po hodině. |
| **Nezapíše rodné číslo ani číslo účtu do CRM** | Redakce probíhá automaticky v převodním skriptu. |
| **Nepřepíše záznam beze stopy** | Každý přepis uloží do logu původní stav — jiná cesta zpět přes MCP není. |

## Nástroje

Čtyři skripty, jen standardní knihovna Pythonu 3, bez závislostí.

**Párování jmen** — `scripts/match_name.py`. Nejčastější chyba celého procesu je
zkomolené jméno. Skript z přepisu udělá hledací výrazy pro Raynet (filtr `name`
rozlišuje diakritiku, přepis bývá v pádě) a kandidáty seřadí foneticky:

```bash
python3 pocket-to-raynet/scripts/match_name.py score "Bretschneider" kandidati.json
# → jistý: Jan Bretšnajdr (124), skóre 0.95
```

Když si není jistý — nebo když je klient v CRM dvakrát — řekne to a skill se zeptá.

**Koncepty e-mailů** — `scripts/make_email_draft.py`. Vyrobí `.eml` s hlavičkou
`X-Unsent: 1`, takže se v Apple Mail otevře jako **koncept k úpravě**, ne jako
přijatá zpráva jen pro čtení. Styl podle `references/email-style.md`, který vychází
z vašich skutečných e-mailů a doplňuje se z úprav, které na konceptech děláte.

**Audit log** — `scripts/audit_log.py`. Řádek za každou akci, u přepisů i s původním
stavem. `stats` ukáže přesnost návrhů podle typu akce a upozorní, kde by šlo potvrzování
vypnout.

**Převod shrnutí** — `scripts/md_to_raynet_html.py`. Raynet renderuje `description`
a `solution` jako HTML; skript převede Markdown z Pocketu, odstraní bloky
`<pocket:chart>` a `<pocket:decision-tree>` a rediguje citlivé údaje.

## Struktura

```
pocket-to-raynet/                   # skill — tohle se instaluje
├── SKILL.md                        # workflow, rozhodovací body, režimy potvrzování
├── references/
│   ├── raynet-reference.md         # číselníky, id, povinná pole, pasti
│   ├── pocket-reference.md         # tvary odpovědí, formáty id, limity
│   ├── html-formatting.md          # co Raynet v HTML polích unese
│   └── email-style.md              # jak píšete e-maily + naučená pravidla
├── scripts/                        # viz Nástroje
└── assets/
    └── signature.txt               # podpis e-mailů

docs/
├── AUDIT-POCKET-RAYNET.md          # technický audit obou MCP
└── SCENARIE.md                     # katalog situací → podklad pro protokoly

tests/                              # regresní testy na reálných případech
```

## Testy

```bash
python3 -m unittest discover -s tests -v
```

Testy párování jmen stojí na skutečných chybách přepisu z provozu — Bretschneider,
Semrád, Honza Ruml — a na klientech, u kterých skill **nesmí** být jistý (duplicity).

## Předpoklady

- **Hey Pocket** — plán Pro (kvůli `get_pocket_conversation`)
- **Raynet MCP** — instance `evergreen`, denní limit 24 000 requestů
- Vlastník aktivit je napevno `owner = 2` (Adam Pospíšil)

## Stav

Ověřeno **suchým během na reálných datech** (15 nahrávek z jednoho dne), který odhalil
a nechal opravit šest chyb — mimo jiné dvě různé díry v detekci duplicit.

**Ostrý zápis do Raynetu zatím neproběhl.** Otevírání konceptu v Apple Mail je ověřené
jen strukturou souboru, ne na Macu. Nerozhodnuté situace jsou v `docs/SCENARIE.md`.

Repozitář obsahuje interní kontext (instance, id uživatele, podpis s telefonem).
Tokeny ani hesla v něm nejsou, ale před případným zveřejněním ho projděte.
