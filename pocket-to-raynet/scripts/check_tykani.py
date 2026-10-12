#!/usr/bin/env python3
"""Hlídá, aby návrh zprávy dodržel tykání, nebo vykání, a tvary se nemíchaly.

Adam (12. 10. 2026): „striktně hlídej, komu tykám a komu vykám, a podle toho připravuj e-maily“.
Skript je poslední kontrola hotového textu, ne rozhodnutí: režim (tykání / vykání) určí skill
podle `references/email-style.md`, sekce „Tykání a vykání“. Návrh s jediným nálezem se uživateli
neukazuje, nejdřív se opraví.

Použití:
    python3 check_tykani.py --rezim vykani [--prijemcu 1] navrh.txt
    python3 check_tykani.py --rezim tykani --prijemcu 2 < navrh.txt

Výstup: jeden nález na řádek („ř. 3: „pošli“ – sloveso v 2. os. j. č. (tykání)“). Návratový kód
0 = čisté, 1 = nálezy. Citace předchozí zprávy (řádky začínající „>“) se nekontrolují.

Počet příjemců (`--prijemcu`) je počet oslovených v oslovení, ne lidí v kopii. Víc oslovených
při tykání znamená množné číslo „vy“ (malým), které je správně.
"""

import argparse
import re
import sys

# tvary 2. osoby jednotného čísla, které ve vykání nemají co dělat
TY_ZAJMENA = {
    "ty", "tebe", "tě", "ti", "tobě", "tebou",
    "tvůj", "tvoje", "tvá", "tvé", "tvého", "tvému", "tvém", "tvým", "tvými", "tvých", "tvou", "tvoji",
}
TY_SLOVESA = {
    "máš", "budeš", "můžeš", "musíš", "potřebuješ", "chceš", "víš", "jsi", "seš", "dáš", "pošleš",
    "napíšeš", "zavoláš", "uvidíš", "najdeš", "zvládneš", "pošli", "dej", "napiš", "zavolej", "ozvi",
    "mrkni", "koukni", "měj", "buď", "přijď", "vezmi", "podívej", "dodáš", "doložíš",
}
TY_POZDRAVY = {"ahoj", "čau", "čauky", "nazdar"}

# tvary zdvořilého vykání
VY_ZAJMENA = {
    "vy", "vás", "vám", "vámi", "váš", "vaše", "vaši", "vašeho", "vašemu", "vašem", "vaším", "vašim",
    "vašich", "vašimi",
}
VY_SLOVESA = {
    "máte", "budete", "můžete", "musíte", "potřebujete", "chcete", "víte", "jste", "dáte", "pošlete",
    "napíšete", "zavoláte", "uvidíte", "najdete", "zvládnete", "dejte", "napište", "zavolejte", "ozvěte",
    "mrkněte", "mějte", "buďte", "přijďte", "vezměte", "podívejte", "dodáte", "doložíte",
}
VY_OSLOVENI = re.compile(r"\b(dobrý den,?\s+(pane|paní)\b|vážen(ý|á|í)\b)", re.I)
TY_OSLOVENI = re.compile(r"\b(prosím tě|zdravím tě|díky ti|měj se)\b", re.I)

WORD = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)?")


def _sentence_start(text, pos):
    """Slovo na začátku věty nebo řádku (velké V tam nic neznamená)."""
    before = text[:pos].rstrip(" \t\"„“'(")
    return not before or before[-1] in ".!?:\n"


def check(text, rezim, prijemcu=1):
    """Vrátí seznam nálezů (číslo řádku, slovo, důvod)."""
    if rezim not in ("tykani", "vykani"):
        raise ValueError("rezim musí být 'tykani', nebo 'vykani'")
    nalezy = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(">"):
            continue
        if rezim == "vykani":
            for m in TY_OSLOVENI.finditer(line):
                nalezy.append((n, m.group(0), "obrat z tykání"))
        else:
            for m in VY_OSLOVENI.finditer(line):
                nalezy.append((n, m.group(0), "oslovení z vykání"))
        for m in WORD.finditer(line):
            w, low = m.group(0), m.group(0).lower()
            if rezim == "vykani":
                if low in TY_POZDRAVY:
                    nalezy.append((n, w, "pozdrav z tykání"))
                elif low in TY_ZAJMENA:
                    nalezy.append((n, w, "zájmeno 2. os. j. č. (tykání)"))
                elif low in TY_SLOVESA:
                    nalezy.append((n, w, "sloveso v 2. os. j. č. (tykání)"))
                elif low in VY_ZAJMENA and w[0].islower() and prijemcu == 1:
                    nalezy.append((n, w, "vykání jednomu člověku se píše s velkým V"))
            else:
                if low in VY_ZAJMENA:
                    if w[0].isupper() and not _sentence_start(line, m.start()):
                        nalezy.append((n, w, "zdvořilostní velké V (vykání)"))
                    elif prijemcu == 1:
                        nalezy.append((n, w, "zájmeno vy/váš jednomu člověku (vykání)"))
                elif low in VY_SLOVESA and prijemcu == 1:
                    nalezy.append((n, w, "sloveso v 2. os. mn. č. jednomu člověku (vykání)"))
    return nalezy


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rezim", required=True, choices=["tykani", "vykani"])
    ap.add_argument("--prijemcu", type=int, default=1, help="počet oslovených (ne lidí v kopii)")
    ap.add_argument("soubor", nargs="?", default="-")
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.soubor == "-" else open(a.soubor, encoding="utf-8").read()
    nalezy = check(text, a.rezim, a.prijemcu)
    for n, w, why in nalezy:
        print(f"ř. {n}: „{w}“ – {why}")
    if not nalezy:
        print(f"OK: {'tykání' if a.rezim == 'tykani' else 'vykání'} bez smíšených tvarů")
    return 1 if nalezy else 0


if __name__ == "__main__":
    sys.exit(main())
