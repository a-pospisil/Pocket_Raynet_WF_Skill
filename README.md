# Pocket → Raynet

Claude skill, který zapisuje hovory a schůzky nahrané v **Hey Pocket** do **Raynet CRM**:
stručný strukturovaný zápis (dokončí naplánovanou aktivitu, jinak založí realizovanou),
kartu případu v popisu obchodního případu s nájmy a bonitou pro 8 bank, maximum údajů na kartu klienta
(kontakty, zdroj, tipař, vlastní pole, profil klienta s portfoliem a konci fixací),
jeden souhrnný úkol s návrhem e-mailu a návrh posunu fáze. Ráno umí připravit dnešní schůzky.
Běží v Claude Code i v orchestrátoru Hermes (každý poradce vlastní instance).

Prostředí je finanční poradenství, hypotéky a investiční nemovitosti
([Evergreen finance](https://egfin.cz)).

## Jak to funguje

```
Pocket nahrávka → třídění a šablona (S / M / L) → párování klienta → co už u klienta je
                                                                         ↓
   Raynet: dokončená naplánovaná aktivita (nebo nová) · karta OP · karta klienta
           · souhrnný úkol · návrh posunu fáze                    (vše po potvrzení)
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
připrav mi dnešní schůzky
```

Nejrychlejší a nejbezpečnější je varianta, kde klienta jmenujete sám — přeskočí
se tím nejrizikovější krok celého procesu.

## Co skill nikdy neudělá

Tyhle hranice nejsou opatrnost, ale technická omezení MCP ověřená auditem:

| | Proč |
|---|---|
| **Nezaloží klienta** | `company_create` umí vytvořit jen organizaci, ne fyzickou osobu. Neznámý volající se založí jako **lead**, klienta zakládá člověk v UI. |
| **Nezaloží e-mail ani dopis** | MCP to neumí. Návrh e-mailu klientovi je v popisu souhrnného úkolu. |
| **Nezapíše pod nejistého klienta** | Klient musí sedět ve dvou znacích, jinak se ptá. |
| **Nezaloží duplicitu k naplánované aktivitě** | Naplánovaný hovor nebo schůzku z téhož dne, které proběhly v jiný čas, dokončí. Aktivity z jiných dní nechá být. |
| **Nezruší schůzku** | Zrušení v Raynetu ji smaže i v Google kalendáři. |
| **Nezmění pole OP** | Navrhne jen posun fáze. |
| **Nenahraje přílohu** | Jen odkaz URL. Pocket audio navíc expiruje po hodině. |
| **Nezapíše rodné číslo ani číslo účtu** | Redakce probíhá automaticky v převodním skriptu. |
| **Nezapíše bez potvrzení** | Vždy nejdřív ukáže návrh. |

## Struktura

```
pocket-to-raynet/
├── SKILL.md                        # workflow, rozhodovací body, eskalace
├── references/
│   ├── sablony-zapisu.md           # šablony S / M / L, karta OP, bonita, úkol, příprava
│   ├── raynet-reference.md         # uživatelé, číselníky, vlastní pole, pasti
│   ├── pocket-reference.md         # tvary odpovědí, formáty id, limity
│   └── html-formatting.md          # co Raynet v HTML polích unese
└── scripts/
    └── md_to_raynet_html.py        # Pocket Summary → HTML pro Raynet

docs/
├── AUDIT-POCKET-RAYNET.md          # technický audit obou MCP, podklad pro skill
├── NAVRH-ZAPISY.md                 # scénáře a Adamova rozhodnutí o zápisech (1. 10. 2026)
├── RAYNET-OPTIMALIZACE.md          # doporučené nastavení Raynetu
└── RAYNET-MANUAL-POZNAMKY.md       # poznámky z celé nápovědy a API Raynetu
```

Reference se načítají až když jsou potřeba. `SKILL.md` nese jen to, co se použije
při každém běhu.

## Předpoklady

- **Hey Pocket** — plán Pro (kvůli `get_pocket_conversation`)
- **Raynet MCP** — instance `evergreen`, denní limit 24 000 requestů
- Vlastník aktivit se zjišťuje za běhu z přihlášeného uživatele Raynetu
- Pro bonitu: přístup k metodice bank (repo s metodikou, zatím Adamův vault `wiki/metodiky/`)

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

1. 10. 2026 proběhl zkušební zápis na testovacího klienta. Ověřil, že Raynet odstraní `<table>` i `<pre>`
a že `status=COMPLETED` při založení nastaví čas dokončení na okamžik zápisu (skill ho hned opraví).
**Ostrý zápis ke klientovi zatím neproběhl.**
