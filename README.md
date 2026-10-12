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
v přepisech (`Novak`/`Novák`, `Dvořáková`/`Dvořáčková`; ilustrační). Špatně spárovaný hovor skončí
u cizího člověka a nikdo si toho nevšimne. Zápis do CRM je navíc přes MCP **nevratný** —
žádný `delete` nástroj neexistuje.

## Použití

Skill se aktivuje sám, když jde o převod hovoru do CRM. Stačí přirozený pokyn:

```
zapiš poslední hovor do Raynetu
zpracuj dnešní hovory
zapiš ten hovor s Novákem ke klientovi
připrav mi dnešní schůzky
```

Nejrychlejší a nejbezpečnější je varianta, kde klienta jmenujete sám — přeskočí
se tím nejrizikovější krok celého procesu.

## Co skill nikdy neudělá

Tyhle hranice nejsou opatrnost, ale technická omezení MCP ověřená auditem:

| | Proč |
|---|---|
| **Nezaloží klienta sám** | `company_create` umí vytvořit jen organizaci, ne fyzickou osobu. Neznámý volající se založí jako **lead**. Klienta založí jen na výslovný pokyn (jako organizaci, typ se přepne v UI). |
| **Nezaloží e-mail ani dopis** | MCP je umí jen číst. Návrh e-mailu klientovi je v popisu souhrnného úkolu, na pokyn v chatu nebo jako koncept do pošty (`.eml`). |
| **Neodešle e-mail** | Jen připraví návrh. Odeslání je vždy na člověku. |
| **Nepřepíše záznam beze stopy** | Každý přepis uloží do audit logu původní stav — přes MCP jiná cesta zpět není. |
| **Nezapíše pod nejistého klienta** | Klient musí sedět ve dvou znacích, jinak se ptá. |
| **Nezaloží duplicitu k naplánované aktivitě** | Naplánovaný hovor nebo schůzku z téhož dne, které proběhly v jiný čas, dokončí. Aktivity z jiných dní nechá být. |
| **Nezruší schůzku** | Zrušení v Raynetu ji smaže i v Google kalendáři. Duplicitní nebo testovací telefonát zruší jen na výslovný pokyn. |
| **Nezapíše zápis do Události** | Událost nemá v UI pole „Výsledek“, zápis by nebyl vidět. Navrhne převod na Schůzku v UI, nebo na pokyn založí novou Schůzku. |
| **Nemění OP naslepo** | OP založí a jeho prázdná pole doplní, jen když hovor evidentně řeší konkrétní případ, vždy po potvrzení. Fázi jen navrhne, výši existujícího OP změní jen na pokyn. |
| **Nepřejmenuje mluvčí v Pocketu** | MCP Pocketu to neumí. Skill napíše, koho přejmenovat, a opraví to v zápisu podle přepisu. |
| **Nenahraje přílohu** | Jen odkaz URL. Pocket audio navíc expiruje po hodině. |
| **Nezapíše rodné číslo ani číslo účtu z hovoru** | Redakce probíhá automaticky v převodním skriptu. Do karty klienta jen z dokumentu. |
| **Neradí k fakturaci** | V zápisu je fakturace jen tak, jak ji popsal klient. |
| **Nezapíše bez potvrzení** | Vždy nejdřív ukáže návrh. |

## Struktura

```
pocket-to-raynet/
├── SKILL.md                        # workflow, rozhodovací body, eskalace
├── references/
│   ├── sablony-zapisu.md           # šablony S / M / L, karta OP, bonita, úkol, příprava
│   ├── raynet-reference.md         # uživatelé, číselníky, vlastní pole, pasti
│   ├── pocket-reference.md         # tvary odpovědí, formáty id, limity
│   ├── html-formatting.md          # co Raynet v HTML polích unese
│   ├── email-style.md              # jak Adam píše e-maily + naučená pravidla
│   └── podklady.md                 # jaké podklady chtít podle případu, kde zjistit, co přišlo
├── scripts/                        # viz Nástroje
└── assets/
    └── signature.txt               # podpis e-mailů (Adamův; kolega si nahradí svým)

docs/
├── AUDIT-POCKET-RAYNET.md          # technický audit obou MCP, podklad pro skill
├── NAVRH-ZAPISY.md                 # scénáře a Adamova rozhodnutí o zápisech (1. 10. 2026)
├── RAYNET-OPTIMALIZACE.md          # doporučené nastavení Raynetu
└── RAYNET-MANUAL-POZNAMKY.md       # poznámky z celé nápovědy a API Raynetu

tests/                              # regresní testy (ilustrační jména, skutečné typy chyb)
```

Reference se načítají až když jsou potřeba. `SKILL.md` nese jen to, co se použije
při každém běhu.

## Předpoklady

