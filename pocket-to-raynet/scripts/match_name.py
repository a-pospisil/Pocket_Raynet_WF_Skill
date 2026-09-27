#!/usr/bin/env python3
"""Dohledání klienta podle jména, které Pocket přepsal z hovoru.

Pocket jména komolí — `Balint` místo `Balent`, `Semrád` místo `Semerák`,
a německé jméno `Bretschneider` je v Raynetu zapsané foneticky jako `Bretšnajdr`.
Přímé hledání pak nenajde nic a klient se zapíše špatně nebo vůbec.

Skript řeší obě půlky problému:

  variants   Z přepsaného jména udělá pár hledacích výrazů pro `company_list(name=…)`.
             Filtr `name` v Raynetu je substring bez ohledu na velikost písmen, ale
             **rozlišuje diakritiku** (`Calek` nenajde `Čálek`), a přepis často
             obsahuje pád („s Honzou Rumlem"). Výrazy proto zkracuje na kmen a prefix.

  score      Seřadí kandidáty z Raynetu podle podobnosti a řekne, jak moc si je jistý.
             Porovnává foneticky (sch→š, ei→aj, y→i, zdvojená písmena), bez diakritiky,
             bez titulů, bez ohledu na pořadí jména a příjmení, a zná domácké podoby
             křestních jmen (Honza = Jan).

Verdikt řídí, co skill udělá dál:
  jistý          pokračuj
  pravděpodobný  pokračuj, ale v návrhu zápisu shodu viditelně označ
  nejistý        zeptej se uživatele
  žádný          klient v CRM nejspíš není

Použití:
    python3 match_name.py variants "Honzou Rumlem"
    python3 match_name.py score "Jaroslav Semrád" kandidati.json [další.json …]
    cat odpoved_company_list.json | python3 match_name.py score "Jaroslav Semrád" -

Kandidáti se berou přímo z odpovědi `company_list` / `lead_list` (objekt s polem
`data`), nebo jako prostý seznam záznamů. Víc souborů se sloučí a deduplikuje podle id.
"""

import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher

TITLES = {
    "ing", "mgr", "bc", "judr", "mudr", "mddr", "mvdr", "phdr", "rndr", "paeddr",
    "phd", "csc", "drsc", "mba", "msc", "llm", "dis", "doc", "prof", "dr", "ma", "bba",
    "ll", "ph", "spol",
}

# Slova, která se v názvu nahrávky objevují kolem jména a jménem nejsou.
STOPWORDS = {
    "s", "se", "z", "ze", "pro", "od", "do", "k", "ke", "a", "o", "na", "u",
    "pan", "pán", "pana", "panu", "panem", "paní", "slečna",
    "klient", "klienta", "klientem", "klientka", "klientkou",
    "hovor", "telefon", "telefonát", "call", "konzultace", "schůzka", "ohledně",
}

# Domácké podoby → občanské jméno. Jen jednoznačné páry.
NICKNAMES = {
    "honza": "jan", "honzík": "jan", "jenda": "jan", "pepa": "josef", "pepík": "josef",
    "franta": "františek", "jirka": "jiří", "kuba": "jakub", "vašek": "václav",
    "venca": "václav", "standa": "stanislav", "míra": "miroslav", "mirek": "miroslav",
    "tonda": "antonín", "péťa": "petr", "peter": "petr", "zdenda": "zdeněk",
    "jarda": "jaroslav", "láďa": "ladislav", "vláďa": "vladimír", "ondra": "ondřej",
    "vojta": "vojtěch", "luboš": "lubomír", "katka": "kateřina", "káťa": "kateřina",
    "bára": "barbora", "verča": "veronika", "zuzka": "zuzana", "lucka": "lucie",
    "evča": "eva", "evička": "eva", "maruška": "marie", "dáša": "dagmar",
}

SURE, PROBABLE, UNSURE = 0.85, 0.70, 0.60
SURE_MARGIN, PROBABLE_MARGIN = 0.15, 0.10


def fold(text: str) -> str:
    """Odstraní diakritiku."""
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )


