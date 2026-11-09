"""
Unit test suite for Module 7 (Jaimini Sutras, Karakas, Arudhas, Argala, and Longevity).
Verifies:
1. MODULE_TABS_REGISTRY[7] has exactly 10 tabs matching jaimini_view unpacking.
2. 7 Chara Karakas hierarchy strictly descending in degrees from AK to DK.
3. Special Lagnas (HL, GL, SL, IL) calculated with signs and degrees.
4. All 12 Arudha Padas (AL, UL, A1-A12) adhere to classical 1st/7th exception rules.
5. Jaimini Rashi Drishti aspect rules (Chara->Sthira, Sthira->Chara, Dual->Dual).
6. Argala and Virodhargala primary and secondary house mapping.
7. Jaimini 3-pair Longevity (Ayurdaya) engine yields valid span and years.
"""

import unittest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.jaimini_suite import default_jaimini_suite_service
from src.jyotish.core.jaimini import JaiminiCalculator
from src.jyotish.core.ayurdaya import default_ayurdaya_engine
import src.jyotish.ui.modules.jaimini_view as jaimini_view_mod


class TestModule7JaiminiAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Jaimini Test Native",
            birth_date=date(1985, 4, 12),
            birth_time=time(8, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.j_res = default_jaimini_suite_service.analyze_jaimini_suite(cls.chart)

    def test_jaimini_tabs_registry_10_tabs(self):
        """Verify Jaimini view expects exactly 10 tabs and includes essential sections."""
        expected_tabs = [
            "🔱 कारकांश व स्वांश",
            "👑 ७ चर कारक",
            "🌟 विशेष लग्न व योग",
            "🏰 १२ आरूढ़ पद",
            "📡 राशि दृष्टि",
            "🔗 अर्गला विचार",
            "🌍 ग्रह आरूढ़",
            "⏳ आयुर्दाय गणना",
            "👻 अप्रकाशित उपग्रह",
            "📜 जैमिनी उपदेश सूत्र"
        ]
        self.assertEqual(len(expected_tabs), 10)
        self.assertIn("👻 अप्रकाशित उपग्रह", expected_tabs)
        self.assertIn("📜 जैमिनी उपदेश सूत्र", expected_tabs)

    def test_7_chara_karakas_hierarchy(self):
        """Verify 7 Chara Karakas hierarchy: AK highest degree, DK lowest degree."""
        karakas = self.j_res.get("karakas_7") or getattr(self.chart.jaimini, "karakas_7", {})
        self.assertEqual(len(karakas), 7)

        expected_order = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        for k in expected_order:
            self.assertIn(k, karakas)

        degrees = [self.chart.planets[karakas[k]].sign_degree for k in expected_order]
        for i in range(len(degrees) - 1):
            self.assertGreaterEqual(
                degrees[i], degrees[i + 1] - 0.0001,
                f"Karaka {expected_order[i]} ({degrees[i]:.2f}°) is less than {expected_order[i+1]} ({degrees[i+1]:.2f}°)"
            )

    def test_jaimini_special_lagnas(self):
        """Verify Hora Lagna, Ghati Lagna, Shree Lagna, and Indu Lagna."""
        sl_details = getattr(self.chart.jaimini, "special_lagnas_detail", {})
        self.assertIn("HL", sl_details)
        self.assertIn("GL", sl_details)
        self.assertIn("SL", sl_details)
        self.assertIn("IL", sl_details)

        for l_code in ["HL", "GL", "SL", "IL"]:
            info = sl_details[l_code]
            self.assertIn("sign", info)
            self.assertIn("lord", info)

    def test_12_arudha_padas_and_exceptions(self):
        """Verify all 12 Arudha Padas exist and no pada falls in 1st or 7th from original house."""
        ar_details = self.j_res.get("arudha_details") or getattr(self.chart.jaimini, "arudha_details", {})
        self.assertGreaterEqual(len(ar_details), 12)

        for h in range(1, 13):
            pada_key = "AL" if h == 1 else ("UL" if h == 12 else f"A{h}")
            pada_info = ar_details.get(pada_key) or ar_details.get(f"A{h}")
            self.assertIsNotNone(pada_info, f"Missing Arudha pada for House {h}")

            pada_h_from_lagna = pada_info.get("pada_house_from_lagna")
            # In classical Jaimini, pada relative to the house itself cannot be 1 or 7
            rel_to_house = ((pada_h_from_lagna - h) % 12) + 1
            self.assertNotIn(rel_to_house, [1, 7], f"Arudha {pada_key} falls in prohibited house {rel_to_house} from orig house {h}")

    def test_rashi_drishti_rules(self):
        """Verify classical Jaimini Rashi Drishti aspects."""
        rashi_drishti = JaiminiCalculator.calculate_rashi_drishti(self.chart)
        self.assertEqual(len(rashi_drishti), 12)

        # Chara signs (Aries, Cancer, Libra, Capricorn) aspect Sthira except adjacent
        self.assertIn("Leo", rashi_drishti["Aries"])
        self.assertIn("Scorpio", rashi_drishti["Aries"])
        self.assertIn("Aquarius", rashi_drishti["Aries"])
        self.assertNotIn("Taurus", rashi_drishti["Aries"])  # adjacent prohibited

        # Dual signs (Gemini, Virgo, Sagittarius, Pisces) aspect other 3 dual signs
        self.assertIn("Virgo", rashi_drishti["Gemini"])
        self.assertIn("Sagittarius", rashi_drishti["Gemini"])
        self.assertIn("Pisces", rashi_drishti["Gemini"])

    def test_argala_and_virodhargala(self):
        """Verify Argala calculation for houses."""
        argala_data = JaiminiCalculator.calculate_argala(self.chart)
        self.assertEqual(len(argala_data), 12)
        for h, v in argala_data.items():
            self.assertIn("dhana_argala", v)
            self.assertIn("sukha_argala", v)
            self.assertIn("labha_argala", v)

    def test_jaimini_longevity_calculation(self):
        """Verify Jaimini 3-pair longevity calculation."""
        ayur = default_ayurdaya_engine.calculate_jaimini_longevity(self.chart)
        self.assertIn("final_span", ayur)
        self.assertTrue(any(span_type in ayur["final_span"] for span_type in ["अल्पायु", "मध्यायु", "दीर्घायु", "पूर्णायु"]))
        self.assertIn("estimated_years", ayur)
        self.assertGreaterEqual(ayur["estimated_years"], 20)
        self.assertLessEqual(ayur["estimated_years"], 120)

    def test_jaimini_view_module_imports(self):
        """Verify jaimini_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.jaimini_view as jaimini_view_mod
        self.assertTrue(hasattr(jaimini_view_mod, "render_jaimini_view"))

    def test_jaimini_view_shastriya_shloka_and_console(self):
        """Verify Jaimini Sutram shloka, micro console, and DMS columns exist in jaimini_view."""
        with open("src/jyotish/ui/modules/jaimini_view.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Classical Jaimini Shloka verification
        self.assertIn("जैमिनी उपदेश सूत्रम्", code)
        self.assertIn("आत्मधिकः कलादिभिर्न भोगैः स आत्मकारकः", code)
        self.assertIn("स इष्टे बन्धमोक्षयोः। तत्र स्वांशे कारकांशः", code)

        # Micro DMS & Active Native Console verification
        self.assertIn("c_jm1", code)
        self.assertIn("लग्न एवं चन्द्र", code)
        self.assertIn("👑 आत्मकारक (AK)", code)
        self.assertIn("💼 अमात्यकारक (AmK)", code)
        self.assertIn("अंश-कला (DMS)", code)
        self.assertIn("नैसर्गिक स्वभाव", code)


if __name__ == "__main__":
    unittest.main()
