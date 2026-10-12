#!/usr/bin/env python3
"""Převede Pocket Summary (Markdown) na HTML, které Raynet zobrazí správně.

Raynet ukládá `description` a `solution` jako HTML. Markdown se v nich zobrazí
doslova, včetně `###` a `**`, takže převod je povinný krok před každým zápisem.

Pocket navíc do shrnutí vkládá vlastní bloky <pocket:chart> a <pocket:decision-tree>,
které mimo Pocket nedávají smysl. Skript je odstraní a z decision-tree zachová
alespoň textový obsah, aby se neztratila informace.

Použití:
    python3 md_to_raynet_html.py vstup.md
    python3 md_to_raynet_html.py < vstup.md
    cat summary.md | python3 md_to_raynet_html.py --strip-ids
    python3 md_to_raynet_html.py vstup.md --check   # režim „doslovně Pocket“: ověří shodu textu
"""

import argparse
import html
import re
import sys

# Značky, které Raynet v praxi zobrazuje (ověřeno na reálných záznamech).
# Nadpisy <h1>-<h6> se mezi nimi nevyskytují, proto se mapují na tučný odstavec.

RODNE_CISLO = re.compile(r"\b\d{6}\s?/\s?\d{3,4}\b")
CISLO_UCTU = re.compile(r"\b\d{1,6}-?\d{2,10}\s?/\s?\d{4}\b")


def strip_pocket_blocks(text: str) -> str:
    """Odstraní <pocket:*> bloky. Z decision-tree zachová textové řádky."""

    def keep_tree_text(match: re.Match) -> str:
        inner = match.group("inner")
        lines = []
        for raw in inner.splitlines():
            line = raw.strip()
            if not line:
                continue
            # 'uzel::otázka' -> 'otázka'; '- volba => cíl' -> '- volba'
            line = re.sub(r"^[\w-]+::", "", line)
            line = re.sub(r"\s*=>\s*\S+$", "", line)
            lines.append(line)
        return "\n".join(lines) + "\n" if lines else ""

    text = re.sub(
        r"<pocket:decision-tree[^>]*>(?P<inner>.*?)</pocket:decision-tree>",
        keep_tree_text,
        text,
        flags=re.DOTALL,
    )
    # Ostatní pocket bloky (chart a případné budoucí) zahodit celé.
    text = re.sub(r"<pocket:[^>]*>.*?</pocket:[^>]*>", "", text, flags=re.DOTALL)
    text = re.sub(r"<pocket:[^>]*/?>", "", text)
    return text


def redact(text: str) -> str:
    """Nahradí rodná čísla a čísla účtů. Finanční parametry ponechá."""
    text = RODNE_CISLO.sub("[r.č. odstraněno]", text)
    text = CISLO_UCTU.sub("[č. účtu odstraněno]", text)
    return text


