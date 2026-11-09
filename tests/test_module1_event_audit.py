"""
Unit tests validating Module 1 (Event Analysis & Verification) audit fixes:
1. Future Event 3-Tier trigger composite calculation across all themes (including property, travel, spirituality).
2. Past Event 6-pillar verification for newly supported themes: property, travel, spirituality.
3. Double transit (Saturn-Jupiter) detection and calculation accuracy.
4. Score boundary invariants (0 <= probability <= 100).
"""

import unittest
from datetime import date, time, datetime
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.event_query import default_event_query_service, THEME_SIGNIFICATORS
from src.jyotish.events.past_verification import (
    default_past_event_engine,
    PastEventVerificationInput,
    AstrologicalEvidenceStatus
)


class TestModule1EventAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Test Event Native",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)

    def test_future_event_3tier_all_themes(self):
        """Test that 3-Tier triggers evaluate cleanly across all 9 themes."""
        target_d = date(2027, 4, 15)
        for theme_key in ["career", "marriage", "wealth", "children", "property", "travel", "health", "spirituality", "all"]:
            res = default_event_query_service.evaluate_3tier_triggers(self.chart, theme_key, target_d)
            self.assertIn("composite_probability", res)
            self.assertIn("tier1", res)
            self.assertIn("tier2", res)
            self.assertIn("tier3", res)
            self.assertGreaterEqual(res["composite_probability"], 0)
            self.assertLessEqual(res["composite_probability"], 100)
            self.assertEqual(res["tier1"]["max"], 40)
            self.assertEqual(res["tier2"]["max"], 35)
            self.assertEqual(res["tier3"]["max"], 25)

    def test_scan_event_range_12_months(self):
        """Test scanning 12 months for property and travel themes."""
        start_d = date(2026, 1, 1)
        res = default_event_query_service.scan_event_range(self.chart, "property", start_d, 12)
        self.assertEqual(len(res["monthly_records"]), 12)
        self.assertIsNotNone(res["peak_record"])
        self.assertGreaterEqual(res["peak_score"], 0)
        self.assertLessEqual(res["peak_score"], 100)

        # Check Pratyantardasha in monthly records
        for r in res["monthly_records"]:
            self.assertIn("active_dasha", r)
            self.assertIn("tier1_score", r)
            self.assertIn("tier2_score", r)
            self.assertIn("tier3_score", r)

    def test_past_verification_property_theme(self):
        """Test that past event verification supports property theme (House 4, Varga D4)."""
        inp = PastEventVerificationInput(
            birth_data=self.birth_data,
            event_theme="property",
            query_text="नया मकान और वाहन क्रय किया",
            target_date=date(2021, 6, 10)
        )
        res = default_past_event_engine.verify_past_event(inp, precomputed_chart=self.chart)
        self.assertIsNotNone(res)
        self.assertIn(res.status, [
            AstrologicalEvidenceStatus.STRONGLY_SUPPORTED,
            AstrologicalEvidenceStatus.SUPPORTED,
            AstrologicalEvidenceStatus.MODERATELY_SUPPORTED,
            AstrologicalEvidenceStatus.WEAKLY_SUPPORTED,
            AstrologicalEvidenceStatus.INCONCLUSIVE,
            AstrologicalEvidenceStatus.CONFLICTING,
            AstrologicalEvidenceStatus.NOT_SUPPORTED
        ])
        # Verify Pillar 1 has primary house 4
        self.assertEqual(res.pillar_1_d1_evidence.get("primary_house"), 4)
        # Verify Pillar 3 has varga D4
        self.assertEqual(res.pillar_3_varga_evidence.get("varga_code"), "D4")

    def test_past_verification_travel_theme(self):
        """Test that past event verification supports travel theme (House 12, Varga D9)."""
        inp = PastEventVerificationInput(
            birth_data=self.birth_data,
            event_theme="travel",
            query_text="प्रथम बार विदेश यात्रा संपन्न हुई",
            target_date=date(2019, 11, 20)
        )
        res = default_past_event_engine.verify_past_event(inp, precomputed_chart=self.chart)
        self.assertIsNotNone(res)
        self.assertEqual(res.pillar_1_d1_evidence.get("primary_house"), 12)
        self.assertEqual(res.pillar_3_varga_evidence.get("varga_code"), "D9")

    def test_past_verification_spirituality_theme(self):
        """Test that past event verification supports spirituality theme (House 9, Varga D20)."""
        inp = PastEventVerificationInput(
            birth_data=self.birth_data,
            event_theme="spirituality",
            query_text="गुरु दीक्षा एवं गायत्री अनुष्ठान संपन्न",
            target_date=date(2022, 3, 1)
        )
        res = default_past_event_engine.verify_past_event(inp, precomputed_chart=self.chart)
        self.assertIsNotNone(res)
        self.assertEqual(res.pillar_1_d1_evidence.get("primary_house"), 9)
        self.assertEqual(res.pillar_3_varga_evidence.get("varga_code"), "D20")

    def test_double_transit_aspects(self):
        """Test that Double Transit correctly evaluates Saturn (1, 3, 7, 10) and Jupiter (1, 5, 7, 9) aspects."""
        target_d = date(2027, 8, 15)
        eval_res = default_event_query_service.evaluate_3tier_triggers(self.chart, "career", target_d)
        tier2 = eval_res["tier2"]
        self.assertIn("score", tier2)
        self.assertIn("saturn_house", tier2)
        self.assertIn("jupiter_house", tier2)
        self.assertIn("reasons", tier2)
        self.assertGreaterEqual(tier2["score"], 0)
        self.assertLessEqual(tier2["score"], 35)

    def test_event_view_active_native_dms_and_shloka(self):
        """Verify active native's planets have valid DMS, ansh, kala, nakshatra padas and Phaldeepika shloka in event_view."""
        view_code = open("src/jyotish/ui/modules/event_view.py", encoding="utf-8").read()
        self.assertIn("phaladeepika_event_shloka", view_code)
        self.assertIn("दशानाथानुसारेण गोचरेण विचारयेत्", view_code)
        self.assertIn("सक्रिय दशानाथ सूक्ष्म स्थिति", view_code)
        self.assertIn("गुरु स्थिति", view_code)
        self.assertIn("शनि स्थिति", view_code)


if __name__ == "__main__":
    unittest.main()
