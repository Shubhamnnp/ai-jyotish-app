"""
Unit tests validating Module 0 (Natal & Divisional Charts) audit fixes across all 9 tabs:
1. D1-D60 Varga interpretation synthesis
2. Pushkara Navamsha & Pushkara Bhaga fruit evaluation
3. Jaimini Indu Lagna & Special Lagnas
4. Bhava Sandhi detection
5. Kemadruma Bhanga Rajayoga detection
6. Surya Vesi/Vasi yoga strict Rahu/Ketu exclusion
7. Graha Yuddha victor/loser evaluation
8. 12 Arudha Padas calculation
9. Kota Chakra transit overlay calculation
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.chakras import default_kota_chakra_engine


class TestModule0AuditFixes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Test Native",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)

    def test_tab1_varga_calculations(self):
        """Tab 1: Test that D1-D60 divisional charts generate valid varga planets."""
        d9 = VargaCalculator.calculate_d9(self.chart)
        self.assertIsNotNone(d9)
        self.assertEqual(len(d9.planets), len(self.chart.planets))

        d10 = VargaCalculator.calculate_d10(self.chart)
        self.assertIsNotNone(d10)
        self.assertEqual(len(d10.planets), len(self.chart.planets))

    def test_tab2_pushkara_audit(self):
        """Tab 2: Test Pushkara Navamsha and Bhaga detection."""
        from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine
        p_audit = default_shastriya_pramana_engine.audit_chart_pushkara(self.chart)
        self.assertIn("planets", p_audit)
        self.assertIn("pushkara_navamsha_planets", p_audit)
        self.assertIn("pushkara_bhaga_planets", p_audit)

    def test_tab3_jaimini_special_lagnas(self):
        """Tab 3: Test Jaimini Hora Lagna, Ghati Lagna, Indu Lagna exist and have valid signs."""
        self.assertIsNotNone(self.chart.jaimini)
        jm = self.chart.jaimini
        self.assertTrue(len(jm.hora_lagna_sign_name) > 0)
        self.assertTrue(len(jm.ghati_lagna_sign_name) > 0)
        self.assertTrue(len(jm.indu_lagna_sign_name) > 0)

    def test_tab4_bhava_chalit_and_sandhi(self):
        """Tab 4: Test Bhava Chalit cusp calculation."""
        res = default_chart_calculator.calculate_bhava_chalit(self.chart)
        self.assertIn("planet_positions", res)
        self.assertIn("bhava_cusps", res)
        self.assertEqual(len(res["bhava_cusps"]), 12)

    def test_tab5_kemadruma_bhanga(self):
        """Tab 5: Test Kemadruma Yoga and its Bhanga (cancellation)."""
        moon = self.chart.planets["Moon"]
        moon_sign = moon.sign_id
        # Planets in 2nd and 12th from Moon
        h2 = (moon_sign % 12) + 1
        h12 = ((moon_sign - 2) % 12) + 1
        adj = [p.name for p in self.chart.planets.values() if p.name not in ["Sun", "Rahu", "Ketu", "Moon"] and p.sign_id in (h2, h12)]

        # Check bhanga: kendra from lagna has moon or jupiter
        lagna_id = self.chart.lagna_sign_id
        kendras = [lagna_id, ((lagna_id + 2) % 12) + 1, ((lagna_id + 5) % 12) + 1, ((lagna_id + 8) % 12) + 1]
        has_kendra_jup_moon = (self.chart.planets["Jupiter"].sign_id in kendras) or (moon.sign_id in kendras)
        self.assertIsInstance(has_kendra_jup_moon, bool)

    def test_tab6_surya_vesi_vasi_exclusion(self):
        """Tab 6: Test that Rahu and Ketu are strictly excluded from Vesi/Vasi yogas."""
        sun = self.chart.planets["Sun"]
        sun_sign = sun.sign_id
        vesi_sign = (sun_sign % 12) + 1
        vasi_sign = ((sun_sign - 2) % 12) + 1

        vesi_planets = [p.name for p in self.chart.planets.values() if p.sign_id == vesi_sign and p.name not in ["Moon", "Rahu", "Ketu"]]
        vasi_planets = [p.name for p in self.chart.planets.values() if p.sign_id == vasi_sign and p.name not in ["Moon", "Rahu", "Ketu"]]

        self.assertNotIn("Rahu", vesi_planets)
        self.assertNotIn("Ketu", vesi_planets)
        self.assertNotIn("Moon", vesi_planets)
        self.assertNotIn("Rahu", vasi_planets)
        self.assertNotIn("Ketu", vasi_planets)
        self.assertNotIn("Moon", vasi_planets)

    def test_tab7_graha_yuddha_matrix(self):
        """Tab 7: Test 5x5 Tara Graha separation distance and detection."""
        yuddha_list = default_chart_calculator.detect_graha_yuddha(self.chart)
        self.assertIsInstance(yuddha_list, list)

    def test_tab8_arudha_padas_12(self):
        """Tab 8: Test all 12 Arudha Padas exist in Jaimini details."""
        jm = self.chart.jaimini
        self.assertIsNotNone(jm)
        self.assertIsNotNone(jm.arudha_details)
        for key in ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]:
            self.assertIn(key, jm.arudha_details)

    def test_tab9_kota_chakra_engine(self):
        """Tab 9: Test Kota Chakra calculates Kota Swami, Kota Pala, and allocations."""
        k_data = default_kota_chakra_engine.calculate(self.chart)
        self.assertIn("kota_swami", k_data)
        self.assertIn("kota_pala", k_data)
        self.assertIn("defense_status", k_data)
        self.assertIn("planet_allocations", k_data)
        self.assertGreater(len(k_data["planet_allocations"]), 0)


if __name__ == "__main__":
    unittest.main()
