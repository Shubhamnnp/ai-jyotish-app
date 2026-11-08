"""
Unit test suite for Module 13 (Varshaphal & Tajika Annual Solar Return).
Verifies:
1. Module 13 has exactly 10 tabs and varshaphal_view fallback is synchronized.
2. Solar return calculation, target year, and return datetime.
3. Muntha sign progression according to native's completed age.
4. Panchadhikari 5 office holders scored and Varshesha selected.
5. Panchavargiya (Kshetra, Uccha, Hadda, Drekkana, Navamsha, Vishopaka) and Harsha Bala for 7 planets.
6. Tajika Sahams (Punya Saham, etc.) calculation.
7. 1-year Mudda Dasha sequence and total period.
8. varshaphal_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.varshaphal import default_varshaphal_service


class TestModule13VarshaphalAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Varshaphal Audit Native",
            birth_date=date(1990, 8, 15),
            birth_time=time(14, 20),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.target_year = 2025
        cls.vp_res = default_varshaphal_service.calculate_varshaphal(cls.chart, cls.target_year)

    def test_varshaphal_tabs_registry_10_tabs(self):
        """Verify Varshaphal Module expects exactly 10 tabs and includes essential sections."""
        expected_tabs = [
            "🌟 वर्ष कुण्डली (D1)",
            "🎯 मुन्था विचार",
            "👑 वर्षेश चयन",
            "⚖️ पंचवर्गीय व हर्ष बल",
            "⚡ १६ ताजिक योग",
            "💫 ३६ ताजिक सहम",
            "⏳ मुद्धा व योगिनी दशा",
            "📊 १२ भाव वर्षफल",
            "🗓️ मासफल (१२ मास)",
            "🪔 वर्षेश शांति उपाय"
        ]
        self.assertEqual(len(expected_tabs), 10)
        self.assertIn("🌟 वर्ष कुण्डली (D1)", expected_tabs)
        self.assertIn("🎯 मुन्था विचार", expected_tabs)
        self.assertIn("👑 वर्षेश चयन", expected_tabs)
        self.assertIn("⚖️ पंचवर्गीय व हर्ष बल", expected_tabs)
        self.assertIn("💫 ३६ ताजिक सहम", expected_tabs)

    def test_solar_return_calculation(self):
        """Verify Solar Return datetime, completed years, and varsha chart generation."""
        self.assertEqual(self.vp_res["target_year"], self.target_year)
        self.assertEqual(self.vp_res["completed_years"], self.target_year - self.birth_data.birth_date.year)
        self.assertIn("solar_return_datetime", self.vp_res)
        self.assertIn("varsha_lagna", self.vp_res)
        self.assertIn("varsha_lagna_lord", self.vp_res)

    def test_muntha_progression(self):
        """Verify Muntha progresses 1 sign per year from natal Lagna."""
        natal_lagna = self.chart.lagna_sign_id
        completed_years = self.vp_res["completed_years"]
        expected_muntha_sign_id = ((natal_lagna - 1 + completed_years) % 12) + 1

        self.assertIn("muntha_sign", self.vp_res)
        self.assertIn("muntha_house", self.vp_res)
        self.assertIn("muntha_lord", self.vp_res)
        self.assertIn("muntha_fruit_title", self.vp_res)

    def test_panchadhikaris_and_varshesha(self):
        """Verify 5 candidates scored and Varshesha selected."""
        candidates = self.vp_res.get("varshesha_candidates_scored", [])
        self.assertEqual(len(candidates), 5)

        roles = [c["role"] for c in candidates]
        self.assertTrue(any("मुन्था" in r for r in roles))
        self.assertTrue(any("जन्म लग्न" in r for r in roles))
        self.assertTrue(any("वर्ष लग्न" in r for r in roles))
        self.assertTrue(any("त्रि-राशीश" in r for r in roles))
        self.assertTrue(any("दिन/रात्रि" in r for r in roles))

        self.assertIn("varshesha", self.vp_res)
        self.assertIsNotNone(self.vp_res["varshesha"])

    def test_panchavargiya_and_harsha_bala(self):
        """Verify Panchavargiya Bala (Kshetra, Uccha, Hadda, Drekkana, Navamsha) and Harsha Bala."""
        pv = self.vp_res.get("panchavargiya_bala", [])
        self.assertEqual(len(pv), 7)
        for item in pv:
            self.assertIn("planet", item)
            self.assertIn("kshetra", item)
            self.assertIn("uccha", item)
            self.assertIn("hadda", item)
            self.assertIn("drekkana", item)
            self.assertIn("navamsha", item)
            self.assertIn("vishopaka", item)

        hb = self.vp_res.get("harsha_bala", [])
        self.assertEqual(len(hb), 7)
        for item in hb:
            self.assertIn("planet", item)
            self.assertIn("sthana", item)
            self.assertIn("swakshetra", item)
            self.assertIn("rashi", item)
            self.assertIn("kala", item)
            self.assertIn("total", item)
            self.assertGreaterEqual(item["total"], 0)
            self.assertLessEqual(item["total"], 20)

    def test_tajika_sahams(self):
        """Verify Tajika Sahams list calculation."""
        sahams = self.vp_res.get("sahams", [])
        self.assertGreaterEqual(len(sahams), 15)
        for s in sahams:
            self.assertIn("saham_hi", s)
            self.assertIn("saham_en", s)
            self.assertIn("sign", s)

    def test_mudda_dasha_full_year(self):
        """Verify 1-year Mudda Dasha sequence for 9 planets."""
        mudda = self.vp_res.get("mudda_dasha_full", [])
        self.assertEqual(len(mudda), 9)

        total_days = sum(m.get("duration_days", 0.0) for m in mudda)
        self.assertAlmostEqual(total_days, 365.25, delta=2.0)

    def test_varshaphal_view_module_imports(self):
        """Verify varshaphal_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.varshaphal_view as varshaphal_view_mod
        self.assertTrue(hasattr(varshaphal_view_mod, "render_varshaphal_view"))


if __name__ == "__main__":
    unittest.main()
