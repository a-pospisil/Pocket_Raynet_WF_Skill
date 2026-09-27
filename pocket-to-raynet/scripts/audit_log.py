#!/usr/bin/env python3
"""Audit log každé akce, kterou skill udělá nebo navrhne.

Dvě věci, které log umožňuje:

1. **Zpětná kontrola.** Když robot udělá sto akcí za den, bez logu se nedá zjistit,
   co přesně kdy zapsal a proč. Každý řádek je jedna akce.

2. **Cesta zpět u přepisů.** Přes MCP neexistuje undo ani delete. Akce, které
   přepisují existující záznam (dokončení naplánovaného hovoru, změna OP),
   proto musí uložit stav **před** změnou — bez pole `before` se nezapíšou.
   Z logu se pak dá původní stav ručně vrátit.

A třetí, na které stojí rozhodnutí o vypnutí potvrzování: `stats` spočítá,
kolik návrhů uživatel potvrdil beze změny. Když je to u některého typu akce
dlouhodobě skoro všechno, je to kandidát na automatický režim.

Log je JSONL — jeden JSON objekt na řádek. Umístění:
    $POCKET_RAYNET_LOG, jinak ~/.pocket-to-raynet/audit.jsonl
Záměrně mimo repozitář: obsahuje jména a id klientů a nemá co dělat v gitu.

Použití:
    echo '{"action": "create_phonecall", "outcome": "confirmed", ...}' | audit_log.py append
    audit_log.py show [--date 2026-09-27] [--client 1071] [--recording ID] [--last 20]
    audit_log.py stats [--since 2026-09-01]
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

ACTIONS = {
    "create_phonecall",            # nový realizovaný telefonát
    "create_personal_activity",    # soukromý hovor jako osobní aktivita
    "complete_phonecall",          # dokončení naplánovaného — PŘEPIS
    "create_scheduled_phonecall",  # naplánovaný telefonát (follow-up)
    "create_task",
    "create_lead",                 # nový zájemce (fyzickou osobu jako klienta MCP neumí)
    "create_business_case",
    "update_business_case",        # změna OP, i zápis do evidence podkladů — PŘEPIS
    "draft_email",                 # jen soubor, nic se neodesílá
    "complete_action_item",        # uzavření action itemu v Pocketu
    "skip",                        # nahrávka vědomě nezapsána
    "escalate",                    # zastaveno, rozhoduje uživatel
}
OVERWRITES = {"complete_phonecall", "update_business_case"}

OUTCOMES = {
    "confirmed",  # navrženo a potvrzeno beze změny
    "edited",     # potvrzeno, ale uživatel něco opravil
    "rejected",   # navrženo a zamítnuto
    "auto",       # provedeno bez potvrzení (automatický režim)
    "skipped",    # pro action=skip / escalate
}

# Doporučení pro vypnutí potvrzování — rozhoduje uživatel, skript jen počítá.
READY_WINDOW = 20        # posledních N potvrzovaných návrhů daného typu
READY_MAX_CORRECTIONS = 1  # nejvýš tolik z nich smí být opraveno/zamítnuto

LABELS = {"confirmed": "potvrzeno", "edited": "upraveno", "rejected": "zamítnuto",
          "auto": "automaticky", "skipped": "přeskočeno"}


def log_path() -> str:
    return os.environ.get("POCKET_RAYNET_LOG") or os.path.expanduser(
        "~/.pocket-to-raynet/audit.jsonl")


def validate(rec: dict) -> list[str]:
    errors = []
    if rec.get("action") not in ACTIONS:
        errors.append(f"neznámá action {rec.get('action')!r}; povolené: {sorted(ACTIONS)}")
    if rec.get("outcome") not in OUTCOMES:
        errors.append(f"neznámý outcome {rec.get('outcome')!r}; povolené: {sorted(OUTCOMES)}")
    if rec.get("action") in OVERWRITES and rec.get("outcome") in ("confirmed", "edited", "auto"):
        if not isinstance(rec.get("before"), dict) or not rec["before"]:
            errors.append(
                f"{rec['action']} přepisuje existující záznam — chybí 'before' "
                "(stav polí před změnou, načti ho přes *_get). Bez něj nejde přepis vrátit.")
    if rec.get("mode", "confirm") not in ("confirm", "auto"):
        errors.append("mode musí být 'confirm' nebo 'auto'")
    return errors


def read_all() -> list[dict]:
    path = log_path()
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def cmd_append() -> int:
    payload = json.loads(sys.stdin.read())
    records = payload if isinstance(payload, list) else [payload]
    problems = []
    for i, rec in enumerate(records):
        problems += [f"záznam {i}: {e}" for e in validate(rec)]
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        for rec in records:
            rec = {"ts": now, "mode": "confirm", **rec}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"zapsáno {len(records)} → {path}")
    return 0


def fmt(rec: dict) -> str:
    parts = [
        rec.get("ts", "")[:16].replace("T", " "),
        f"{rec.get('action', ''):<27}",
        f"{LABELS.get(rec.get('outcome'), rec.get('outcome')):<11}",
    ]
    if rec.get("entity_id"):
        parts.append(f"{rec.get('entity', '')} {rec['entity_id']}")
    if rec.get("client_id"):
        parts.append(f"klient {rec['client_id']}")
    if rec.get("business_case_id"):
        parts.append(f"OP {rec['business_case_id']}")
    if rec.get("recording_id"):
        parts.append(f"nahrávka {rec['recording_id'][:12]}…")
    line = "  ".join(parts)
    if rec.get("note"):
        line += f"\n    {rec['note']}"
    if rec.get("before"):
        line += f"\n    před změnou: {json.dumps(rec['before'], ensure_ascii=False)}"
    return line


def cmd_show(a) -> int:
    rows = read_all()
    if a.date:
        rows = [r for r in rows if r.get("ts", "").startswith(a.date)]
    if a.client:
        rows = [r for r in rows if str(r.get("client_id")) == a.client]
    if a.recording:
        rows = [r for r in rows if r.get("recording_id") == a.recording]
    if a.last:
        rows = rows[-a.last:]
    if not rows:
        print("žádné záznamy")
    for r in rows:
        print(fmt(r))
    return 0


def cmd_stats(a) -> int:
    rows = read_all()
    if a.since:
        rows = [r for r in rows if r.get("ts", "") >= a.since]
    by_action = defaultdict(list)
    for r in rows:
        by_action[r.get("action")].append(r)
    if not by_action:
        print("žádné záznamy")
        return 0

    print(f"{'akce':<27}{'celkem':>7}{'potvrz.':>9}{'uprav.':>8}{'zamít.':>8}{'přesnost':>10}")
    for action in sorted(by_action):
        rs = by_action[action]
        counts = defaultdict(int)
        for r in rs:
            counts[r.get("outcome")] += 1
        reviewed = counts["confirmed"] + counts["edited"] + counts["rejected"]
        acc = f"{counts['confirmed'] / reviewed:.0%}" if reviewed else "—"
        print(f"{action:<27}{len(rs):>7}{counts['confirmed']:>9}{counts['edited']:>8}"
              f"{counts['rejected']:>8}{acc:>10}")

    print()
    for action in sorted(by_action):
        confirmed_mode = [r for r in by_action[action] if r.get("mode", "confirm") == "confirm"
                          and r.get("outcome") in ("confirmed", "edited", "rejected")]
        window = confirmed_mode[-READY_WINDOW:]
        if len(window) < READY_WINDOW:
            continue
        corrections = sum(r["outcome"] != "confirmed" for r in window)
        if corrections <= READY_MAX_CORRECTIONS:
            print(f"✓ {action}: z posledních {READY_WINDOW} návrhů opraveno {corrections} "
                  "→ kandidát na automatický režim (rozhoduje uživatel)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Audit log skillu Pocket → Raynet.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("append", help="zapíše záznam(y) ze stdin (JSON objekt nebo pole)")
    s = sub.add_parser("show", help="vypíše záznamy")
    s.add_argument("--date", help="YYYY-MM-DD")
    s.add_argument("--client")
    s.add_argument("--recording")
    s.add_argument("--last", type=int)
    st = sub.add_parser("stats", help="přesnost návrhů podle typu akce")
    st.add_argument("--since", help="YYYY-MM-DD")
    a = p.parse_args()
    if a.cmd == "append":
        return cmd_append()
    if a.cmd == "show":
        return cmd_show(a)
    return cmd_stats(a)


if __name__ == "__main__":
    sys.exit(main())
