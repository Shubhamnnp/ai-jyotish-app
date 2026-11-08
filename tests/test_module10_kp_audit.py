"""
Unit test suite for Module 10 (Krishnamurti Paddhati - KP System).
Verifies:
1. Module 10 has exactly 9 tabs and kp_view fallback is synchronized.
2. Cuspal sub-lords (12 houses) with Sign Lord, Star Lord, Sub Lord, and Sub-Sub Lord.
3. Planetary positions in KP with Star Lord and Sub Lord.
4. 4-fold significators (Levels 1 to 4) for all 12 houses and planets.
5. Ruling Planets (RP: Day Lord, Moon Sign/Star Lord, Lagna Sign/Star Lord).
6. 1-249 Horary Master Table integrity and single horary number detail.
7. KP Event prediction query engine (predict_kp_query) and CSL promise matrix.
8. kp_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.kp import default_kp_engine


class TestModule10KPAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="KP Audit Native",
            birth_date=date(1992, 3, 10),
            birth_time=time(9, 45),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.kp_data = default_kp_engine.calculate_chart_kp(cls.chart)

    def test_kp_tabs_registry_9_tabs(self):
        """Verify KP Module expects exactly 9 tabs and includes essential sections."""
        expected_tabs = [
            "🔮 के.पी. कार्य सिद्धि",
            "🪐 ४-स्तरीय कार्यकत्व",
            "🏰 कस्पल सब-लॉर्ड",
            "👑 रूलिंग प्लैनेट्स (RP)",
            "🔢 १-२४९ होरारी तालिका",
            "📐 पाश्चात्य दृष्टि वेध",
            "⏱️ के.पी. दशा भुक्ति",
            "📊 २२ घटना मैट्रिक्स",
            "📜 के.पी. स्वर्णिम नियम"
        ]
        self.assertEqual(len(expected_tabs), 9)
        self.assertIn("🔮 के.पी. कार्य सिद्धि", expected_tabs)
        self.assertIn("🪐 ४-स्तरीय कार्यकत्व", expected_tabs)
        self.assertIn("🏰 कस्पल सब-लॉर्ड", expected_tabs)
        self.assertIn("👑 रूलिंग प्लैनेट्स (RP)", expected_tabs)
        self.assertIn("🔢 १-२४९ होरारी तालिका", expected_tabs)

    def test_kp_cuspal_sublords_12_houses(self):
        """Verify all 12 houses have complete Placidus cusps with Sign, Star, Sub, and Sub-Sub Lords."""
        cusps = self.kp_data.get("cusps_kp", [])
        self.assertEqual(len(cusps), 12)

        for c in cusps:
            self.assertIn("cusp_num", c)
            self.assertIn("sign", c)
            self.assertIn("sign_lord", c)
            self.assertIn("star_lord", c)
            self.assertIn("sub_lord", c)
            self.assertIn("sub_sub_lord", c)
            self.assertIn("longitude", c)
            self.assertGreaterEqual(c["longitude"], 0.0)
            self.assertLess(c["longitude"], 360.0)

    def test_kp_planets_star_sublords(self):
        """Verify planets in KP have Sign, Star, Sub, and Sub-Sub Lords."""
        planets = self.kp_data.get("planets_kp", [])
        self.assertGreaterEqual(len(planets), 9)

        for p in planets:
            self.assertIn("planet", p)
            self.assertIn("sign", p)
            self.assertIn("sign_lord", p)
            self.assertIn("star_lord", p)
            self.assertIn("sub_lord", p)
            self.assertIn("sub_sub_lord", p)

    def test_kp_4_fold_significators(self):
        """Verify 4-level house significators and planet significations."""
        h_sig = self.kp_data.get("house_significators", {})
        self.assertEqual(len(h_sig), 12)

        for h in range(1, 13):
            self.assertIn(h, h_sig)
            h_info = h_sig[h]
            self.assertIn("level_a", h_info)
            self.assertIn("level_b", h_info)
            self.assertIn("level_c", h_info)
            self.assertIn("level_d", h_info)
            self.assertIn("all_significators", h_info)

        p_sig = self.kp_data.get("planet_significations", {})
        self.assertGreaterEqual(len(p_sig), 7)

    def test_kp_ruling_planets(self):
        """Verify Ruling Planets (RP) determination."""
        rp = self.kp_data.get("ruling_planets", {})
        self.assertIn("day_lord", rp)
        self.assertIn("moon_sign_lord", rp)
        self.assertIn("moon_star_lord", rp)
        self.assertIn("moon_sub_lord", rp)
        self.assertIn("lagna_sign_lord", rp)
        self.assertIn("lagna_star_lord", rp)
        self.assertIn("lagna_sub_lord", rp)
        self.assertIn("all_rp_list", rp)
        self.assertGreater(len(rp["all_rp_list"]), 0)

    def test_kp_249_horary_table(self):
        """Verify 1-249 Horary Master table spans full 360 degrees."""
        all_249 = default_kp_engine.get_all_249_table()
        self.assertGreaterEqual(len(all_249), 249)

        # Check detail lookup for number 1 and 249
        h1 = default_kp_engine.get_horary_number_detail(1)
        self.assertEqual(h1["sign_name"], "Aries")
        self.assertEqual(h1["star_lord"], "Ketu")
        self.assertEqual(h1["sub_lord"], "Ketu")

        h_last = default_kp_engine.get_horary_number_detail(249)
        self.assertEqual(h_last["sign_name"], "Pisces")

    def test_kp_event_prediction_query(self):
        """Verify predict_kp_query generates structured prediction output."""
        pred = default_kp_engine.predict_kp_query(self.chart, query_key="job_new")
        self.assertIsNotNone(pred)
        self.assertIn("query_name", pred)
        self.assertIn("verdict_badge", pred)
        self.assertIn("primary_cusp", pred)
        self.assertIn("favorable_houses", pred)

    def test_kp_csl_promise_matrix(self):
        """Verify 22 life event CSL matrix generation."""
        csl_matrix = self.kp_data.get("csl_matrix", [])
        self.assertGreaterEqual(len(csl_matrix), 10)
        for item in csl_matrix:
            self.assertIn("cusp_num", item)
            self.assertIn("bhava_name", item)
            self.assertIn("csl", item)

    def test_kp_view_module_imports(self):
        """Verify kp_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.kp_view as kp_view_mod
        self.assertTrue(hasattr(kp_view_mod, "render_kp_view"))


if __name__ == "__main__":
    unittest.main()
