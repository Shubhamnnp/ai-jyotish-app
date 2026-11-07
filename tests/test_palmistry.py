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

        # Test X-Ray generation
        xray_bytes = HastarekhaEngine.generate_palm_xray(image_bytes, mode="neon_cyan")
        self.assertIsNotNone(xray_bytes)
        self.assertGreater(len(xray_bytes), 100)

    def test_palm_svg_rendering_right_and_left(self):
        from src.jyotish.ui.palmistry_renderer import PalmRenderer
        svg_right = PalmRenderer.render_palm_svg(self.profile, is_right_hand=True)
        self.assertIn("दायां हाथ (Right Palm)", svg_right)
        self.assertIn("हृदय रेखा", svg_right)
        self.assertIn("मस्तिष्क रेखा", svg_right)
        self.assertIn("जीवन रेखा", svg_right)
        self.assertIn("भाग्य रेखा", svg_right)
        self.assertIn("सूर्य रेखा", svg_right)
        self.assertIn("गुरु", svg_right)
        self.assertIn("शनि", svg_right)
        self.assertIn("शुक्र", svg_right)
        self.assertIn("चन्द्र", svg_right)

        svg_left = PalmRenderer.render_palm_svg(self.profile, is_right_hand=False)
        self.assertIn("बायां हाथ (Left Palm)", svg_left)
        self.assertIn("हृदय रेखा", svg_left)
        self.assertIn("मस्तिष्क रेखा", svg_left)


if __name__ == "__main__":
    unittest.main()
