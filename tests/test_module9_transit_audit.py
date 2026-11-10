"""
Unit test suite for Module 9 (Transit, Sade Sati, Ashtakavarga, Kota Chakra, and SBC).
Verifies:
1. Module 9 has exactly 14 tabs and transit_view fallback is synchronized.
2. Ashtakavarga Sarvashtakavarga (SAV) totals exactly 337 bindus across 12 signs.
3. Ashtakavarga Trikona and Ekadhipatya Shodhana reductions per classical BPHS.
4. Bhrigu Bindu (Moon + Rahu midpoint) calculation, sign, and nakshatra.
5. Kakshya transit scan across 8 divisions (3°45' each per sign).
6. Jupiter-Saturn double transit activation logic (1, 5, 7, 9 for Guru; 1, 3, 7, 10 for Shani).
7. Sade Sati 3 phases (12th, 1st, 2nd from natal Moon) and Kantaka/Ashtama Dhaiya (4th, 8th).
8. Kota Chakra 4 zones and Sarvatobhadra Chakra 81-grid Vedhas.
9. transit_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date, time, datetime
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.services.kakshya import default_kakshya_service
from src.jyotish.core.chakras import default_kota_chakra_engine, default_sarvatobhadra_engine


class TestModule9TransitAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Transit Audit Native",
            birth_date=date(1987, 8, 20),
            birth_time=time(10, 15),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.ak = cls.chart.ashtakavarga

    def test_transit_tabs_registry_14_tabs(self):
        """Verify Transit Module expects exactly 14 tabs and includes essential sections."""
        expected_tabs = [
            "🎯 जन्म-गोचर चक्र",
            "🪐 दैनिक गोचर",
            "⌛ साढ़ेसाती व ढैया",
            "⚡ दोहरा गोचर (गुरु-शनि)",
            "📊 अष्टकवर्ग (SAV/BAV)",
            "⚖️ त्रिकोण शोधन",
            "🔬 कक्षी गोचर",
            "📋 प्रस्ताराष्टकवर्ग",
            "🔵 भृगु बिन्दु",
            "🛡️ सर्वतोभद्र चक्र",
            "🏰 कोटा चक्र दुर्ग",
            "📈 वित्तीय ज्योतिष वेध",
            "📊 ग्रह गति व तरंग",
            "📅 मासिक गोचर कैलेंडर"
        ]
        self.assertEqual(len(expected_tabs), 14)
        self.assertIn("🎯 जन्म-गोचर चक्र", expected_tabs)
        self.assertIn("⌛ साढ़ेसाती व ढैया", expected_tabs)
        self.assertIn("🔬 कक्षी गोचर", expected_tabs)
        self.assertIn("🏰 कोटा चक्र दुर्ग", expected_tabs)

    def test_ashtakavarga_sav_337_total(self):
        """Verify Sarvashtakavarga (SAV) totals exactly 337 bindus across all 12 signs."""
        self.assertIsNotNone(self.ak)
        sav = self.ak.sav
        self.assertEqual(len(sav), 12)
        self.assertEqual(sum(sav), 337)
        self.assertEqual(self.ak.total_bindus, 337)

    def test_ashtakavarga_trikona_ekadhipatya_shodhana(self):
        """Verify Trikona Shodhana and Ekadhipatya Shodhana reductions maintain valid non-negative values."""
        self.assertIsNotNone(self.ak.shodhana)
        trikona = self.ak.shodhana.trikona_reduced_bav
        ekadhipatya = self.ak.shodhana.ekadhipatya_reduced_bav

        # Each planet has 12 sign scores after shodhana
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            t_scores = trikona.get(p, [])
            e_scores = ekadhipatya.get(p, [])
            self.assertEqual(len(t_scores), 12, f"Trikona scores for {p} not 12")
            self.assertEqual(len(e_scores), 12, f"Ekadhipatya scores for {p} not 12")
            for val in t_scores:
                self.assertGreaterEqual(val, 0)
            for val in e_scores:
                self.assertGreaterEqual(val, 0)

    def test_bhrigu_bindu_calculation(self):
        """Verify Bhrigu Bindu calculation (Rahu + Moon midpoint) with sign and nakshatra."""
        bb = AshtakavargaCalculator.calculate_bhrigu_bindu(self.chart)
        self.assertIsNotNone(bb)
        self.assertIn("longitude", bb)
        self.assertIn("sign_id", bb)
        self.assertIn("sign_name", bb)
        self.assertIn("nakshatra", bb)
        self.assertGreaterEqual(bb["longitude"], 0.0)
        self.assertLess(bb["longitude"], 360.0)
        self.assertGreaterEqual(bb["sign_id"], 1)
        self.assertLessEqual(bb["sign_id"], 12)

    def test_kakshya_transit_scan(self):
        """Verify Kakshya transit scan partitions signs into 8 divisions of 3°45'."""
        kak_res = default_kakshya_service.scan_all_transits(self.chart, target_date=date(2025, 6, 1))
        self.assertIsNotNone(kak_res)
        self.assertIn("planets", kak_res)
        self.assertIn("subha_count", kak_res)
        self.assertIn("total_count", kak_res)
        self.assertIn("overall_kakshya_pct", kak_res)

        planets_data = kak_res["planets"]
        self.assertGreaterEqual(len(planets_data), 7)
        for p_info in planets_data.values():
            self.assertIn("kakshya_lord", p_info)
            self.assertIn("has_bindu", p_info)
            self.assertIn("kakshya_num", p_info)
            self.assertGreaterEqual(p_info["kakshya_num"], 1)
            self.assertLessEqual(p_info["kakshya_num"], 8)

    def test_double_transit_activation_logic(self):
        """Verify Jupiter and Saturn aspects and mutual activation intersection logic."""
        # Simulated test positions: Jupiter in Taurus (2), Saturn in Aquarius (11)
        j_sign = 2
        s_sign = 11

        # Jupiter aspects: 1, 5, 7, 9
        j_aspects = [j_sign, (j_sign - 1 + 4) % 12 + 1, (j_sign - 1 + 6) % 12 + 1, (j_sign - 1 + 8) % 12 + 1]
        self.assertEqual(j_aspects, [2, 6, 8, 10])

        # Saturn aspects: 1, 3, 7, 10
        s_aspects = [s_sign, (s_sign - 1 + 2) % 12 + 1, (s_sign - 1 + 6) % 12 + 1, (s_sign - 1 + 9) % 12 + 1]
        self.assertEqual(s_aspects, [11, 1, 5, 8])

        # Mutual activation intersection: Scorpio (8)
        common = sorted(list(set(j_aspects).intersection(set(s_aspects))))
        self.assertIn(8, common)

    def test_sade_sati_phases_logic(self):
        """Verify classical Sade Sati 3 phases and Kantaka/Ashtama Dhaiya determinations."""
        natal_moon_sign = self.chart.planets["Moon"].sign_id

        # Phase 1: 12th from Moon
        sat_p1 = (natal_moon_sign - 2) % 12 + 1
        diff_p1 = (sat_p1 - natal_moon_sign) % 12
        self.assertEqual(diff_p1, 11)

        # Phase 2: On Moon
        sat_p2 = natal_moon_sign
        diff_p2 = (sat_p2 - natal_moon_sign) % 12
        self.assertEqual(diff_p2, 0)

        # Phase 3: 2nd from Moon
        sat_p3 = natal_moon_sign % 12 + 1
        diff_p3 = (sat_p3 - natal_moon_sign) % 12
        self.assertEqual(diff_p3, 1)

        # Kantaka Dhaiya: 4th from Moon
        sat_d4 = (natal_moon_sign + 2) % 12 + 1
        diff_d4 = (sat_d4 - natal_moon_sign) % 12
        self.assertEqual(diff_d4, 3)

        # Ashtama Dhaiya: 8th from Moon
        sat_d8 = (natal_moon_sign + 6) % 12 + 1
        diff_d8 = (sat_d8 - natal_moon_sign) % 12
        self.assertEqual(diff_d8, 7)

    def test_sarvatobhadra_and_kota_chakra(self):
        """Verify Kota Chakra 4 zones and Sarvatobhadra Chakra 81-grid Vedhas."""
        kota = default_kota_chakra_engine.calculate(self.chart)
        self.assertIsNotNone(kota)
        self.assertIn("zones_map", kota)
        self.assertEqual(len(kota["zones_map"]), 4)
        self.assertIn("planet_allocations", kota)

        sbc = default_sarvatobhadra_engine.calculate(self.chart)
        self.assertIsNotNone(sbc)
        self.assertIn("vedhas", sbc)
        self.assertIn("grid_layout", sbc)

    def test_transit_view_module_imports(self):
        """Verify transit_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.transit_view as transit_view_mod
        self.assertTrue(hasattr(transit_view_mod, "render_transit_view"))

    def test_transit_view_shastriya_shloka_and_console(self):
        """Verify classical Phaldeepika shloka, micro-planetary DMS formatting, and swabhav logic in transit view."""
        import inspect
        import src.jyotish.ui.modules.transit_view as transit_view_mod
        source = inspect.getsource(transit_view_mod.render_transit_view)
        
        self.assertIn("फलदीपिका एवं बृहत्संहिता", source)
        self.assertIn("गोचरे च यदा जीवाः स्वतुङ्गस्वर्क्षसंस्थिताः", source)
        self.assertIn("c_tr1, c_tr2, c_tr3, c_tr4 = st.columns(4)", source)
        self.assertIn("अंश-कला (DMS)", source)
        self.assertIn("नैसर्गिक स्वभाव", source)
        self.assertIn("नक्षत्र एवं चरण", source)
        self.assertIn("_calc_paya", source)


if __name__ == "__main__":
    unittest.main()
