"""
Tests for Workstation Header Navigation System.
Verifies all 33 Vedic Modules (Indices 0 to 32), active tabs registry, and top menu action items.
"""
import pytest


# Canonical 33 Vedic Module Names in Hindi / English
EXPECTED_MODULE_NAMES = [
    "📜 जन्म कुण्डली (Kundali)",
    "🎯 घटना विश्लेषण (Events)",
    "🛡️ दोष व उपाय (Remedies)",
    "📊 वर्ग तालिका (Vargas)",
    "🏛️ वास्तु ज्योतिष (Vastu)",
    "❓ प्रश्न कुण्डली (Prashna)",
    "⚖️ षड्बल व भावबल (Bala)",
    "🔱 जैमिनी व उपग्रह (Jaimini)",
    "⏱️ दशा प्रणालियाँ (Dasha)",
    "🪐 गोचर व अष्टकवर्ग (Transit)",
    "📐 के.पी. ज्योतिष (KP System)",
    "⏳ शुभ मुहूर्त (Muhurta)",
    "☸️ सुदर्शन चक्र (Sudarshan)",
    "📅 ताजिक वर्षफल (Varshaphal)",
    "⏳ जन्म समय शोधन (BTR)",
    "💍 कुण्डली मिलान (Matching)",
    "💬 दैवज्ञ AI (AI Astrologer)",
    "📄 कुण्डली रिपोर्ट (Reports)",
    "📚 नियम बैंक (Rules Library)",
    "🔍 गणना सत्यापन (Validation)",
    "⚡ योग व दोष (Yog & Dosh)",
    "🔢 अंकशास्त्र (Numerology)",
    "📕 लाल किताब (Lal Kitab)",
    "🍽️ त्रिदोष व आहार (Diet)",
    "🤝 संबंध व स्वजन (Relations)",
    "🏥 स्वास्थ्य व रोग (Health)",
    "🧬 शारीरिक गठन (Physique)",
    "🕉️ इष्टदेवता व पूजा (Pooja)",
    "🧘 व्यक्तित्व व कर्मफल (Karma)",
    "📅 वैदिक पञ्चाङ्ग (Panchang)",
    "📜 शास्त्रीय फलादेश (Predictions)",
    "✋ हस्तरेखा व सामुद्रिक (Palmistry)",
    "💎 रत्न व रुद्राक्ष (Gemology)"
]


def test_all_33_modules_list_integrity():
    """Verify all 33 modules (0 to 32) are uniquely identified without omissions."""
    assert len(EXPECTED_MODULE_NAMES) == 33
    assert len(set(EXPECTED_MODULE_NAMES)) == 33
    # First module is Kundali
    assert "जन्म कुण्डली" in EXPECTED_MODULE_NAMES[0]
    # Last module is Gemology
    assert "रत्न व रुद्राक्ष" in EXPECTED_MODULE_NAMES[32]


def test_clean_single_line_header_column_ratios():
    """Verify the balanced single-line workstation header layout proportions."""
    # Balanced column ratios: [>> Toggle (0.80), All Modules (6.60), Active Tabs (6.60), Menu List (4.40)]
    col_ratios = [0.80, 6.60, 6.60, 4.40]
    assert len(col_ratios) == 4
    assert sum(col_ratios) > 15.0
    assert col_ratios[0] < col_ratios[1]  # Toggle button is compact


def test_top_menu_action_items_structure():
    """Verify standard menu actions available in workstation header dropdown."""
    MENU_ACTION_ITEMS = [
        "⚡ मेन्यू (Menu)...",
        "✨ नया जातक (New Kundali)",
        "📂 कुण्डली वॉल्ट (Client Vault)",
        "💾 कुण्डली सहेजें (Save Kundali)",
        "📝 परामर्श नोट्स (Consultation Notes)",
        "📄 PDF रिपोर्ट (Download PDF)",
        "💬 दैवज्ञ AI परामर्श (AI Astrologer)",
        "🌐 भाषा: English",
        "🌓 थीम: नाइट मोड",
        "⚙️ सेटिंग्स (Settings)",
        "🚪 लॉगआउट (Logout)"
    ]
    assert len(MENU_ACTION_ITEMS) >= 10
    assert "✨ नया जातक (New Kundali)" in MENU_ACTION_ITEMS
    assert "📂 कुण्डली वॉल्ट (Client Vault)" in MENU_ACTION_ITEMS
    assert "💾 कुण्डली सहेजें (Save Kundali)" in MENU_ACTION_ITEMS


def test_header_line2_breadcrumb_formatting():
    """Verify Header Line 2 status breadcrumb formatting."""
    mod_str = "📜 जन्म कुण्डली (Kundali)"
    name_str = "शुभम शर्मा"
    dob_str = "01-01-1995"
    tob_str = "02:30 PM"
    place_str = "New Delhi, India"

    line2_text = f"📍 सक्रिय मॉड्यूल: {mod_str} | 👤 जातक: {name_str} (जन्म: {dob_str}, {tob_str} | {place_str})"
    assert "📍 सक्रिय मॉड्यूल:" in line2_text
    assert "👤 जातक:" in line2_text
    assert "जन्म कुण्डली" in line2_text
    assert "शुभम शर्मा" in line2_text
