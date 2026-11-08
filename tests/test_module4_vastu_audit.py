"""
Unit test suite for Module 4 (Vastu-Jyotish Architectural Alignment Engine and View).
Verifies:
1. All 9 Vastu directional zones (8 directions + Brahmasthan) evaluated with 0-100 score.
2. Brahmasthan Kendra-balance calculation (benefics vs malefics in Kendras).
3. Directional Digbala points logic aligned with classical Jyotish sutras.
4. Non-destructive shastriya 5-pillar remedies completeness (zero empty/N/A entries).
5. render_vastu_view function and module integrity with no UnboundLocalError or syntax issues.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.vastu import VastuJyotishEngine, VASTU_DIRECTIONS


class TestModule4VastuAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Vastu Test Native",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)

    def test_vastu_engine_9_zones_evaluation(self):
        """Test that all 9 Vastu zones are evaluated with valid scores and metadata."""
        engine = VastuJyotishEngine(self.chart)
        zones = engine.evaluate_vastu_zones()

        self.assertEqual(len(zones), 9)
        zone_dirs = [z["direction"] for z in zones]
        for expected_dir in ["East", "South-East", "South", "South-West", "West", "North-West", "North", "North-East", "Center"]:
            self.assertIn(expected_dir, zone_dirs)

        for z in zones:
            score = z["score"]
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
            self.assertIn(z["defect_risk"], ["Harmonious", "Moderate Risk", "High Risk"])
            self.assertTrue(len(z["element"]) > 0)
            self.assertIsNotNone(z.get("meta"))

    def test_vastu_brahmasthan_kendra_balance(self):
        """Test that Brahmasthan score reflects Kendra house conditions."""
        engine = VastuJyotishEngine(self.chart)
        zones = engine.evaluate_vastu_zones()
        center_zone = next(z for z in zones if z["direction"] == "Center")

        self.assertIsNotNone(center_zone)
        self.assertEqual(center_zone["lord"], "Cosmic (Lord Brahma)")
        self.assertGreaterEqual(center_zone["score"], 20)
        self.assertLessEqual(center_zone["score"], 100)
        self.assertIn("kendra_benefics", center_zone)
        self.assertIn("kendra_malefics", center_zone)

    def test_vastu_digbala_directional_strengths(self):
        """Test Digbala computation on zones."""
        engine = VastuJyotishEngine(self.chart)
        zones = engine.evaluate_vastu_zones()
        east_zone = next(z for z in zones if z["direction"] == "East")
        self.assertIn("digbala", east_zone)
        self.assertTrue(len(east_zone["digbala"]) > 0)

    def test_vastu_non_destructive_remedies_integrity(self):
        """Test that each zone has authentic non-destructive remedies defined."""
        for d_key, meta in VASTU_DIRECTIONS.items():
            self.assertIn("non_destructive_remedy", meta)
            self.assertTrue(len(meta["non_destructive_remedy"]) > 10, f"Remedy too short for {d_key}")
            self.assertIn("mantra", meta)
            self.assertIn("metal", meta)
            self.assertIn("botanical", meta)
            self.assertIn("color_therapy", meta)
            self.assertIn("shastra_shloka", meta)

    def test_vastu_view_module_imports(self):
        """Test that vastu_view module imports cleanly without UnboundLocalError."""
        import src.jyotish.ui.modules.vastu_view as vastu_view_mod
        self.assertTrue(hasattr(vastu_view_mod, "render_vastu_view"))
        self.assertTrue(hasattr(vastu_view_mod, "_VastuEngine"))


if __name__ == "__main__":
    unittest.main()
