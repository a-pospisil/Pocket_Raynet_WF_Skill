# Formátování textu pro Raynet

Otevři tenhle soubor, když sestavuješ HTML ručně mimo `scripts/md_to_raynet_html.py`
— typicky při krátké poznámce nebo při úpravě už zapsaného textu.

## Která pole jsou HTML

Ověřeno čtením reálných záznamů, ne odhadem:

| Pole | Formát | Doklad z dat |
|---|---|---|
| `phonecall.solution` | **HTML** | `<p>Úvodní schůzka s…</p>` |
| `phonecall.description` | **HTML** | `Záměr: …<br><br>Bonita: …` |
| `task.solution` | **HTML** | `<p>zaslána nabídka účelové…</p>` |
| `meeting.description` | **HTML** | `<p>lepší komentář k yoy nárůstu…</p>` |
| `company.notice` | **HTML** | `"<p>\n<br>\n</p>"` |
| `*.title`, `businessCase.name` | **prostý text** | bez značek ve všech vzorcích |
| `tags` | prostý text, čárkami | `"Import 18.9.2026 #1,Broker Trust"` |

Markdown se v HTML polích **nezpracovává**. Zapsané `### Nadpis` a `**tučně**`
se v CRM zobrazí doslova i s těmi znaky.

## Co Raynet renderuje

Doloženo z existujících záznamů:

| Prvek | Značka |
|---|---|
| Odstavec | `<p>…</p>` |
| Zalomení řádku | `<br>` |
| Tučně | `<b>…</b>` |
| Kurzíva | `<i>…</i>` |
| Odrážky | `<ul><li>…</li></ul>` |
| Číslovaný seznam | `<ol><li>…</li></ol>` |
| Odkaz | `<a href="…">…</a>` |
| Blok | `<div>…</div>` |

Inline `style` atributy v datech reálně jsou (`<li style="margin: 0">`), takže se
HTML nesanitizuje agresivně. Spoléhat se na to ale nemá smysl — vystač si s výčtem výše.

## Co nepoužívat

- **`<h1>`–`<h6>`** se v žádném existujícím záznamu nevyskytují. Nadpis dělej jako
  `<p><b>Text</b></p>` — tak to vypadá i ve výstupech, které do CRM píše člověk.
- **`<hr>`** a vodorovné oddělovače — v datech nejsou a v úzkém sloupci aktivity
  působí rušivě.
- **Tabulky** (`<table>`) — nevyzkoušené a v detailu aktivity se stejně nevejdou.
- **Markdown v jakékoli podobě.**

## Vnořené seznamy

Vnořený seznam patří **dovnitř** rodičovského `<li>`, ne vedle něj. Takhle to má
Raynet ve vlastních datech:

```html
<ul>
<li><b>Varianta A:</b>
<ul>
<li>Splatnost 30 let</li>
<li>Sazba 6,2 %</li>
</ul>
</li>
<li><b>Varianta B:</b> …</li>
</ul>
```

Skript `md_to_raynet_html.py` to řeší; při ručním psaní na to pozor.

## Escapování

Text z přepisu může obsahovat `&`, `<` a `>`. Escapuj je na `&amp;`, `&lt;`, `&gt;`,
jinak se kus textu ztratí nebo rozbije značkování. Skript to dělá automaticky.

## Citlivé údaje

Přepisy hovorů obsahují **rodná čísla, čísla účtů a zůstatky úvěrů**. Do CRM patří
pracovní parametry případu — výše úvěru, LTV, sazba, bonita, příjmy. Nepatří tam
rodná čísla a čísla bankovních účtů; skript je nahrazuje značkou
`[r.č. odstraněno]` / `[č. účtu odstraněno]`.

Pokud text sestavuješ ručně, udělej totéž. Vypnout to jde přepínačem `--no-redact`,
ale bez výslovného pokynu uživatele k tomu není důvod.

## Stopa ke zdroji

Na konec `description` patří řádek, podle kterého se dá záznam dohledat zpět
k nahrávce:

```html
<p>— Zdroj: Pocket recording 36d473d6-c7c5-46fc-8d55-1211085af00c —</p>
```

Slouží k auditu a ruční kontrole. **Není to mechanismus proti duplicitám** — na ten
se používá časový otisk přes `phonecall_list`, protože `fulltext` matchuje celá slova
a prefixy a dohledatelnost celého UUID není ověřená.

Skript řádek přidá přepínačem `--recording-id <id>`.
