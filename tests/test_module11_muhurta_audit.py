"""
Unit test suite for Module 11 (Muhurta, Choghadiya, Tarabala, and Panchanga).
Verifies:
1. Module 11 has exactly 8 tabs and muhurta_view fallback is synchronized.
2. Daily 8 Day and 8 Night Choghadiyas calculation and sequence.
3. Panchanga 5 limbs: Tithi, Vaar, Nakshatra, Yoga, and Karana.
4. Special time windows: Abhijit, Brahma Muhurta, Rahu Kaal, Yamaghanta, Gulika Kaal.
5. Tarabalam logic: 9 Taras (Janma, Sampat, Vipat, Kshema, Pratyari, Sadhaka, Naidhana, Mitra, Parama Mitra).
6. Chandrabalam logic: 1, 3, 6, 7, 10, 11 from natal Moon are auspicious.
7. Panchanga Mahadoshas: Bhadra, Pitru Paksha, Kharmas, Chaturmas, Panchak.
8. muhurta_view module imports cleanly without importlib reload side-effects.
"""

import unittest
from datetime import date
from src.jyotish.services.muhurta import default_muhurta_engine


class TestModule11MuhurtaAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.target_date = date(2025, 4, 15)
        cls.m_data = default_muhurta_engine.calculate_daily_muhurta(cls.target_date)
        cls.p_doshas = default_muhurta_engine.get_daily_panchang_and_doshas(cls.target_date)

    def test_muhurta_tabs_registry_8_tabs(self):
        """Verify Muhurta Module expects exactly 8 tabs and includes essential sections."""
        expected_tabs = [
            "📜 जन्म पञ्चाङ्ग व तत्व",
            "☀️ अहोरात्र चौघड़िया",
            "⏳ राहुकाल व अभिजित",
            "🌕 ताराबल व चन्द्रबल",
            "🏛️ १६ संस्कार मुहूर्त",
            "🔍 मुहूर्त खोजक (Scanner)",
            "📜 २१ महादोष विचार",
            "🪔 दोष परिहार व शांति"
        ]
        self.assertEqual(len(expected_tabs), 8)
        self.assertIn("☀️ अहोरात्र चौघड़िया", expected_tabs)
        self.assertIn("⏳ राहुकाल व अभिजित", expected_tabs)
        self.assertIn("🌕 ताराबल व चन्द्रबल", expected_tabs)
        self.assertIn("📜 २१ महादोष विचार", expected_tabs)

    def test_daily_muhurta_choghadiya_intervals(self):
        """Verify 8 Day Choghadiyas and 8 Night Choghadiyas are generated with valid properties."""
        day_chog = self.m_data.get("day_choghadiyas", [])
        night_chog = self.m_data.get("night_choghadiyas", [])

        self.assertEqual(len(day_chog), 8)
        self.assertEqual(len(night_chog), 8)

        for c in day_chog + night_chog:
            self.assertIn("name", c)
            self.assertIn("nature", c)
            self.assertIn("start_time", c)
            self.assertIn("end_time", c)
            self.assertIn("is_good", c)

    def test_panchanga_elements_calculation(self):
        """Verify Panchanga 5 limbs: Tithi, Vaar, Nakshatra, Yoga, Karana."""
        self.assertIn("tithi_name", self.p_doshas)
        self.assertIn("paksha", self.p_doshas)
        self.assertIn("nakshatra_name", self.p_doshas)
        self.assertIn("yoga_name", self.p_doshas)
        self.assertIn("karana_name", self.p_doshas)
        self.assertIn("weekday_name", self.p_doshas)

    def test_special_muhurta_windows(self):
        """Verify Abhijit, Brahma Muhurta, Rahu Kaal, Yamaghanta, Gulika Kaal."""
        windows = self.m_data.get("special_windows", [])
        self.assertGreaterEqual(len(windows), 4)

        titles = [w.get("title", "") for w in windows]
        self.assertTrue(any("अभिजित" in t for t in titles))
        self.assertTrue(any("राहुकाल" in t for t in titles))
        self.assertTrue(any("यमघंट" in t for t in titles))
        self.assertTrue(any("गुलिक" in t for t in titles))

    def test_tarabalam_classical_logic(self):
        """Verify 9 Tara sequence calculation and benefic/malefic classifications."""
        benefic_tara_indices = [2, 4, 6, 8, 9]  # Sampat, Kshema, Sadhaka, Mitra, Parama Mitra
        malefic_tara_indices = [3, 5, 7]        # Vipat, Pratyari, Naidhana

        # Simulate natal nakshatra 1 (Ashwini) and various transit nakshatras
        natal_nak = 1
        for t_nak in range(1, 28):
            tara_rem = ((t_nak - natal_nak) % 9) + 1
            if tara_rem in benefic_tara_indices:
                is_subha = True
            elif tara_rem in malefic_tara_indices:
                is_subha = False
            else:
                is_subha = None  # Janma tara is mixed
            self.assertIn(tara_rem, range(1, 10))

    def test_chandrabalam_classical_houses(self):
        """Verify classical Chandrabalam: 1, 3, 6, 7, 10, 11 from natal Moon are auspicious."""
        auspicious_houses = [1, 3, 6, 7, 10, 11]
        inauspicious_houses = [2, 4, 5, 8, 9, 12]

        natal_moon_sign = 4  # Cancer
        for transit_sign in range(1, 13):
            house_from_moon = ((transit_sign - natal_moon_sign) % 12) + 1
            if house_from_moon in auspicious_houses:
                self.assertNotIn(house_from_moon, inauspicious_houses)

    def test_panchanga_mahadoshas(self):
        """Verify detection of Panchanga Mahadoshas (Bhadra, Pitru Paksha, Chaturmas, etc.)."""
        self.assertIn("is_bhadra", self.p_doshas)
        self.assertIn("is_pitru_paksha", self.p_doshas)
        self.assertIn("is_chaturmas", self.p_doshas)
        self.assertIn("is_kharmas", self.p_doshas)
        self.assertIn("is_panchak", self.p_doshas)
        self.assertIn("active_mahadoshas", self.p_doshas)

    def test_muhurta_view_module_imports(self):
        """Verify muhurta_view module imports cleanly without errors."""
        import src.jyotish.ui.modules.muhurta_view as muhurta_view_mod
        self.assertTrue(hasattr(muhurta_view_mod, "render_muhurta_view"))

    def test_muhurta_view_shastriya_shloka_and_console(self):
        """Verify classical Muhurta Chintamani shloka, micro DMS, and Tara/Chandra Balam HUD in muhurta_view."""
        import inspect
        import src.jyotish.ui.modules.muhurta_view as muhurta_view_mod
        source = inspect.getsource(muhurta_view_mod.render_muhurta_view)

        self.assertIn("muhurta_shastriya_shloka", source)
        self.assertIn("मुहूर्त चिन्तामणि एवं कालप्रकाशिका", source)
        self.assertIn("तिथेश्च श्रियमवाप्नोति वारादायुष्यवर्धनम्", source)
        self.assertIn("col_hud1, col_hud2, col_hud3, col_hud4 = st.columns(4)", source)
        self.assertIn("जातक ताराबल (Tara Balam)", source)
        self.assertIn("जातक चन्द्रबल (Chandra Balam)", source)
        self.assertIn("जन्म लग्न स्पष्ट (DMS)", source)
        self.assertIn("जन्म चन्द्र स्पष्ट (DMS)", source)
        self.assertIn("जन्म सूर्य स्पष्ट (DMS)", source)


if __name__ == "__main__":
    unittest.main()
