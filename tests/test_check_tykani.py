"""Tykání a vykání se v návrhu nesmí míchat (Adam, 12. 10. 2026). Jména jsou ilustrační."""

import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "pocket-to-raynet", "scripts"))

from check_tykani import check, main  # noqa: E402

VYKANI = """Dobrý den, pane Nováku,

navazuji na náš dnešní hovor. Abych Vám mohl přesně spočítat výši úvěru, poprosím Vás o podklady:
- daňové přiznání za poslední 2 roky

Vy jste zmiňoval i refinancování, to probereme příště.

Děkuji a přeji hezký den
"""

TYKANI = """Ahoj Petře,

posílám ti shrnutí. Mrkni na varianty a dej vědět, která ti víc sedí.
Kdyby něco, zavolej.

Díky, Adam
"""


class Vykani(unittest.TestCase):
    def test_spravne_vykani_je_ciste(self):
        self.assertEqual(check(VYKANI, "vykani"), [])

    def test_tykaci_sloveso_ve_vykani(self):
        nalezy = check(VYKANI + "\nPošli mi to prosím do pátku.\n", "vykani")
        self.assertEqual([w for _, w, _ in nalezy], ["Pošli"])

    def test_tykaci_zajmeno_a_pozdrav(self):
        nalezy = check("Ahoj,\n\nposílám Vám tvůj výpočet.\n", "vykani")
        self.assertEqual({w for _, w, _ in nalezy}, {"Ahoj", "tvůj"})

    def test_male_v_jednomu_cloveku(self):
        nalezy = check("Dobrý den, paní Nováková,\n\nposílám vám nabídku.\n", "vykani")
        self.assertEqual([w for _, w, _ in nalezy], ["vám"])

    def test_male_v_vice_prijemcum_je_spravne(self):
        text = "Dobrý den, pane Nováku, paní Nováková,\n\nposílám vám nabídku.\n"
        self.assertEqual(check(text, "vykani", prijemcu=2), [])


class Tykani(unittest.TestCase):
    def test_spravne_tykani_je_ciste(self):
        self.assertEqual(check(TYKANI, "tykani"), [])

    def test_velke_v_v_tykani(self):
        nalezy = check("Ahoj Petře,\n\nposílám Vám shrnutí.\n", "tykani")
        self.assertEqual([w for _, w, _ in nalezy], ["Vám"])

    def test_vykaci_sloveso_jednomu(self):
        nalezy = check("Ahoj Petře,\n\npošlete mi prosím výpisy.\n", "tykani")
        self.assertEqual([w for _, w, _ in nalezy], ["pošlete"])

    def test_mnozne_cislo_vice_prijemcum(self):
        text = "Ahoj Petře a Jano,\n\npošlete mi prosím výpisy, ať vám to spočítám.\n"
        self.assertEqual(check(text, "tykani", prijemcu=2), [])

    def test_oslovení_z_vykani(self):
        nalezy = check("Dobrý den, pane Nováku,\n\nposílám ti shrnutí.\n", "tykani")
        self.assertEqual(len(nalezy), 1)
        self.assertIn("oslovení", nalezy[0][2])


class Obecne(unittest.TestCase):
    def test_citace_se_nekontroluje(self):
        text = VYKANI + "\n> Ahoj Adame, pošli mi to.\n"
        self.assertEqual(check(text, "vykani"), [])

    def test_navratovy_kod(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(TYKANI)
        try:
            self.assertEqual(main(["--rezim", "tykani", f.name]), 0)
            self.assertEqual(main(["--rezim", "vykani", f.name]), 1)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
