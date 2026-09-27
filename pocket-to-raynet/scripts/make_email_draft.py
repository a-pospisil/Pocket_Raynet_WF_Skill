#!/usr/bin/env python3
"""Připraví e-mail jako koncept, který jde v Apple Mail rovnou upravit a odeslat.

Proč ne obyčejný .eml: Apple Mail (i Outlook) otevře .eml soubor jako **přijatou**
zprávu — jen pro čtení, text se musí kopírovat jinam. Hlavička `X-Unsent: 1`
říká, že jde o neodeslaný koncept, a klient ho otevře v okně pro psaní,
kde jde všechno upravit.

E-mail se nikdy neodesílá. Skript jen vyrobí soubor; odeslání je vždy na člověku.

Použití:
    python3 make_email_draft.py --to klient@example.cz --subject "Podklady k hypotéce" \\
            --body telo.md [--cc kolega@egfin.cz] [--attach seznam.pdf] [--out koncept.eml]

Tělo se píše v Markdownu (odstavce, odrážky, **tučně**) a převede se na HTML
i na čistý text. Podpis se připojí z assets/signature.txt, pokud nedáte --no-signature.
Oslovení a rozloučení („S pozdravem") patří do těla — liší se podle klienta.
"""

import argparse
import html
import mimetypes
import os
import re
import sys
import unicodedata
from email.message import EmailMessage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from md_to_raynet_html import convert  # noqa: E402

DEFAULT_SIGNATURE = os.path.join(HERE, "..", "assets", "signature.txt")


def md_to_plain(md: str) -> str:
    text = re.sub(r"^#{1,6}\s+", "", md, flags=re.M)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r"\1 (\2)", text)
    return text.strip() + "\n"


def signature_html(lines: list[str]) -> str:
    out = []
    for line in lines:
        esc = html.escape(line, quote=False)
        if re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.]+", line):
            esc = f'<a href="mailto:{esc}">{esc}</a>'
        elif re.fullmatch(r"www\.[\w.-]+", line):
            esc = f'<a href="https://{esc}">{esc}</a>'
        out.append(esc)
    return "<p>" + "<br>\n".join(out) + "</p>"


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text)[:60] or "koncept"


def build(to, subject, body_md, cc=(), bcc=(), attachments=(), sender=None,
          signature_path=DEFAULT_SIGNATURE) -> EmailMessage:
    msg = EmailMessage()
    if sender:
        msg["From"] = sender
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = subject
    # Klíčová hlavička: koncept, ne přijatá zpráva → otevře se k úpravě.
    msg["X-Unsent"] = "1"

    plain = md_to_plain(body_md)
    # Do e-mailu klientovi se citlivé údaje neredigují — může je potřebovat
    # (např. banka číslo účtu). Redakce platí pro zápis do CRM, ne sem.
    body_html = convert(body_md, do_redact=False)

    if signature_path:
        with open(signature_path, encoding="utf-8") as f:
            sig = [line.rstrip() for line in f.read().strip().splitlines()]
        plain += "\n" + "\n".join(sig) + "\n"
        body_html += "\n" + signature_html(sig)

    msg.set_content(plain)
    msg.add_alternative(f"<html><body>\n{body_html}\n</body></html>\n", subtype="html")

    for path in attachments:
        ctype, _ = mimetypes.guess_type(path)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype,
                               filename=os.path.basename(path))
    return msg


def main() -> int:
    p = argparse.ArgumentParser(description="E-mail jako upravitelný koncept (.eml s X-Unsent: 1).")
    p.add_argument("--to", action="append", required=True, help="příjemce; lze opakovat")
    p.add_argument("--cc", action="append", default=[])
    p.add_argument("--bcc", action="append", default=[])
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True, help="soubor s tělem v Markdownu, nebo - pro stdin")
    p.add_argument("--attach", action="append", default=[])
    p.add_argument("--from", dest="sender", help="odesílatel; bez něj použije Mail výchozí účet")
    p.add_argument("--signature", default=DEFAULT_SIGNATURE)
    p.add_argument("--no-signature", action="store_true")
    p.add_argument("--out", help="výstupní soubor; výchozí je koncept-<předmět>.eml")
    a = p.parse_args()

    body = sys.stdin.read() if a.body == "-" else open(a.body, encoding="utf-8").read()
    msg = build(a.to, a.subject, body, a.cc, a.bcc, a.attach, a.sender,
                None if a.no_signature else a.signature)

    out = a.out or f"koncept-{slug(a.subject)}.eml"
    with open(out, "wb") as f:
        f.write(msg.as_bytes())
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
