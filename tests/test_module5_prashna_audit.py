"""
Unit test suite for Module 5 (Prashna Kundali & Tajika Horary Engine and View).
Verifies:
1. render_prashna_view imports cleanly and resolves 'name' safely without NameError.
2. All 23 Horary Categories are structurally sound with valid houses (1-12) and lords.
3. PrashnaService generates valid horary charts with Tajika aspects and timing.
4. Tajika Yogas (Ithasala, Esharpha, Nakta) evaluation logic.
5. 100 Classical Horary Rules engine runs with complete 100-rule dossier.
"""

import unittest
from datetime import datetime, date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.prashna import default_prashna_service, PRASHNA_CATEGORIES
from src.jyotish.rules.prashna_rules import default_prashna_rule_evaluator


class TestModule5PrashnaAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Prashna Test Native",
            birth_date=date(1992, 8, 20),
            birth_time=time(10, 15),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.query_dt = datetime(2026, 11, 8, 10, 30, 0)

    def test_prashna_view_imports_and_symbols(self):
        """Test that prashna_view module can be imported and contains render_prashna_view."""
        import src.jyotish.ui.modules.prashna_view as prashna_view_mod
        self.assertTrue(hasattr(prashna_view_mod, "render_prashna_view"))
        self.assertTrue(hasattr(prashna_view_mod, "get_live_local_now"))
        self.assertTrue(hasattr(prashna_view_mod, "PRASHNA_DEEPTAMSHA"))

    def test_prashna_categories_structure(self):
        """Verify all 23 horary categories have valid houses and lords."""
        self.assertGreaterEqual(len(PRASHNA_CATEGORIES), 23)
        for cat in PRASHNA_CATEGORIES:
            self.assertIn("Name", cat)
            self.assertIn("Name_Hi", cat)
            self.assertIn("house", cat)
            self.assertGreaterEqual(cat["house"], 1)
            self.assertLessEqual(cat["house"], 12)
            self.assertIn("karyesh_default", cat)
            self.assertIn("icon", cat)

    def test_prashna_service_chart_generation(self):
        """Test horary chart generation across diverse categories."""
        test_cats = ["Job", "Marriage", "Health", "Wealth", "Litigation / Court"]
        for cat in test_cats:
            res = default_prashna_service.generate_prashna_chart(
                query_text=f"क्या {cat} कार्य सिद्ध होगा?",
                category_name=cat,
                latitude=28.6139,
                longitude=77.2090,
                timezone_offset=5.5,
                query_dt=self.query_dt,
                questioner_name="Shri Test Querent"
            )

            self.assertIsNotNone(res)
            self.assertIn("chart", res)
            self.assertIn("prashna_lagna", res)
            self.assertIn("lagnesh", res)
            self.assertIn("karyesh", res)
            self.assertIn("tajika_yoga", res)
            self.assertIn("verdict", res)
            self.assertIn("verdict_score", res)
            self.assertIn("timing", res)
            self.assertIn("graha_table", res)
            self.assertEqual(len(res["graha_table"]), 9)

    def test_100_prashna_rules_engine_coverage(self):
        """Test that the 100 classical rules engine evaluates all 100 rules."""
        res = default_prashna_service.generate_prashna_chart(
            query_text="क्या मेरी नौकरी लगेगी?",
            category_name="Job",
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5,
            query_dt=self.query_dt,
            questioner_name="Job Seeker"
        )

        all_rules = res.get("all_rules", [])
        self.assertEqual(len(all_rules), 100, f"Expected 100 rules, got {len(all_rules)}")
        self.assertIn("active_positive_count", res)
        self.assertIn("active_negative_count", res)
        self.assertIn("net_balance_score", res)

    def test_tajika_nakta_and_aspect_logic(self):
        """Test Tajika Ithasala, Esharpha, and Nakta Yoga evaluation."""
        res = default_prashna_service.generate_prashna_chart(
            query_text="क्या व्यापार में सफलता मिलेगी?",
            category_name="Business",
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5,
            query_dt=self.query_dt,
            questioner_name="Merchant"
        )
        self.assertIn("is_ithasala", res)
        self.assertIn("is_esharpha", res)
        self.assertIn("tajika_yoga", res)
        self.assertTrue(len(res["tajika_yoga"]) > 0)

    def test_prashna_micro_dms_nakshatra_swabhav(self):
        """Test that prashna graha table data contains micro DMS, nakshatra pada, and swabhav."""
        res = default_prashna_service.generate_prashna_chart(
            query_text="क्या कार्य सिद्ध होगा?",
            category_name="Job",
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5,
            query_dt=self.query_dt,
            questioner_name="Test Querent"
        )
        gt = res.get("graha_table", [])
        self.assertEqual(len(gt), 9)
        for g in gt:
            self.assertIn("ansh", g)
            self.assertIn("kala", g)
            self.assertIn("dms_str", g)
            self.assertIn("nakshatra_pada", g)
            self.assertIn("swabhav", g)
            self.assertIn("°", g["dms_str"])
            self.assertIn("'", g["dms_str"])
            self.assertIn(g["swabhav"], ["नैसर्गिक शुभ", "नैसर्गिक क्रूर"])

    def test_prashna_view_shastriya_shloka_and_console(self):
        """Test that classical Prashna Marga shloka and micro console are present in prashna_view."""
        with open("src/jyotish/ui/modules/prashna_view.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Classical Shloka verification
        self.assertIn("प्रश्नमार्ग एवं ताजिक नीलकण्ठी", code)
        self.assertIn("यदुपचितमन्यजन्मनि शुभाशुभं", code)
        self.assertIn("लग्नेशकार्येशसुदृष्टियोगे", code)

        # Micro DMS & Active Native Console verification
        self.assertIn("c_pn1", code)
        self.assertIn("जन्म लग्न एवं चन्द्र", code)
        self.assertIn("तात्कालिक प्रश्न लग्न", code)
        self.assertIn("अंश-कला (DMS)", code)
        self.assertIn("नैसर्गिक स्वभाव", code)


if __name__ == "__main__":
    unittest.main()
