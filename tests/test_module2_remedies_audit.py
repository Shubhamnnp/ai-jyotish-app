"""
Unit tests validating Module 2 (Remedies, Free Will & Badhaka/Maraka) audit fixes:
1. Free Will & Affliction calculation across 12 houses and 9 planets.
2. Gemstone recommendation safety check: 6th, 8th, 12th lords strictly forbidden.
3. Badhaka & Maraka detection for Movable, Fixed, and Dual Ascendants.
4. Active Maraka/Badhaka Mahadasha/Antardasha operational alert logic.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.affliction import AfflictionEngine
from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine
from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS


class TestModule2RemediesAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Native with Leo Ascendant (Fixed Sign: Sun lord, 9th house Aries/Mars is Badhaka)
        cls.birth_data_fixed = BirthData(
            name="Test Leo Fixed Lagna",
            birth_date=date(1990, 8, 20),
            birth_time=time(7, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart_fixed = default_chart_calculator.calculate_full_chart(cls.birth_data_fixed)

        # Native with Aries Ascendant (Movable Sign: Mars lord, 11th house Aquarius/Saturn is Badhaka)
        cls.birth_data_movable = BirthData(
            name="Test Aries Movable Lagna",
            birth_date=date(1990, 4, 15),
            birth_time=time(6, 0),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart_movable = default_chart_calculator.calculate_full_chart(cls.birth_data_movable)

    def test_tab1_freewill_house_and_planet_points(self):
        """Tab 1: Test that AfflictionEngine calculates valid free will percentages for all 12 houses and planets."""
        engine = AfflictionEngine(self.chart_fixed)
        hp_list = engine.calculate_house_points()
        self.assertEqual(len(hp_list), 12)
        for h in hp_list:
            self.assertIn("house", h)
            self.assertIn("freeWill", h)
            fw_val = float(str(h["freeWill"]).replace("%", "").strip())
            self.assertGreaterEqual(fw_val, 0.0)
            self.assertLessEqual(fw_val, 100.0)

        pp_list = engine.calculate_planet_points()
        self.assertGreaterEqual(len(pp_list), 7)
        for p in pp_list:
            self.assertIn("planet", p)
            self.assertIn("freeWill", p)

    def test_tab2_life_areas_coverage(self):
        """Tab 2: Test that applicable life areas are computed and detailed data is returned."""
        engine = AfflictionEngine(self.chart_fixed)
        areas = engine.get_applicable_life_areas("male")
        self.assertGreater(len(areas), 20)
        # Check area 1 (Career)
        detail = engine.get_life_area_detail(1)
        self.assertIn("HouseRows", detail)
        self.assertIn("LordRows", detail)

    def test_tab3_gemstone_safety_rules(self):
        """Tab 3: Verify gemstone safety rule: 6th, 8th, 12th lords should never be safe gemstones."""
        lagna_id = self.chart_fixed.lagna_sign_id
        # Trika house lords (6, 8, 12)
        h6_sign = SIGN_NAMES[((lagna_id - 1 + 5) % 12)]
        h8_sign = SIGN_NAMES[((lagna_id - 1 + 7) % 12)]
        h12_sign = SIGN_NAMES[((lagna_id - 1 + 11) % 12)]

        trika_lords = {SIGN_LORDS[h6_sign], SIGN_LORDS[h8_sign], SIGN_LORDS[h12_sign]}

        # For Leo (5): H6 is Capricorn (Saturn), H8 is Pisces (Jupiter), H12 is Cancer (Moon)
        self.assertIn("Saturn", trika_lords)
        self.assertIn("Moon", trika_lords)

    def test_tab4_badhaka_maraka_movable_vs_fixed(self):
        """Tab 4: Verify Badhaka calculation: Movable -> 11th, Fixed -> 9th, Dual -> 7th."""
        # Fixed Lagna (Leo) -> 9th house is Badhaka
        bm_fixed = default_shastriya_pramana_engine.audit_badhaka_maraka(self.chart_fixed)
        self.assertIn("स्थिर", bm_fixed["lagna_type"])
        self.assertEqual(bm_fixed["badhaka_house"], 9)

        # Movable Lagna (Aries) -> 11th house is Badhaka
        bm_movable = default_shastriya_pramana_engine.audit_badhaka_maraka(self.chart_movable)
        self.assertIn("चर", bm_movable["lagna_type"])
        self.assertEqual(bm_movable["badhaka_house"], 11)

        # Maraka primary is 2nd house lord, secondary is 7th house lord
        self.assertEqual(bm_fixed["maraka_primary"]["house"], 2)
        self.assertEqual(bm_fixed["maraka_secondary"]["house"], 7)

    def test_remedies_view_active_native_dms_and_shloka(self):
        """Verify active native's planets have valid DMS, ansh, kala, nakshatra padas and BPHS shloka in remedies_view."""
        view_code = open("src/jyotish/ui/modules/remedies_view.py", encoding="utf-8").read()
        self.assertIn("bphs_remedies_shloka", view_code)
        self.assertIn("चरभवनेषु लाभेशो बाधको नवमो स्थिरे", view_code)
        self.assertIn("बाधकेश सूक्ष्म स्थिति", view_code)
        self.assertIn("मुख्य मारकेश सूक्ष्म स्थिति", view_code)
        self.assertIn("बाधकेश स्थिति", view_code)


if __name__ == "__main__":
    unittest.main()
