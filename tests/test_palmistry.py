"""
Unit tests for Hastarekha & Samudrika Shastra Engine (Phase validation).
"""

import unittest
from src.jyotish.core.palmistry import (
    HastarekhaEngine,
    PalmInputProfile,
    MountStatus,
    LineStatus
)


class TestPalmistryEngine(unittest.TestCase):

    def setUp(self):
        self.profile = PalmInputProfile(
            hand_type="Square",
            has_buddha_eye=True,
            has_mystic_cross=True,
            has_matsya_sign=True,
            bracelets_count=3
        )

    def test_vitality_score_calculation(self):
        score = HastarekhaEngine._calc_vitality_score(self.profile)
        self.assertGreaterEqual(score, 70)
        self.assertLessEqual(score, 100)

    def test_career_score_calculation(self):
        score = HastarekhaEngine._calc_career_score(self.profile)
        self.assertGreaterEqual(score, 60)
        self.assertLessEqual(score, 100)

    def test_classical_yogas_detection(self):
        yogas = HastarekhaEngine._detect_palm_yogas(self.profile)
        yoga_names = [y["name"] for y in yogas]
        self.assertTrue(any("यव योग" in n for n in yoga_names))
        self.assertTrue(any("रहस्यमयी क्रॉस" in n for n in yoga_names))
        self.assertTrue(any("मत्स्य योग" in n for n in yoga_names))
        self.assertTrue(any("त्रि-मणिबंध" in n for n in yoga_names))

    def test_full_palm_report_generation(self):
        report = HastarekhaEngine.analyze_palm(self.profile, chart=None)
        self.assertIsNotNone(report.hand_summary)
        self.assertEqual(len(report.sections), 6)
        self.assertIn("Grade", report.overall_samudrika_grade)
        
        # Check that Sanskrit shlokas and sources are attached
        for sec in report.sections:
            self.assertTrue(len(sec.shloka_sanskrit) > 0)
            self.assertTrue(len(sec.shloka_source) > 0)
            self.assertTrue(len(sec.detailed_points) > 0)


    def test_palm_image_analysis(self):
        import io
        from PIL import Image
        img = Image.new("RGB", (200, 200), color=(220, 180, 150))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

        prof, scan_res = HastarekhaEngine.analyze_palm_image(image_bytes)
        self.assertIsNotNone(prof)
        self.assertIsNotNone(scan_res)
        self.assertGreaterEqual(scan_res.confidence_pct, 80)
        self.assertTrue(len(scan_res.detected_features) > 0)


if __name__ == "__main__":
    unittest.main()
