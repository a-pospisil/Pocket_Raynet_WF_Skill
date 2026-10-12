"""Regresní testy párování jmen.

Jména a id jsou ilustrační (tests/fixtures/crm_sample.json), ale každý případ
nese stejný typ chyby přepisu, na jaký se narazilo v provozu: cizí jméno zapsané
v CRM foneticky, záměna písmen, pád, domácké jméno, duplicita, osoba vs. její firma.

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

    def test_cizi_jmeno_zapsane_v_crm_foneticky(self):
        # Z hovoru 27. 9.: německé jméno „… vůbec nevzalo"; v CRM je zapsané foneticky.
        self.assertTop("Schneider", 9112, allowed=("jistý",))
        self.assertTop("Jan Schneider", 9112, allowed=("jistý",))

    def test_zamena_pismen_uprostred_prijmeni(self):
        self.assertTop("Jaroslav Lemrád", 9102)

    def test_nazev_nahravky_se_slovy_kolem_jmena(self):
        self.assertTop("Úvěr a bonita Jaroslav Lemrád", 9102)

    def test_nazev_nahravky_se_jmenem_v_zavorkach(self):
        self.assertTop("Konzultace a výpočet [Peter Kolent]", 9101, allowed=("jistý",))

    def test_zamena_samohlasky(self):
        self.assertTop("Petr Kolint", 9101)

    def test_vlozena_slabika_a_zdvojene_pismeno(self):
        self.assertTop("Jana Basolová", 9110)

    def test_pad_a_domacka_podoba(self):
        # „Hovor s Honzou Kumlem" — 7. pád a Honza = Jan. Tři další Kumlové v CRM.
        self.assertTop("Honzou Kumlem", 9113, allowed=("jistý",))

    def test_pad_zamena_z_s_a_obracene_poradi(self):
        self.assertTop("Lukášem Jozefem", 9109)

    def test_krestni_jmeno_rozlisi_bratry(self):
        # V CRM Martin i Michal Bajdošech.
        self.assertTop("Martin Bajdušek", 9103)

    def test_osoba_ne_jeji_firma(self):
        # Milan Čápek a jeho Capek Invest s.r.o.
        self.assertTop("Milanem Čápkem", 9106)

    def test_prechylene_prijmeni_v_pade(self):
        self.assertTop("Fanni Szekelyovou", 9105)


class NesmiBytJisty(unittest.TestCase):
    """Tady by jistota znamenala zápis ke špatnému záznamu."""

    def test_duplicitni_klient(self):
        r = score("Zbyněk Dvořák")
        self.assertEqual(r["verdict"], "nejistý")
        self.assertEqual({c["id"] for c in r["candidates"][:2]}, {9122, 9123})

    def test_dve_osoby_stejneho_jmena(self):
        self.assertEqual(score("Michal Kopal")["verdict"], "nejistý")

    def test_jen_prijmeni_u_rodiny(self):
        self.assertEqual(score("Novotná")["verdict"], "nejistý")

    def test_klient_ktery_v_crm_neni(self):
        self.assertEqual(score("Robert Wiśniewski")["verdict"], "žádný")


class HledaciVyrazy(unittest.TestCase):
    """Výrazy pro company_list(name=…), který rozlišuje diakritiku."""

    def variants(self, name):
        return match_name.cmd_variants(name)

    def test_odstrani_pad(self):
        v = self.variants("Honzou Kumlem")
        self.assertEqual(v["surname_variants"][0], "Kuml")
        self.assertIn("Jan", v["first_name_fallback"])

    def test_prefix_bez_diakritiky_i_s_ni(self):
        # Ověřeno v provozu: příjmení bez háčku nenajde klienta s háčkem.
        v = self.variants("Milanem Čápkem")["surname_variants"]
        self.assertIn("Čáp", v)
        self.assertIn("Cap", v)

    def test_cesky_prepis_ciziho_jmena(self):
        # Sch- vs Š-: prefix originálu zápis v CRM nenajde, prefix přepisu ano.
        self.assertIn("Šna", self.variants("Schneider")["surname_variants"])

    def test_kratky_prefix_pri_zamene_uprostred(self):
        self.assertIn("Lem", self.variants("Jaroslav Lemrád")["surname_variants"])


if __name__ == "__main__":
    unittest.main()