def phonetic(token: str) -> str:
    """Klíč pro porovnání: jak slovo zní, ne jak je napsané.

    Nejdřív převede cizí hlásky na české (Bretschneider → bretšnajder;
    `t` před `sch` zůstává, česky se píše Bret-šnajdr),
    teprve pak odstraní diakritiku — jinak by se š z `sch` ztratilo dřív,
    než vznikne.
    """
    s = token.lower()
    for src, dst in (
        ("sch", "š"), ("sh", "š"), ("tz", "c"), ("ck", "k"),
        ("ph", "f"), ("th", "t"), ("qu", "kv"), ("w", "v"), ("x", "ks"),
        ("ei", "aj"), ("eu", "oj"), ("äu", "oj"), ("ie", "i"),
        ("ä", "e"), ("ö", "e"), ("ü", "i"), ("ý", "í"), ("y", "i"),
    ):
        s = s.replace(src, dst)
    s = fold(s)
    s = re.sub(r"[^a-z]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)  # Hassová → hasova


def base_forms(token: str) -> set[str]:
    """Možné základní tvary slova, které může být v pádě.

    Přepis zachytí „s Honzou Rumlem" nebo „Pavlu Sýkorovi", v CRM je ale 1. pád.
    Vrací víc kandidátů; skóre se pak bere přes nejlepší z nich.
    """
    t = token.lower()
    forms = {t}
    for suffix, repl in (("ovou", "ová"), ("ové", "ová"), ("ovej", "ová")):
        if t.endswith(suffix):
            forms.add(t[: -len(suffix)] + repl)
    if len(t) > 4:
        if t.endswith("ovi"):
            forms.update({t[:-3], t[:-3] + "a"})       # Balentovi, Sýkorovi
        if t.endswith("em"):
            forms.add(t[:-2])                          # Rumlem, Kubíkem
        if t.endswith("ou"):
            forms.add(t[:-2] + "a")                    # Honzou → Honza
        if t.endswith("u") and len(t) > 5:
            forms.add(t[:-1])                          # Pavlu
        if t.endswith("a"):
            forms.add(t[:-1])                          # Balenta (2. pád)
    # Pohyblivé e: Čálkem → čálk → čálek, Pavlu → pavl → pavel.
    for f in list(forms):
        if len(f) >= 3 and re.search(r"[^aeiouyáéěíóúůý][^aeiouyáéěíóúůý]$", f):
            forms.add(f[:-1] + "e" + f[-1])
    return forms


def tokens_of(name: str, is_query: bool = False) -> list[str]:
    """Rozdělí jméno na slova bez titulů, interpunkce a přípon za čárkou."""
    if is_query:
        bracket = re.search(r"\[([^\]]+)\]", name)   # Pocket: „Konzultace [Peter Balent]"
        if bracket:
            name = bracket.group(1)
    name = re.sub(r"[\[\]()_]", " ", name)
    if not is_query:
        name = name.split(",")[0]                      # „…, advokátní kancelář"
    raw = re.findall(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", name)
    # Tituly a zbytky právních forem („s.r.o." se rozpadne na s, r, o).
    words = [w for w in raw if len(w) > 1 and fold(w.lower()) not in TITLES]
    if is_query:
        kept = [w for w in words if w.lower() not in STOPWORDS]
        # Z delší fráze („Úvěr a bonita Jaroslav Semrád") vezmi poslední dvě slova
        # s velkým písmenem. Velké bývá i první slovo věty, proto ne všechna.
        if len(kept) > 2:
            capital = [w for w in kept if w[:1].isupper()] or kept
            kept = capital[-2:]
        words = kept
    return words


def sim(query_word: str, cand_word: str) -> float:
    cand = phonetic(cand_word)
    if not cand:
        return 0.0
    best = 0.0
    for form in base_forms(query_word):
        for f in {form, NICKNAMES.get(form, form)}:
            best = max(best, SequenceMatcher(None, phonetic(f), cand).ratio())
    cand_nick = NICKNAMES.get(cand_word.lower())
    if cand_nick:
        best = max(best, SequenceMatcher(None, phonetic(query_word), phonetic(cand_nick)).ratio())
    return best


def score_candidate(query: list[str], cand: list[str]) -> float:
    """Skóre 0–1. Příjmení váží 75 %, křestní jméno 25 %.

    Pořadí se nepředpokládá: v Raynetu je „Tomáš Josef" i „Pospíšilová Vladislava",
    takže se zkouší každé přiřazení a bere se nejlepší.
    """
    if not query or not cand:
        return 0.0
    if len(query) == 1:
        return max(sim(query[0], c) for c in cand)
    surname, first = query[-1], query[0]
    if len(cand) == 1:
        return 0.9 * sim(surname, cand[0])
    best = 0.0
    for i, c_surname in enumerate(cand):
        for j, c_first in enumerate(cand):
            if i == j:
                continue
            best = max(best, 0.75 * sim(surname, c_surname) + 0.25 * sim(first, c_first))
    return best


def candidate_name(rec: dict) -> str:
    for key in ("name", "companyName", "topic"):
        if rec.get(key):
            return rec[key]
    return " ".join(x for x in (rec.get("firstName"), rec.get("lastName")) if x)


def candidate_email(rec: dict):
    return (
        rec.get("email")
        or (rec.get("primaryAddress") or {}).get("email")
        or rec.get("contactInfo.email")
    )


def load_candidates(paths: list[str]) -> list[dict]:
    seen, out = set(), []
    for path in paths:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        data = json.loads(text)
        rows = data.get("data", []) if isinstance(data, dict) else data
        for rec in rows:
            key = rec.get("id", id(rec))
            if key not in seen:
                seen.add(key)
                out.append(rec)
    return out


def verdict(ranked: list[dict]) -> str:
    if not ranked or ranked[0]["score"] < UNSURE:
        return "žádný"
    top = ranked[0]["score"]
    second = ranked[1]["score"] if len(ranked) > 1 else 0.0
    if top >= SURE and top - second >= SURE_MARGIN:
        return "jistý"
    if top >= PROBABLE and top - second >= PROBABLE_MARGIN:
        return "pravděpodobný"
    return "nejistý"


def cmd_score(name: str, paths: list[str]) -> dict:
    query = tokens_of(name, is_query=True)
    ranked = []
    for rec in load_candidates(paths):
        cname = candidate_name(rec)
        s = score_candidate(query, tokens_of(cname))
        ranked.append({
            "id": rec.get("id"),
            "name": cname,
            "email": candidate_email(rec),
            "score": round(s, 3),
        })
    ranked.sort(key=lambda r: r["score"], reverse=True)
    v = verdict(ranked)
    advice = {
        "jistý": "Pokračuj s nejlepším kandidátem.",
        "pravděpodobný": "Pokračuj, ale v návrhu zápisu shodu viditelně označ.",
        "nejistý": "Zeptej se uživatele — předlož kandidáty.",
        "žádný": "Klient v CRM nejspíš není. Zkus další hledací výrazy nebo lead_list.",
    }[v]
    return {"query": name, "tokens": query, "verdict": v, "advice": advice,
            "candidates": ranked[:5]}


def toggle_hacek(prefix: str):
    pairs = {"c": "č", "s": "š", "z": "ž", "r": "ř", "č": "c", "š": "s", "ž": "z", "ř": "r"}
    first = prefix[0]
    swapped = pairs.get(first.lower())
    if not swapped:
        return None
    return (swapped.upper() if first.isupper() else swapped) + prefix[1:]


def cmd_variants(name: str) -> dict:
    """Hledací výrazy pro company_list(name=…), od nejužšího po nejširší."""
    words = tokens_of(name, is_query=True)
    if not words:
        return {"query": name, "variants": []}
    surname = words[-1]
    stem = min(base_forms(surname), key=len)
    stem = stem[:1].upper() + stem[1:]

    out = [stem]
    for n in (4, 3):
        if len(stem) > n:
            out.append(stem[:n])
    short = stem[:3]
    toggled = toggle_hacek(short)
    if toggled:
        out.append(toggled)
    folded = fold(short)
    if folded != short:
        out.append(folded)

    seen, variants = set(), []
    for v in out:
        if len(v) >= 3 and v.lower() not in seen:
            seen.add(v.lower())
            variants.append(v)

    first_names = []
    if len(words) > 1:
        forms = base_forms(words[0])
        names = {NICKNAMES[f] for f in forms if f in NICKNAMES} or {min(forms, key=len)}
        first_names = sorted(n[:1].upper() + n[1:] for n in names if len(n) >= 3)

    return {
        "query": name,
        "surname_variants": variants,
        "first_name_fallback": first_names,
        "note": "Filtr name rozlišuje diakritiku. Zkoušej varianty postupně; "
                "křestní jméno jen jako poslední možnost, vrací hodně záznamů.",
    }


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("score", "variants"):
        print(__doc__, file=sys.stderr)
        return 2
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == "variants":
        result = cmd_variants(name)
    else:
        if len(sys.argv) < 4:
            print("score potřebuje aspoň jeden soubor s kandidáty (nebo - pro stdin)",
                  file=sys.stderr)
            return 2
        result = cmd_score(name, sys.argv[3:])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
