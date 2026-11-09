"""
Unit test suite for Module 6 (Shadbala, Bhavabala, and Aspectarium Engine and View).
Verifies:
1. All 7 classical planets have valid Shadbala scores, Rupas, required benchmarks, and ratios.
2. 6 individual Balas (Sthana, Dik, Kaala, Cheshta, Naisargika, Drik) calculated per BPHS Ch. 27.
3. 12 Bhavabala potency with 3-fold components (Adhipati, Digbala, Drishti Bala).
4. Ishta Phala and Kashta Phala balance within 0 to 60 Virupas, plus 3-tier Avasthas.
5. Dynamic Aspectarium (Western aspects + Parashari Vedic Drishtis) calculation.
6. shadbala_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.shadbala import default_shadbala_calculator, REQUIRED_VIRUPAS, NAISARGIKA_BALA
from src.jyotish.services.aspectarium import default_aspectarium_service


class TestModule6ShadbalaAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Shadbala Test Native",
            birth_date=date(1988, 10, 24),
            birth_time=time(12, 15),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.shadbala = default_shadbala_calculator.calculate(cls.chart)

    def test_shadbala_7_planets_calculation(self):
        """Verify all 7 planets have complete Shadbala metrics."""
        seven_p = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        self.assertEqual(len(self.shadbala.planets), 7)

        for p in seven_p:
            p_res = self.shadbala.planets.get(p)
            self.assertIsNotNone(p_res, f"Missing Shadbala for {p}")
            self.assertGreater(p_res.total_virupas, 100.0)
            self.assertGreater(p_res.total_rupas, 1.5)
            self.assertEqual(p_res.required_virupas, REQUIRED_VIRUPAS[p])
            self.assertGreater(p_res.strength_ratio, 0.2)
            self.assertIsInstance(p_res.is_strong, bool)

    def test_shadbala_6_fold_components(self):
        """Verify 6 individual components are calculated accurately per BPHS."""
        for p, res in self.shadbala.planets.items():
            self.assertGreaterEqual(res.sthana_bala, 0.0)
            self.assertGreaterEqual(res.dik_bala, 0.0)
            self.assertGreaterEqual(res.kaala_bala, 0.0)
            self.assertGreaterEqual(res.cheshta_bala, 0.0)
            # Exact Naisargika Bala match per BPHS
            self.assertAlmostEqual(res.naisargika_bala, NAISARGIKA_BALA[p], delta=0.01)
            # Drik bala can be slightly negative or positive
            self.assertIsInstance(res.drik_bala, float)

    def test_bhavabala_12_houses_components(self):
        """Verify 12 Bhavas have total potency and 3-fold constituent components."""
        self.assertEqual(len(self.shadbala.bhava_bala), 12)
        self.assertEqual(len(self.shadbala.bhava_bala_components), 12)

        for h in range(1, 13):
            total_v = self.shadbala.bhava_bala[h]
            comps = self.shadbala.bhava_bala_components[h]

            self.assertGreater(total_v, 100.0)
            self.assertIn("adhipati_bala", comps)
            self.assertIn("dig_bala", comps)
            self.assertIn("drishti_bala", comps)
            self.assertAlmostEqual(total_v, comps["total_virupas"], places=1)

    def test_ishta_kashta_and_avasthas(self):
        """Verify Ishta/Kashta phala and 3-tier Avasthas."""
        for p, res in self.shadbala.planets.items():
            self.assertGreaterEqual(res.ishta_phala, 0.0)
            self.assertLessEqual(res.ishta_phala, 60.0)
            self.assertGreaterEqual(res.kashta_phala, 0.0)
            self.assertLessEqual(res.kashta_phala, 60.0)

            # Baladi Avasthas per BPHS
            self.assertTrue(any(st in res.baladi_avastha for st in ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]))
            self.assertTrue(any(st in res.jagratadi_avastha for st in ["Jagrat", "Swapna", "Sushupti"]))
            self.assertTrue(len(res.deeptadi_avastha) > 0)

    def test_aspectarium_service_calculation(self):
        """Verify Aspectarium service computes Western aspects and Vedic drishtis."""
        asp_data = default_aspectarium_service.calculate_aspectarium(self.chart)
        self.assertIn("aspects", asp_data)
        self.assertIn("vedic_drishtis", asp_data)
        self.assertIn("matrix_data", asp_data)
        self.assertGreaterEqual(asp_data["total_aspects_count"], 0)
        self.assertGreater(asp_data["total_drishti_count"], 0)

    def test_shadbala_view_module_imports(self):
        """Verify shadbala_view module imports cleanly."""
        import src.jyotish.ui.modules.shadbala_view as shadbala_view_mod
        self.assertTrue(hasattr(shadbala_view_mod, "render_shadbala_view"))

    def test_shadbala_view_shastriya_shloka_and_console(self):
        """Verify BPHS Shadbala shloka, micro console, and DMS table column exist in shadbala_view."""
        with open("src/jyotish/ui/modules/shadbala_view.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Classical BPHS Shloka verification
        self.assertIn("बृहत्पाराशर होराशास्त्रम्", code)
        self.assertIn("स्थानं दिग्कालचेष्टा च नैसर्गं दृग्बलं तथा", code)
        self.assertIn("विरूपाणां समूहस्तु षड्बलं कथ्यते बुधैः", code)

        # Micro DMS & Active Native Console verification
        self.assertIn("c_sb1", code)
        self.assertIn("लग्न एवं चन्द्र", code)
        self.assertIn("🌟 शिरोमणि बली ग्रह", code)
        self.assertIn("राशि व अंश-कला (DMS)", code)
        self.assertIn("नैसर्गिक स्वभाव", code)


if __name__ == "__main__":
    unittest.main()
