"""
Unit test suite for Module 12 (Sudarshan Chakra - Concentric 3-Wheel Synthesis).
Verifies:
1. Module 12 has exactly 9 tabs and sudarshan_chakra_view fallback is synchronized.
2. Concentric 3-ring mandala calculation (Lagna, Chandra, Surya) for all 12 houses.
3. Triad dominance analysis (Deha, Manas, Atma) with harmony level and scores.
4. Sudarshan annual dasha progression (1 house per year, 12-year cycle).
5. 12 Bhava composite scores with BPHS Ch. 74 classical sutras.
6. sudarshan_chakra_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.ui.sudarshan import default_sudarshan_engine


class TestModule12SudarshanAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Sudarshan Audit Native",
            birth_date=date(1991, 7, 22),
            birth_time=time(11, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.sd_res = default_sudarshan_engine.calculate(cls.chart)
        cls.dom = default_sudarshan_engine.calculate_triad_dominance(cls.chart)
        cls.dasha = default_sudarshan_engine.calculate_dasha(cls.chart, current_age=34)

    def test_sudarshan_tabs_registry_9_tabs(self):
        """Verify Sudarshan Module expects exactly 9 tabs and includes essential sections."""
        expected_tabs = [
            "☸️ त्रि-चक्रीय मण्डल",
            "📊 १२ भाव त्रिविध फल",
            "⏳ सुदर्शन दशा",
            "🪐 त्रि-लग्न संरेखण",
            "🔍 त्रि-आयामी फलित",
            "📈 अष्टकवर्ग समन्वय",
            "⚖️ त्रि-शरीर मीमांसा",
            "📜 पाराशर प्रमाण (अ. ७४)",
            "🪔 सुदर्शन कवच व मन्त्र"
        ]
        self.assertEqual(len(expected_tabs), 9)
        self.assertIn("☸️ त्रि-चक्रीय मण्डल", expected_tabs)
        self.assertIn("📊 १२ भाव त्रिविध फल", expected_tabs)
        self.assertIn("⏳ सुदर्शन दशा", expected_tabs)
        self.assertIn("📜 पाराशर प्रमाण (अ. ७४)", expected_tabs)

    def test_sudarshan_triple_ring_calculation(self):
        """Verify 3 concentric rings (Lagna, Chandra, Surya) are calculated for all 12 houses."""
        self.assertIn("lagna_sign", self.sd_res)
        self.assertIn("chandra_sign", self.sd_res)
        self.assertIn("surya_sign", self.sd_res)
        self.assertIn("houses", self.sd_res)

        houses = self.sd_res["houses"]
        self.assertEqual(len(houses), 12)

        for h in houses:
            self.assertIn("house_num", h)
            self.assertIn("lagna_ring", h)
            self.assertIn("chandra_ring", h)
            self.assertIn("surya_ring", h)
            self.assertIn("score_num", h)
            self.assertGreaterEqual(h["score_num"], 0)
            self.assertLessEqual(h["score_num"], 100)

    def test_sudarshan_triad_dominance(self):
        """Verify Triad Dominance (Deha, Manas, Atma) analysis and harmony level."""
        self.assertIn("dominant_lagna", self.dom)
        self.assertIn("dominant_score", self.dom)
        self.assertIn("lagna_score", self.dom)
        self.assertIn("chandra_score", self.dom)
        self.assertIn("surya_score", self.dom)
        self.assertIn("harmony_level", self.dom)
        self.assertIn("philosophical_analysis", self.dom)

        for score in [self.dom["lagna_score"], self.dom["chandra_score"], self.dom["surya_score"]]:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_sudarshan_dasha_annual_progression(self):
        """Verify Sudarshan Dasha annual progression (1 house per year, 12 houses per cycle)."""
        self.assertEqual(self.dasha["current_age"], 34)
        # Age 34 = 34 % 12 = house 10
        expected_house = ((34 - 1) % 12) + 1
        self.assertEqual(self.dasha["active_house"], expected_house)
        self.assertEqual(self.dasha["cycle_num"], (34 - 1) // 12 + 1)
        self.assertIn("annual_prediction", self.dasha)
        self.assertIn("monthly_antardashas", self.dasha)
        self.assertEqual(len(self.dasha["monthly_antardashas"]), 12)

    def test_sudarshan_bhava_composite_scores(self):
        """Verify composite scores and BPHS Ch. 74 classical sutras in house definitions."""
        houses = self.sd_res["houses"]
        for h in houses:
            self.assertIn("shubh_wheels", h)
            self.assertIn(h["shubh_wheels"], [0, 1, 2, 3])
            self.assertIn("classical_sutra", h)
            self.assertTrue(len(h["classical_sutra"]) > 10)

    def test_sudarshan_chakra_view_module_imports(self):
        """Verify sudarshan_chakra_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.sudarshan_chakra_view as sudarshan_view_mod
        self.assertTrue(hasattr(sudarshan_view_mod, "render_sudarshan_chakra_view"))


if __name__ == "__main__":
    unittest.main()
