"""Koncept e-mailu musí jít v Apple Mail upravit — to byla stížnost z hovoru 27. 9."""

import email
import os
import sys
import tempfile
import unittest
from email import policy

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "pocket-to-raynet", "scripts"))

import make_email_draft as m  # noqa: E402

BODY = """Dobrý den, pane Balente,

navazuji na náš dnešní hovor. Poprosím Vás o následující podklady:

**Příjmy fyzické osoby**
- daňové přiznání za poslední 2 roky
- výpis z účtu, kam chodí nájmy

S pozdravem
"""


def parse(msg):
    return email.message_from_bytes(msg.as_bytes(), policy=policy.default)


class Koncept(unittest.TestCase):
    def test_je_oznacen_jako_neodeslany(self):
        # Bez X-Unsent: 1 otevře Apple Mail .eml jako přijatou zprávu jen pro čtení.
        msg = parse(m.build(["klient@example.cz"], "Podklady", BODY))
        self.assertEqual(msg["X-Unsent"], "1")

    def test_ceska_diakritika_v_predmetu_a_tele(self):
        msg = parse(m.build(["klient@example.cz"], "Podklady k hypotéce – Žižkov", BODY))
        self.assertEqual(msg["Subject"], "Podklady k hypotéce – Žižkov")
        self.assertIn("Příjmy fyzické osoby", msg.get_body(("plain",)).get_content())
        self.assertIn("<b>Příjmy fyzické osoby</b>", msg.get_body(("html",)).get_content())

    def test_html_i_cisty_text(self):
        msg = parse(m.build(["klient@example.cz"], "Podklady", BODY))
        self.assertIsNotNone(msg.get_body(("plain",)))
        html = msg.get_body(("html",)).get_content()
        self.assertIn("<ul>", html)
        self.assertNotIn("**", html)

    def test_podpis_je_na_konci(self):
        msg = parse(m.build(["klient@example.cz"], "Podklady", BODY))
        plain = msg.get_body(("plain",)).get_content()
        self.assertTrue(plain.rstrip().endswith("www.egfin.cz"))
        self.assertIn("Bc. Adam Pospíšil", plain)

    def test_bez_podpisu(self):
        msg = parse(m.build(["klient@example.cz"], "Podklady", BODY, signature_path=None))
        self.assertNotIn("Jednatel", msg.get_body(("plain",)).get_content())

    def test_kopie_a_priloha(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 test")
        try:
            msg = parse(m.build(["klient@example.cz"], "Podklady", BODY,
                                cc=["martin.fiedor@egfin.cz"], attachments=[f.name]))
            self.assertEqual(msg["Cc"], "martin.fiedor@egfin.cz")
            names = [p.get_filename() for p in msg.iter_attachments()]
            self.assertIn(os.path.basename(f.name), names)
        finally:
            os.unlink(f.name)

    def test_citlive_udaje_se_v_emailu_neredigují(self):
        # V CRM se r.č. maže, ale e-mail bance ho může potřebovat.
        msg = parse(m.build(["banka@example.cz"], "Žádost", "Klient r.č. 880916/7027."))
        self.assertIn("880916/7027", msg.get_body(("plain",)).get_content())


if __name__ == "__main__":
    unittest.main()
