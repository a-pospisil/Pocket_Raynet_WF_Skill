# Pocket → Raynet

Claude skill, který zapisuje hovory nahrané v **Hey Pocket** do **Raynet CRM** jako
realizované telefonáty — včetně shrnutí, vazby na klienta a obchodní případ,
a navazujících aktivit z Pocket action items.

Prostředí je finanční poradenství, hypotéky a investiční nemovitosti
([Evergreen finance](https://egfin.cz)).

## Jak to funguje

```
Pocket nahrávka  →  klasifikace  →  párování klienta  →  kontrola duplicity
                                                              ↓
                              Raynet: realizovaný telefonát + follow-up aktivity
```

Proces je **interaktivní**, ne automatický. Spustíte ho pokynem, skill připraví návrh
a před zápisem ho nechá potvrdit. Důvod je praktický: Raynet obsahuje přes 1000 klientů,
z toho ~94 % fyzických osob, mezi nimi už existující duplicity, a Pocket komolí jména
v přepisech (`Balint`/`Balent`, `Hasová`/`Hasolová`). Špatně spárovaný hovor skončí
u cizího člověka a nikdo si toho nevšimne. Zápis do CRM je navíc přes MCP **nevratný** —
žádný `delete` nástroj neexistuje.

## Použití

Skill se aktivuje sám, když jde o převod hovoru do CRM. Stačí přirozený pokyn:

```
zapiš poslední hovor do Raynetu
zpracuj dnešní hovory
zapiš ten hovor s Balentem ke klientovi
```

Nejrychlejší a nejbezpečnější je varianta, kde klienta jmenujete sám — přeskočí
se tím nejrizikovější krok celého procesu.

## Co skill nikdy neudělá

Tyhle hranice nejsou opatrnost, ale technická omezení MCP ověřená auditem:

| | Proč |
|---|---|
| **Nezaloží klienta** | `company_create` umí vytvořit jen organizaci, ne fyzickou osobu. U ~94 % klientské báze by vznikl záznam špatného typu. Nový klient = ruční krok v Raynet UI. |
| **Nezaloží e-mail ani dopis** | Aktivity typu `Email` a `Letter` jdou číst, ale MCP je vytvořit neumí. Náhradou je úkol. |
| **Nenahraje přílohu** | Jen odkaz URL. Pocket audio navíc expiruje po hodině. |
| **Nezapíše rodné číslo ani číslo účtu** | Redakce probíhá automaticky v převodním skriptu. |
| **Nezapíše bez potvrzení** | Vždy nejdřív ukáže návrh. |

## Struktura

```
pocket-to-raynet/
├── SKILL.md                        # workflow, rozhodovací body, eskalace
├── references/
│   ├── raynet-reference.md         # číselníky, id, povinná pole, pasti
│   ├── pocket-reference.md         # tvary odpovědí, formáty id, limity
│   └── html-formatting.md          # co Raynet v HTML polích unese
└── scripts/
    └── md_to_raynet_html.py        # Pocket Summary → HTML pro Raynet

docs/
└── AUDIT-POCKET-RAYNET.md          # technický audit obou MCP, podklad pro skill
```

Reference se načítají až když jsou potřeba. `SKILL.md` nese jen to, co se použije
při každém běhu.

## Předpoklady

- **Hey Pocket** — plán Pro (kvůli `get_pocket_conversation`)
- **Raynet MCP** — instance `evergreen`, denní limit 24 000 requestů
- Vlastník aktivit je napevno `owner = 2` (Adam Pospíšil)

## Převodní skript

Pocket vrací shrnutí v Markdownu, Raynet pole `description` a `solution` renderuje
jako HTML. Syrový Markdown se v CRM zobrazí i s `###` a `**`, takže převod je povinný.
Skript navíc odstraní proprietární bloky `<pocket:chart>` a `<pocket:decision-tree>`
a rediguje citlivé údaje.

```bash
python3 pocket-to-raynet/scripts/md_to_raynet_html.py summary.md \
        --recording-id 890c636f-1555-4714-aa95-3f65618db135
```

Bez závislostí, jen standardní knihovna Pythonu 3.

## Stav

Skill je ověřený **suchým během na reálných datech** (15 nahrávek z jednoho dne),
kde odhalil a nechal opravit šest chyb — mimo jiné dvě různé díry v detekci duplicit:

- hovor bývá v Raynetu uložený i jako **událost**, ne jen jako telefonát
- ručně zapsaný hovor má často `scheduledFrom: null`, takže ho časové okno nikdy nevrátí

**Ostrý zápis do Raynetu zatím neproběhl.** Detaily v auditu, sekce
*RISKS* a *LIMITATIONS*.