def inline(text: str) -> str:
    """Escapuje HTML a převede inline Markdown (tučně, kurzíva, kód, odkazy)."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def convert(md: str, do_redact: bool = True) -> str:
    md = strip_pocket_blocks(md)
    if do_redact:
        md = redact(md)

    out: list[str] = []
    # Každá úroveň seznamu: [značka, odsazení, je otevřené <li>].
    # Vnořený seznam musí být uvnitř <li> rodiče, ne vedle něj — tak to má
    # Raynet i ve vlastních datech a jeho renderer na to spoléhá.
    stack: list[list] = []

    def close_lists(to_depth: int = 0) -> None:
        while len(stack) > to_depth:
            kind, _, li_open = stack.pop()
            if li_open:
                out.append("</li>")
            out.append(f"</{kind}>")

    for raw in md.splitlines():
        if not raw.strip():
            close_lists()
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        # Vodorovná čára a oddělovače se do CRM nehodí.
        if re.fullmatch(r"[-*_]{3,}", line):
            close_lists()
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            close_lists()
            out.append(f"<p><b>{inline(heading.group(2))}</b></p>")
            continue

        bullet = re.match(r"^[-*+]\s+(.*)$", line)
        numbered = re.match(r"^\d+[.)]\s+(.*)$", line)
        if bullet or numbered:
            kind = "ul" if bullet else "ol"
            content = (bullet or numbered).group(1)

            # Zpět z hlubších úrovní, pokud se odsazení zmenšilo.
            while len(stack) > 1 and indent < stack[-1][1]:
                closed_kind, _, li_open = stack.pop()
                if li_open:
                    out.append("</li>")
                out.append(f"</{closed_kind}>")

            if not stack or indent > stack[-1][1]:
                # Nová nebo vnořená úroveň — <li> rodiče zůstává otevřené,
                # aby se vnořený seznam ocitl uvnitř něj.
                out.append(f"<{kind}>")
                stack.append([kind, indent, False])
            elif stack[-1][0] != kind:
                # Přepnutí mezi odrážkami a číslováním na téže úrovni.
                closed_kind, _, li_open = stack.pop()
                if li_open:
                    out.append("</li>")
                out.append(f"</{closed_kind}>")
                out.append(f"<{kind}>")
                stack.append([kind, indent, False])
            elif stack[-1][2]:
                out.append("</li>")

            out.append(f"<li>{inline(content)}")
            stack[-1][2] = True
            continue

        close_lists()
        out.append(f"<p>{inline(line)}</p>")

    close_lists()
    return "\n".join(out)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def md_plain(md: str) -> str:
    """Čistý text Markdownu bez značek (stejná pravidla jako convert/inline)."""
    lines = []
    for raw in md.splitlines():
        line = raw.strip()
        if not line or re.fullmatch(r"[-*_]{3,}", line):
            continue
        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", line)
        line = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r"\1", line)
        line = line.replace("***", "").replace("**", "")
        line = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", line)
        line = re.sub(r"`(.+?)`", r"\1", line)
        lines.append(line)
    return _norm(" ".join(lines))


def html_plain(text: str) -> str:
    """Čistý text HTML bez značek. Inline značky zmizí beze stopy, blokové oddělí mezerou."""
    text = re.sub(r"</?(?:b|i|code|a|strong|em|span)\b[^>]*>", "", text)
    return _norm(html.unescape(re.sub(r"<[^>]+>", " ", text)))


def check_identical(md: str, result: str, do_redact: bool = True) -> tuple[bool, str]:
    """Ověří, že převod nezměnil text (režim „doslovně Pocket“).

    Porovnává se s Markdownem po odstranění <pocket:*> bloků a po redakci,
    protože ty dvě úpravy jsou záměrné.
    """
    source = strip_pocket_blocks(md)
    if do_redact:
        source = redact(source)
    a, b = md_plain(source), html_plain(result)
    if a == b:
        return True, "OK: text je shodný s originálem"
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return False, f"ROZDÍL na znaku {i}:\n  originál: …{a[max(0, i - 40):i + 40]}…\n  převod:   …{b[max(0, i - 40):i + 40]}…"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Převod Pocket Summary (Markdown) na HTML pro Raynet."
    )
    parser.add_argument("soubor", nargs="?", help="vstupní .md; bez něj se čte stdin")
    parser.add_argument(
        "--recording-id",
        help="připojí na konec stopu ke zdrojové nahrávce",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="ponechá rodná čísla a čísla účtů (výchozí je odstranit)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="ověří, že text bez značek je shodný s originálem (režim „doslovně Pocket“); "
        "výsledek kontroly jde na stderr, při rozdílu návratový kód 1",
    )
    args = parser.parse_args()

    md = open(args.soubor, encoding="utf-8").read() if args.soubor else sys.stdin.read()

    result = convert(md, do_redact=not args.no_redact)

    status = 0
    if args.check:
        ok, message = check_identical(md, result, do_redact=not args.no_redact)
        print(message, file=sys.stderr)
        status = 0 if ok else 1

    if args.recording_id:
        rid = html.escape(args.recording_id, quote=False)
        result += f"\n<p>— Zdroj: Pocket recording {rid} —</p>"

    print(result)
    return status


if __name__ == "__main__":
    sys.exit(main())
