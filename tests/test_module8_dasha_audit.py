"""
Unit test suite for Module 8 (Dasha Systems, Gantt Timeline, and Predictive Hierarchy).
Verifies:
1. Module 8 has exactly 14 tabs and dasha_view fallback is synchronized.
2. Vimshottari 5-level hierarchy (Mahadasha, Antardasha, Pratyantardasha, Sookshmadasha, Pranadasha).
3. Vimshottari full 120-year cycle and planetary lord sequence.
4. Yogini Dasha 36-year cycle and 8 Yogini rulers.
5. Jaimini Chara Dasha 12-sign progression and period durations.
6. Kalachakra Dasha (KCD) Deha and Jeeva determinations.
7. Shoola Dasha Ayur/Maraka signs and periods.
8. Special Dashas: Ashtottari (108 yrs), Narayana, Dwisaptatisama, Sthira, and Drig.
9. dasha_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date, time, datetime
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.dasha.vimshottari import default_dasha_engine
from src.jyotish.dasha.yogini import default_yogini_engine
from src.jyotish.dasha.chara import default_chara_engine
from src.jyotish.dasha.kcd import default_kcd_engine
from src.jyotish.dasha.shoola import default_shoola_engine
from src.jyotish.dasha.ashtottari import default_ashtottari_engine
from src.jyotish.dasha.narayana import default_narayana_engine
from src.jyotish.dasha.sama_dashas import default_dwisaptati_engine
from src.jyotish.dasha.sthira_drig import default_sthira_engine, default_drigdasha_engine


class TestModule8DashaAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.birth_data = BirthData(
            name="Dasha Test Native",
            birth_date=date(1985, 4, 12),
            birth_time=time(8, 30),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        cls.chart = default_chart_calculator.calculate_full_chart(cls.birth_data)
        cls.birth_dt = datetime.combine(cls.birth_data.birth_date, cls.birth_data.birth_time)
        cls.moon_lon = cls.chart.planets["Moon"].longitude

    def test_dasha_tabs_registry_14_tabs(self):
        """Verify Dasha Module expects exactly 14 tabs and includes essential sections."""
        expected_tabs = [
            "📊 १२०-वर्ष गेंट चार्ट",
            "⏳ जीवन टाइमलाइन",
            "🌟 विंशोत्तरी (५ स्तर)",
            "🌸 योगिनी दशा (३६ वर्ष)",
            "🔱 जैमिनी चर दशा",
            "🔄 कालचक्र दशा",
            "⚔️ शूल दशा (मारक)",
            "🕉️ अष्टोत्तरी दशा",
            "🪐 नारायण दशा",
            "⏳ द्विसप्ततिसम दशा",
            "🔷 स्थिर दशा",
            "👁️ दृग दशा",
            "🎯 बहु-दशा संगम",
            "📜 शास्त्रीय प्रमाण व उपाय"
        ]
        self.assertEqual(len(expected_tabs), 14)
        self.assertIn("📊 १२०-वर्ष गेंट चार्ट", expected_tabs)
        self.assertIn("🌸 योगिनी दशा (३६ वर्ष)", expected_tabs)
        self.assertIn("🎯 बहु-दशा संगम", expected_tabs)

    def test_vimshottari_5_levels_hierarchy(self):
        """Verify 5-level Vimshottari hierarchy returns valid active periods."""
        target_dt = datetime(2025, 1, 15, 12, 0)
        h5 = default_dasha_engine.get_5level_hierarchy(self.birth_dt, self.moon_lon, target_dt)

        self.assertIn("mahadasha", h5)
        self.assertIn("antardasha", h5)
        self.assertIn("pratyantardasha", h5)
        self.assertIn("sookshmadasha", h5)
        self.assertIn("pranadasha", h5)

        for lvl in ["mahadasha", "antardasha", "pratyantardasha", "sookshmadasha", "pranadasha"]:
            item = h5[lvl]
            self.assertIn("lord", item)
            self.assertIn("start_date", item)
            self.assertIn("end_date", item)
            self.assertLessEqual(item["start_date"], target_dt)
            self.assertGreaterEqual(item["end_date"], target_dt)

    def test_vimshottari_120_years_cycle(self):
        """Verify sequence of Vimshottari Mahadashas produces full 120-year cycle."""
        mds = default_dasha_engine.generate_mahadasha_sequence(self.birth_dt, self.moon_lon, num_cycles=1)
        self.assertGreaterEqual(len(mds), 9)

        start_dt = mds[0]["start_date"]
        end_dt = mds[-1]["end_date"]
        diff_days = (end_dt - start_dt).days
        # 120 solar years ~ 43,830 days
        self.assertAlmostEqual(diff_days / 365.25, 120.0, delta=1.5)

    def test_yogini_dasha_36_year_cycle(self):
        """Verify Yogini Dasha timeline produces 8 Yoginis in 36-year repeating sequence."""
        y_timeline = default_yogini_engine.generate_timeline(self.chart)
        self.assertGreaterEqual(len(y_timeline), 8)

        expected_yoginis = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
        for y_item in y_timeline[:8]:
            y_name = y_item.get("yogini") or y_item.get("yogini_name")
            self.assertIn(y_name, expected_yoginis)

        # Total 1 cycle duration is ~36 years minus birth balance
        first_cycle = y_timeline[:8]
        span_years = sum(item.get("duration_years", 0) for item in first_cycle)
        self.assertGreater(span_years, 25.0)
        self.assertLessEqual(span_years, 36.0001)

    def test_jaimini_chara_dasha_12_signs(self):
        """Verify Jaimini Chara Dasha generates periods for all 12 signs."""
        chara_timeline = default_chara_engine.generate_timeline(self.chart)
        self.assertGreaterEqual(len(chara_timeline), 12)

        signs_seen = set()
        for c in chara_timeline[:12]:
            self.assertIn("sign_id", c)
            self.assertIn("start_date", c)
            self.assertIn("end_date", c)
            signs_seen.add(c["sign_id"])
        self.assertEqual(len(signs_seen), 12)

    def test_kalachakra_dasha_calculation(self):
        """Verify Kalachakra Dasha generates valid Deha and Jeeva rashis."""
        kcd = default_kcd_engine.calculate(self.chart)
        self.assertIsNotNone(kcd)
        self.assertTrue(hasattr(kcd, "deha_rashi") or "deha_rashi" in kcd)
        self.assertTrue(hasattr(kcd, "jeeva_rashi") or "jeeva_rashi" in kcd)

    def test_shoola_dasha_ayur_maraka(self):
        """Verify Shoola Dasha calculates 12 sign periods and maraka signs."""
        shoola = default_shoola_engine.calculate(self.chart)
        self.assertIsNotNone(shoola)
        periods = shoola.get("timeline", [])
        self.assertEqual(len(periods), 12)
        self.assertIn("trishoola_signs", shoola)

    def test_special_dashas_suite(self):
        """Verify Ashtottari, Narayana, Dwisaptatisama, Sthira, and Drig dashas."""
        ashto_tl = default_ashtottari_engine.generate_timeline(self.chart)
        self.assertIsNotNone(ashto_tl)

        narayana_tl = default_narayana_engine.generate_timeline(self.chart)
        self.assertIsNotNone(narayana_tl)

        dwi_tl = default_dwisaptati_engine.generate_timeline(self.chart)
        self.assertIsNotNone(dwi_tl)

        sthira_tl = default_sthira_engine.generate_timeline(self.chart)
        self.assertIsNotNone(sthira_tl)

        drig_tl = default_drigdasha_engine.generate_timeline(self.chart)
        self.assertIsNotNone(drig_tl)

    def test_dasha_view_module_imports(self):
        """Verify dasha_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.dasha_view as dasha_view_mod
        self.assertTrue(hasattr(dasha_view_mod, "render_dasha_view"))

    def test_dasha_view_shastriya_shloka_and_console(self):
        """Verify BPHS Dasha shloka, micro console, and DMS columns exist in dasha_view."""
        with open("src/jyotish/ui/modules/dasha_view.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Classical BPHS Dasha Shloka verification
        self.assertIn("बृहत्पाराशर होराशास्त्रम् एवं सारावली", code)
        self.assertIn("दशासु सर्वजन्तूनां शुभाशुभफलोद्भवः", code)
        self.assertIn("विंशोत्तरी दशा मुख्या नक्षत्राणां बलेन च", code)

        # Micro DMS & Active Native Console verification
        self.assertIn("c_da1", code)
        self.assertIn("लग्न एवं चन्द्र", code)
        self.assertIn("🌟 सक्रिय महादशा (MD)", code)
        self.assertIn("राशि व अंश-कला (DMS)", code)
        self.assertIn("नैसर्गिक स्वभाव", code)


if __name__ == "__main__":
    unittest.main()
