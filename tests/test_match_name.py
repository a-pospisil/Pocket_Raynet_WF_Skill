"""Regresní testy párování jmen.

Každý případ je skutečná chyba přepisu, na kterou se narazilo v auditu,
suchém běhu nebo v hovoru o přípravě orchestrátoru. Kandidáti jsou reální
klienti z Raynetu (tests/fixtures/crm_sample.json).

Spuštění:  python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "pocket-to-raynet", "scripts"))

import match_name  # noqa: E402

CRM = os.path.join(HERE, "fixtures", "crm_sample.json")


def score(name):
    return match_name.cmd_score(name, [CRM])


class NajdeSpravnehoKlienta(unittest.TestCase):
    """Přepis je špatně, ale klient se musí najít."""

    def assertTop(self, query, expected_id, allowed=("jistý", "pravděpodobný")):
        r = score(query)
        top = r["candidates"][0]
        self.assertEqual(top["id"], expected_id, f"{query} → {top}")
        self.assertIn(r["verdict"], allowed, f"{query} → {r['verdict']} {r['candidates'][:3]}")

    def test_bretschneider_je_v_crm_foneticky(self):
        # Z hovoru 27. 9.: „klient Bretschneider … vůbec nevzalo to jméno".
        # V Raynetu je zapsaný jako „Jan Bretšnajdr".
        self.assertTop("Bretschneider", 124, allowed=("jistý",))
        self.assertTop("Jan Bretschneider", 124, allowed=("jistý",))

    def test_semrad_misto_semeraka(self):
        # Suchý běh: název nahrávky „Úvěr a bonita Jaroslav Semrád".
        self.assertTop("Jaroslav Semrád", 41)

    def test_nazev_nahravky_se_slovy_kolem_jmena(self):
        self.assertTop("Úvěr a bonita Jaroslav Semrád", 41)

    def test_balint_misto_balenta(self):
        self.assertTop("Petr Balint", 599)

    def test_hasolova_misto_hassove(self):
        self.assertTop("Jana Hasolová", 342)

    def test_pad_a_domacka_podoba(self):
        # „Hovor s Honzou Rumlem" — 7. pád a Honza = Jan. Tři další Rumlové v CRM.
        self.assertTop("Honzou Rumlem", 379, allowed=("jistý",))

    def test_pad_a_obracene_poradi(self):
        # „Storno hypotéky s Tomášem Jozefem" — v CRM „Tomáš Josef".
        self.assertTop("Tomášem Jozefem", 1071)

    def test_krestni_jmeno_rozlisi_bratry(self):
        # „Martin Gajdušek" — v CRM Martin i Michal Gajdošech.
        self.assertTop("Martin Gajdušek", 39)

    def test_osoba_ne_jeji_firma(self):
        # Milan Čálek a jeho Calek Invest s.r.o. sdílejí e-mail.
        self.assertTop("Milanem Čálkem", 54)

    def test_prechylene_prijmeni(self):
        self.assertTop("Fenni Gergelyovou", 1082)


class NesmiBytJisty(unittest.TestCase):
    """Tady by jistota znamenala zápis ke špatnému záznamu."""

    def test_duplicitni_klient(self):
        # Zbyněk Svoboda je v CRM dvakrát (613 a 603), stejný e-mail.
        r = score("Zbyněk Svoboda")
        self.assertEqual(r["verdict"], "nejistý")
        self.assertEqual({c["id"] for c in r["candidates"][:2]}, {613, 603})

    def test_dve_osoby_stejneho_jmena(self):
        r = score("Michal Huml")
        self.assertEqual(r["verdict"], "nejistý")

    def test_jen_prijmeni_u_rodiny(self):
        r = score("Pospíšilová")
        self.assertEqual(r["verdict"], "nejistý")

    def test_klient_ktery_v_crm_neni(self):
        # Suchý běh: „Robert Tomaszewicz" — v CRM není.
        self.assertEqual(score("Robert Tomaszewicz")["verdict"], "žádný")


class HledaciVyrazy(unittest.TestCase):
    """Výrazy pro company_list(name=…), který rozlišuje diakritiku."""

    def variants(self, name):
        return match_name.cmd_variants(name)

    def test_odstrani_pad(self):
        v = self.variants("Honzou Rumlem")
        self.assertEqual(v["surname_variants"][0], "Ruml")
        self.assertIn("Jan", v["first_name_fallback"])

    def test_prefix_bez_diakritiky_i_s_ni(self):
        # Ověřeno: name="Calek" nenajde „Milan Čálek", name="Čál" ano.
        v = self.variants("Milanem Čálkem")["surname_variants"]
        self.assertIn("Čál", v)
        self.assertIn("Cal", v)

    def test_prefix_najde_foneticky_zapis(self):
        # Ověřeno: name="Bret" najde „Jan Bretšnajdr".
        self.assertIn("Bret", self.variants("Bretschneider")["surname_variants"])

    def test_prefix_najde_prepis_se_spatnym_koncem(self):
        # Ověřeno: name="Semr" → 0, name="Sem…" najde Semeráka.
        self.assertIn("Sem", self.variants("Jaroslav Semrád")["surname_variants"])


if __name__ == "__main__":
    unittest.main()
