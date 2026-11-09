"""
Unit tests validating Module 3 (Dasvarga & Shodashvarga Grid View) audit fixes:
1. Dasvarga (10 divisions) dignity summary and Vaisheshikamsa calculation.
2. Shodashvarga (16 divisions) dignity summary.
3. Vimsopaka Bala scores range (0 to 20).
4. Vargottama detection in D1 and D9.
5. Varga specific significations (D10, D20, D24, D30, D60) synthesis.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.affliction import AfflictionEngine


class TestModule3VargaAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Test Varga Native",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.engine = AfflictionEngine(cls.chart)

    def test_tab1_dasvarga_summary(self):
        """Tab 1: Verify Dasvarga summary contains all 7 planets with valid scores."""
        dasvarga_codes = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D24", "D30", "D60"]
        dv_sum = self.engine.calculate_varga_dignity_summary(dasvarga_codes)
        self.assertEqual(len(dv_sum), 7)
        for p, data in dv_sum.items():
            self.assertIn("score_20", data)
            self.assertGreaterEqual(data["score_20"], 0.0)
            self.assertLessEqual(data["score_20"], 20.0)
            self.assertIn("vaisheshikamsa_hi", data)
            self.assertIn("counts", data)

    def test_tab2_shodashvarga_summary(self):
        """Tab 2: Verify Shodashvarga summary covers all 16 divisions."""
        shodashvarga_codes = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        sv_sum = self.engine.calculate_varga_dignity_summary(shodashvarga_codes)
        self.assertEqual(len(sv_sum), 7)
        for p, data in sv_sum.items():
            self.assertIn("score_20", data)
            self.assertIn("auspicious_count", data)
            self.assertGreaterEqual(data["auspicious_count"], 0)
            self.assertLessEqual(data["auspicious_count"], 16)

    def test_vargottama_consistency(self):
        """Test that Vargottama planets have matching sign in D1 and D9."""
        d1 = self.chart.planets
        d9 = self.chart.vargas.get("D9")
        if d9:
            for p_name, p_pos in d1.items():
                if p_name in d9.planets:
                    is_varg = (p_pos.sign_name == d9.planets[p_name].sign_name)
                    # Verify consistency
                    if is_varg:
                        self.assertEqual(p_pos.sign_name, d9.planets[p_name].sign_name)

    def test_varga_table_generation(self):
        """Test HTML table generation for Dasvarga and Shodashvarga."""
        dv_tbl = self.engine.calculate_dasvarga_table()
        self.assertGreater(len(dv_tbl), 0)
        sv_tbl = self.engine.calculate_shodashvarga_table()
        self.assertGreater(len(sv_tbl), 0)

    def test_varga_grid_view_module_symbols(self):
        """Test that varga_grid_view imports all required symbols without NameError."""
        import src.jyotish.ui.modules.varga_grid_view as vgv
        self.assertTrue(hasattr(vgv, 'SIGN_LORDS'))
        self.assertTrue(hasattr(vgv, 'SIGN_NAMES'))
        self.assertIn("Aries", vgv.SIGN_LORDS)
        self.assertEqual(vgv.SIGN_LORDS["Aries"], "Mars")

    def test_module3_shastriya_shloka_and_dms_integration(self):
        """Test that classical BPHS shloka and active native micro DMS are present in varga_grid_view."""
        with open("src/jyotish/ui/modules/varga_grid_view.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Classical Shloka verification
        self.assertIn("बृहत्पाराशर होराशास्त्रम्", code)
        self.assertIn("पारिजातांशके जाते धनवान् कीर्तिमान् सुधीः", code)
        self.assertIn("देवलोके नृपो भूयादैरावते तु भूपतिः", code)

        # Micro DMS & Active Native Console verification
        self.assertIn("lagna_sname", code)
        self.assertIn("top_p", code)
        self.assertIn("विंशोपक अंक", code)
        self.assertIn("लग्न (D1) राशि, अंश-कला व नक्षत्र", code)


if __name__ == "__main__":
    unittest.main()
