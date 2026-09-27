"""Audit log: každá akce dohledatelná, každý přepis vratný."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "pocket-to-raynet", "scripts"))

import audit_log  # noqa: E402


class Log(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["POCKET_RAYNET_LOG"] = os.path.join(self.tmp.name, "audit.jsonl")

    def tearDown(self):
        self.tmp.cleanup()
        del os.environ["POCKET_RAYNET_LOG"]

    def append(self, payload):
        sys.stdin = io.StringIO(json.dumps(payload))
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = audit_log.cmd_append()
        sys.stdin = sys.__stdin__
        return code, err.getvalue()

    def test_zapis_a_cteni(self):
        code, _ = self.append({"action": "create_phonecall", "outcome": "confirmed",
                               "entity": "phonecall", "entity_id": 35927, "client_id": 54})
        self.assertEqual(code, 0)
        rows = audit_log.read_all()
        self.assertEqual(rows[0]["entity_id"], 35927)
        self.assertEqual(rows[0]["mode"], "confirm")
        self.assertIn("ts", rows[0])

    def test_prepis_bez_puvodniho_stavu_neprojde(self):
        # Dokončení naplánovaného hovoru přepisuje existující záznam.
        code, err = self.append({"action": "complete_phonecall", "outcome": "confirmed",
                                 "entity": "phonecall", "entity_id": 30517})
        self.assertEqual(code, 1)
        self.assertIn("before", err)
        self.assertEqual(audit_log.read_all(), [])

    def test_prepis_s_puvodnim_stavem_projde(self):
        code, _ = self.append({
            "action": "complete_phonecall", "outcome": "confirmed",
            "entity": "phonecall", "entity_id": 30517,
            "before": {"status": "SCHEDULED", "scheduledFrom": "2026-09-22 14:30"},
            "after": {"status": "COMPLETED", "scheduledFrom": "2026-09-22 15:28"},
        })
        self.assertEqual(code, 0)

    def test_zamitnuty_prepis_nepotrebuje_puvodni_stav(self):
        # Nic se nezměnilo, není co vracet.
        code, _ = self.append({"action": "complete_phonecall", "outcome": "rejected"})
        self.assertEqual(code, 0)

    def test_zapis_do_evidence_podkladu_je_prepis(self):
        # Doplnění oddílu PODKLADY v popisu OP přepisuje celé pole description.
        code, err = self.append({"action": "update_business_case", "outcome": "confirmed",
                                 "entity": "businessCase", "entity_id": 469})
        self.assertEqual(code, 1)
        self.assertIn("before", err)

    def test_novy_lead_a_soukromy_hovor(self):
        code, _ = self.append([
            {"action": "create_lead", "outcome": "confirmed", "entity": "lead", "entity_id": 301},
            {"action": "create_personal_activity", "outcome": "confirmed", "entity": "phonecall"},
        ])
        self.assertEqual(code, 0)

    def test_neznama_akce(self):
        code, _ = self.append({"action": "delete_everything", "outcome": "auto"})
        self.assertEqual(code, 1)

    def test_kandidat_na_automaticky_rezim(self):
        batch = [{"action": "create_phonecall", "outcome": "confirmed"} for _ in range(19)]
        batch.append({"action": "create_phonecall", "outcome": "edited"})
        self.append(batch)
        out = io.StringIO()
        with redirect_stdout(out):
            audit_log.cmd_stats(type("A", (), {"since": None})())
        self.assertIn("kandidát na automatický režim", out.getvalue())

    def test_malo_dat_neni_kandidat(self):
        self.append([{"action": "create_phonecall", "outcome": "confirmed"} for _ in range(5)])
        out = io.StringIO()
        with redirect_stdout(out):
            audit_log.cmd_stats(type("A", (), {"since": None})())
        self.assertNotIn("kandidát", out.getvalue())


if __name__ == "__main__":
    unittest.main()