- **Hey Pocket** — plán Pro (kvůli `get_pocket_conversation`)
- **Raynet MCP** — instance `evergreen`, denní limit 24 000 requestů
- Vlastník aktivit se zjišťuje za běhu z přihlášeného uživatele Raynetu
- Pro bonitu: přístup k metodice bank (cíl: Evergreen app jako jediné místo, zatím Adamův vault `wiki/metodiky/`)
- Raynet plán Professional (limity: 50 automatizací za měsíc, 8 API klíčů, 25 povinných polí)

## Instalace

Skill je složka `pocket-to-raynet/`. Ve všech prostředích potřebuje připojené MCP servery **Hey Pocket** a **Raynet**.

- **Claude (claude.ai, desktop, mobil):** soubor `pocket-to-raynet.skill` otevřete v Claude a klikněte na **Save skill**.
  Vyrobíte ho z kořene repozitáře: `zip -r pocket-to-raynet.skill pocket-to-raynet -x '*/__pycache__/*'`
- **Claude Code:** `cp -r pocket-to-raynet ~/.claude/skills/`
- **Hermes Agent** ([Nous Research](https://hermes-agent.nousresearch.com/docs/)): čte skilly ve stejném formátu (standard
  agentskills.io). Zkopírujte složku do `~/.hermes/skills/` a připojte oba MCP servery. *Zatím nevyzkoušeno.*

## Nástroje

Čtyři skripty, jen standardní knihovna Pythonu 3, bez závislostí.

**Párování jmen** — `scripts/match_name.py`. Filtr `name` v Raynetu rozlišuje diakritiku, přepis bývá v pádě a cizí jména
jsou v CRM zapsaná foneticky. Skript z přepsaného jména vyrobí hledací výrazy (včetně českého přepisu: `Schneider` → `Šna…`)
a kandidáty seřadí foneticky. U klienta vedeného v CRM dvakrát odmítne být jistý. Verdikt se týká jen jména, druhý znak
(e-mail nebo telefon) se ověřuje zvlášť.

**Převod zápisu** — `scripts/md_to_raynet_html.py`. Raynet renderuje `description` a `solution` jako HTML; skript převede
Markdown, odstraní bloky `<pocket:chart>` a `<pocket:decision-tree>` a rediguje RČ a čísla účtů.

```bash
python3 pocket-to-raynet/scripts/md_to_raynet_html.py summary.md --recording-id <id>
python3 pocket-to-raynet/scripts/md_to_raynet_html.py summary.md --check   # režim „doslovně Pocket“
```

**Koncept e-mailu do pošty** — `scripts/make_email_draft.py`. Vyrobí `.eml` s hlavičkou `X-Unsent: 1`, takže se v Apple Mail
otevře jako koncept k úpravě, ne jako přijatá zpráva jen pro čtení. Nic se neodesílá.

**Audit log** — `scripts/audit_log.py`. Řádek za každou akci; přepis bez uloženého původního stavu odmítne. `stats` ukáže
u každého typu akce podíl návrhů potvrzených beze změny.

## Testy

```bash
python3 -m unittest discover -s tests -v
```

## Stav

Skill je ověřený **suchým během na reálných datech** (15 nahrávek z jednoho dne),
kde odhalil a nechal opravit šest chyb — mimo jiné dvě různé díry v detekci duplicit:

- hovor bývá v Raynetu uložený i jako **událost**, ne jen jako telefonát
- ručně zapsaný hovor má často `scheduledFrom: null`, takže ho časové okno nikdy nevrátí

1. 10. 2026 proběhl zkušební zápis na testovacího klienta. Ověřil, že Raynet odstraní `<table>` i `<pre>`
a že `status=COMPLETED` při založení nastaví čas dokončení na okamžik zápisu (skill ho hned opraví).

12. 10. 2026 proběhl **první ostrý zápis ke klientovi** (úvodní schůzka). Odhalil, že naplánovaná schůzka z kalendáře byla
v Raynetu typu **Událost**, která nemá v UI pole „Výsledek“, takže zápis nebyl na kartě klienta vidět. Doplněno tvrdé pravidlo 7
a větev A2 (zápis jen do Schůzky nebo Telefonátu), režim „doslovně Pocket“ s kontrolou `--check` a e-mail do chatu na pokyn.

12. 10. 2026 byl doplněn **úplný soupis polí Raynetu** podle Adamova manuálu (pole přečtená v Nastavení evidence, klíče
ověřené zápisem a čtením přes MCP) a kontroly 119 reálných OP: standardní pole klienta a OP, klíče všech vlastních polí
klienta i OP, přesné hodnoty roletek a formáty (`references/raynet-reference.md`). Skill podle toho plní víc vlastních
polí klienta (mapování „co zaznělo → klíč“ v šabloně karty klienta), čte pole typu Soubor jako přehled dodaných dokladů
a na výslovný pokyn vyplní i pole OP.
Podle Adamových rozhodnutí z 12. 10. 2026 skill zakládá OP, když hovor evidentně řeší konkrétní případ, přepočítá hrubou mzdu na
čistou a souhrnný úkol vede jako checklist `☐`/`☑`, který při dalších bězích odškrtává a posouvá termín úkolu na další otevřený bod.
