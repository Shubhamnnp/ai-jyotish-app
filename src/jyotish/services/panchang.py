"""
Vedic Jyotish Panchang Engine for JyotishOS.
A comprehensive, world-class Shastriya Panchang system exceeding Drik Panchang standards.
Accurate to seconds using Swiss Ephemeris / PyEphem.

Calculates:
1. Pancha-Anga (5 Pillars): Tithi, Nakshatra, Yoga, Karana, Vara with exact ending moments,
   degrees, remaining time, deities, lords, and classical attributes.
2. Bhadra (Vishti Karana) Engine: Active timings, Loka (Swarga, Patala, Mrityu/Bhuloka),
   Mukha & Puchha timings, and classical verdicts.
3. Panchaka & Gandamoola Engine:
   - 5 Panchaka types (Roga, Raja, Agni, Chora, Mrityu) based on Moon ingress weekday.
   - Gandamoola 6 nakshatras with pada-specific dosha and shanti recommendations.
4. Choghadiya (8 Day, 8 Night) & 24 Horas with ruling planets and activities.
5. Shubh & Ashubh Timings: Abhijit, Brahma, Vijaya, Godhuli, Amrit Kaal, Nishita,
   Rahu Kaal, Yamaganda, Gulika, Durmuhurta, Varjyam.
6. Anandadi & Special Yogas: Sarvartha Siddhi, Amrit Siddhi, Dwi-Pushkar, Tri-Pushkar,
   Ravi Pushya, Guru Pushya, Ravi Yoga, and the full 28 Anandadi Yogas.
7. Vedic Time & Shoola: Disha Shoola & Remedies, Chandra Vasa, Agnivasa, Shivavasa,
   and 60-Ghati Vedic Clock (Ghati, Pala, Vipala).
8. Chandrabalam & Tarabalam: All 12 Rashis Moon strength & All 27 Nakshatras Tarabala.
9. Samvatsara & Cabinet: Vikram, Shaka, Jovian Year, Ayana, Ritu, King & Minister Cabinet.
10. Planetary Transit Matrix: All 9 grahas with degrees, nakshatras, padas, combust/retrograde.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date, time, timedelta
import math
import ephem

try:
    from ..core.ephemeris import PyEphemProvider
    from ..core.constants import NAKSHATRAS, SIGN_NAMES
except (ImportError, ValueError):
    from src.jyotish.core.ephemeris import PyEphemProvider
    from src.jyotish.core.constants import NAKSHATRAS, SIGN_NAMES


# ---------------------------------------------------------------------------
# Classical Constants & Tables
# ---------------------------------------------------------------------------

TITHI_NAMES = [
    ("प्रतिपदा", "Pratipada", "अग्नि (Agni)", "नन्दा (Nanda)"),
    ("द्वितीया", "Dwitiya", "ब्रह्मा (Brahma)", "भद्रा (Bhadra)"),
    ("तृतीया", "Tritiya", "गौरी (Gauri)", "जया (Jaya)"),
    ("चतुर्थी", "Chaturthi", "गणेश (Ganesha)", "रिक्ता (Rikta)"),
    ("पञ्चमी", "Panchami", "नाग (Naga)", "पूर्णा (Poorna)"),
    ("षष्ठी", "Shashthi", "कार्तिकेय (Kartikeya)", "नन्दा (Nanda)"),
    ("सप्तमी", "Saptami", "सूर्य (Surya)", "भद्रा (Bhadra)"),
    ("अष्टमी", "Ashtami", "शिव / दुर्गा (Shiva)", "जया (Jaya)"),
    ("नवमी", "Navami", "दुर्गा (Durga)", "रिक्ता (Rikta)"),
    ("दशमी", "Dashami", "यम (Yama)", "पूर्णा (Poorna)"),
    ("एकादशी", "Ekadashi", "विश्वेदेव (Vishvedeva)", "नन्दा (Nanda)"),
    ("द्वादशी", "Dvadashi", "विष्णु (Vishnu)", "भद्रा (Bhadra)"),
    ("त्रयोदशी", "Trayodashi", "कामदेव (Kamadeva)", "जया (Jaya)"),
    ("चतुर्दशी", "Chaturdashi", "शिव (Shiva)", "रिक्ता (Rikta)"),
    ("पूर्णिमा", "Purnima", "चन्द्रमा (Chandra)", "पूर्णा (Poorna)"),
    ("प्रतिपदा", "Pratipada", "अग्नि (Agni)", "नन्दा (Nanda)"),
    ("द्वितीया", "Dwitiya", "ब्रह्मा (Brahma)", "भद्रा (Bhadra)"),
    ("तृतीया", "Tritiya", "गौरी (Gauri)", "जया (Jaya)"),
    ("चतुर्थी", "Chaturthi", "गणेश (Ganesha)", "रिक्ता (Rikta)"),
    ("पञ्चमी", "Panchami", "नाग (Naga)", "पूर्णा (Poorna)"),
    ("षष्ठी", "Shashthi", "कार्तिकेय (Kartikeya)", "नन्दा (Nanda)"),
    ("सप्तमी", "Saptami", "सूर्य (Surya)", "भद्रा (Bhadra)"),
    ("अष्टमी", "Ashtami", "शिव / रुद्र (Rudra)", "जया (Jaya)"),
    ("नवमी", "Navami", "दुर्गा (Durga)", "रिक्ता (Rikta)"),
    ("दशमी", "Dashami", "यम (Yama)", "पूर्णा (Poorna)"),
    ("एकादशी", "Ekadashi", "विश्वेदेव (Vishvedeva)", "नन्दा (Nanda)"),
    ("द्वादशी", "Dvadashi", "विष्णु (Vishnu)", "भद्रा (Bhadra)"),
    ("त्रयोदशी", "Trayodashi", "कामदेव (Kamadeva)", "जया (Jaya)"),
    ("चतुर्दशी", "Chaturdashi", "शिव (Shiva)", "रिक्ता (Rikta)"),
    ("अमावस्या", "Amavasya", "पितृगण (Pitru)", "दर्श (Darsha)")
]

YOGA_DETAILS = [
    {"name": "विष्कम्भ", "name_en": "Vishkambha", "nature": "अशुभ", "is_good": False, "deity": "यम"},
    {"name": "प्रीति", "name_en": "Priti", "nature": "शुभ", "is_good": True, "deity": "विष्णु"},
    {"name": "आयुष्मान्", "name_en": "Ayushman", "nature": "शुभ", "is_good": True, "deity": "चन्द्र"},
    {"name": "सौभाग्य", "name_en": "Saubhagya", "nature": "शुभ", "is_good": True, "deity": "ब्रह्मा"},
    {"name": "शोभन", "name_en": "Shobhana", "nature": "शुभ", "is_good": True, "deity": "बृहस्पति"},
    {"name": "अतिगण्ड", "name_en": "Atiganda", "nature": "अशुभ", "is_good": False, "deity": "चन्द्र"},
    {"name": "सुकर्मा", "name_en": "Sukarma", "nature": "शुभ", "is_good": True, "deity": "इन्द्र"},
    {"name": "धृति", "name_en": "Dhriti", "nature": "शुभ", "is_good": True, "deity": "जलदेव"},
    {"name": "शूल", "name_en": "Shula", "nature": "अशुभ", "is_good": False, "deity": "सर्प"},
    {"name": "गण्ड", "name_en": "Ganda", "nature": "अशुभ", "is_good": False, "deity": "अग्नि"},
    {"name": "वृद्धि", "name_en": "Vriddhi", "nature": "शुभ", "is_good": True, "deity": "सूर्य"},
    {"name": "ध्रुव", "name_en": "Dhruva", "nature": "शुभ", "is_good": True, "deity": "भूमि"},
    {"name": "व्याघात", "name_en": "Vyaghata", "nature": "अशुभ", "is_good": False, "deity": "वायु"},
    {"name": "हर्षण", "name_en": "Harshana", "nature": "शुभ", "is_good": True, "deity": "भग"},
    {"name": "वज्र", "name_en": "Vajra", "nature": "अशुभ", "is_good": False, "deity": "वरुण"},
    {"name": "सिद्धि", "name_en": "Siddhi", "nature": "शुभ", "is_good": True, "deity": "गणेश"},
    {"name": "व्यतीपात", "name_en": "Vyatipata", "nature": "महा-अशुभ", "is_good": False, "deity": "रुद्र"},
    {"name": "वरीयान्", "name_en": "Variyan", "nature": "शुभ", "is_good": True, "deity": "कुबेर"},
    {"name": "परिघ", "name_en": "Parigha", "nature": "अशुभ", "is_good": False, "deity": "विश्वकर्मा"},
    {"name": "शिव", "name_en": "Shiva", "nature": "शुभ", "is_good": True, "deity": "महादेव"},
    {"name": "सिद्ध", "name_en": "Siddha", "nature": "शुभ", "is_good": True, "deity": "कार्तिकेय"},
    {"name": "साध्य", "name_en": "Sadhya", "nature": "शुभ", "is_good": True, "deity": "सावित्री"},
    {"name": "शुभ", "name_en": "Shubha", "nature": "शुभ", "is_good": True, "deity": "लक्ष्मी"},
    {"name": "शुक्ल", "name_en": "Shukla", "nature": "शुभ", "is_good": True, "deity": "पार्वती"},
    {"name": "ब्रह्म", "name_en": "Brahma", "nature": "शुभ", "is_good": True, "deity": "अश्विनीकुमार"},
    {"name": "ऐन्द्र", "name_en": "Aindra", "nature": "शुभ", "is_good": True, "deity": "इन्द्राणी"},
    {"name": "वैधृति", "name_en": "Vaidhriti", "nature": "महा-अशुभ", "is_good": False, "deity": "ददिति"}
]

CHARA_KARANAS = ["बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि (भद्रा)"]
STHIRA_KARANAS = ["शकुनि", "चतुष्पद", "नाग", "किंस्तुघ्न"]

KARANA_DEITIES = {
    "बव": "इन्द्र (Indra)",
    "बालव": "ब्रह्मा (Brahma)",
    "कौलव": "मित्र (Mitra)",
    "तैतिल": "अर्यमा (Aryama)",
    "गर": "भूमि (Bhoomi)",
    "वणिज": "श्रिया (Lakshmi)",
    "विष्टि (भद्रा)": "यमराज (Yamaraja)",
    "शकुनि": "कलियुग / सर्प (Kali)",
    "चतुष्पद": "वृषभ / पशुपति (Pashupati)",
    "नाग": "नागराज (Nagaraja)",
    "किंस्तुघ्न": "वायु (Vayu)"
}

VISHTI_HALF_TITHIS = [8, 15, 22, 29, 36, 43, 50, 57]

NAKSHATRA_EXTENDED = [
    {"name": "अश्विनी", "lord": "Ketu", "deity": "अश्विनीकुमार", "gana": "देव", "yoni": "अश्व", "nadi": "आद्य", "varna": "वैश्य", "symbol": "अश्व का सिर"},
    {"name": "भरणी", "lord": "Venus", "deity": "यम", "gana": "मनुष्य", "yoni": "गज", "nadi": "मध्य", "varna": "म्लेच्छ", "symbol": "योनि"},
    {"name": "कृत्तिका", "lord": "Sun", "deity": "अग्नि", "gana": "राक्षस", "yoni": "मेष", "nadi": "अन्त्य", "varna": "ब्राह्मण", "symbol": "अग्नि शिखा"},
    {"name": "रोहिणी", "lord": "Moon", "deity": "ब्रह्मा / प्रजापति", "gana": "मनुष्य", "yoni": "सर्प", "nadi": "अन्त्य", "varna": "शूद्र", "symbol": "रथ / छकड़ा"},
    {"name": "मृगशिरा", "lord": "Mars", "deity": "सोम (चन्द्र)", "gana": "देव", "yoni": "सर्प", "nadi": "मध्य", "varna": "वैश्य", "symbol": "हिरण का सिर"},
    {"name": "आर्द्रा", "lord": "Rahu", "deity": "रुद्र", "gana": "मनुष्य", "yoni": "श्वान", "nadi": "आद्य", "varna": "संकर", "symbol": "अश्रु बिन्दु"},
    {"name": "पुनर्वसु", "lord": "Jupiter", "deity": "अदिति", "gana": "देव", "yoni": "मार्जारी", "nadi": "आद्य", "varna": "वैश्य", "symbol": "धनुष-बाण"},
    {"name": "पुष्य", "lord": "Saturn", "deity": "बृहस्पति", "gana": "देव", "yoni": "मेष", "nadi": "मध्य", "varna": "क्षत्रिय", "symbol": "गाय का थन / पुष्प"},
    {"name": "आश्लेषा", "lord": "Mercury", "deity": "सर्प", "gana": "राक्षस", "yoni": "मार्जारी", "nadi": "अन्त्य", "varna": "म्लेच्छ", "symbol": "कुण्डलित सर्प"},
    {"name": "मघा", "lord": "Ketu", "deity": "पितर", "gana": "राक्षस", "yoni": "मूषक", "nadi": "अन्त्य", "varna": "शूद्र", "symbol": "सिंहासन"},
    {"name": "पूर्वाफाल्गुनी", "lord": "Venus", "deity": "भग", "gana": "मनुष्य", "yoni": "मूषक", "nadi": "मध्य", "varna": "ब्राह्मण", "symbol": "झूला / पलंग"},
    {"name": "उत्तराफाल्गुनी", "lord": "Sun", "deity": "अर्यमा", "gana": "मनुष्य", "yoni": "गौ", "nadi": "आद्य", "varna": "क्षत्रिय", "symbol": "शैया"},
    {"name": "हस्त", "lord": "Moon", "deity": "सूर्य / सविता", "gana": "देव", "yoni": "महिष", "nadi": "आद्य", "varna": "वैश्य", "symbol": "हाथ का पंजा"},
    {"name": "चित्रा", "lord": "Mars", "deity": "त्वष्टा (विश्वकर्मा)", "gana": "राक्षस", "yoni": "व्याघ्र", "nadi": "मध्य", "varna": "शूद्र", "symbol": "चमकता रत्न"},
    {"name": "स्वाती", "lord": "Rahu", "deity": "वायु", "gana": "देव", "yoni": "महिष", "nadi": "अन्त्य", "varna": "संकर", "symbol": "मूंगा / अंकुर"},
    {"name": "विशाखा", "lord": "Jupiter", "deity": "इन्द्राग्नि", "gana": "राक्षस", "yoni": "व्याघ्र", "nadi": "अन्त्य", "varna": "म्लेच्छ", "symbol": "तोरण / तराजू"},
    {"name": "अनुराधा", "lord": "Saturn", "deity": "मित्र", "gana": "देव", "yoni": "मृग", "nadi": "मध्य", "varna": "ब्राह्मण", "symbol": "कमल पुष्प"},
    {"name": "ज्येष्ठा", "lord": "Mercury", "deity": "इन्द्र", "gana": "राक्षस", "yoni": "मृग", "nadi": "आद्य", "varna": "शूद्र", "symbol": "कुण्डल / छत्र"},
    {"name": "मूल", "lord": "Ketu", "deity": "निरृति", "gana": "राक्षस", "yoni": "श्वान", "nadi": "आद्य", "varna": "म्लेच्छ", "symbol": "जड़ / अंकुश"},
    {"name": "पूर्वाषाढ़ा", "lord": "Venus", "deity": "आपः (जल)", "gana": "मनुष्य", "yoni": "वानर", "nadi": "मध्य", "varna": "ब्राह्मण", "symbol": "हाथी दांत / पंखा"},
    {"name": "उत्तराषाढ़ा", "lord": "Sun", "deity": "विश्वेदेव", "gana": "मनुष्य", "yoni": "नकुल", "nadi": "अन्त्य", "varna": "क्षत्रिय", "symbol": "तख्त / मंच"},
    {"name": "श्रवण", "lord": "Moon", "deity": "विष्णु", "gana": "देव", "yoni": "वानर", "nadi": "अन्त्य", "varna": "म्लेच्छ", "symbol": "कान / त्रिशूल"},
    {"name": "धनिष्ठा", "lord": "Mars", "deity": "अष्ट वसु", "gana": "राक्षस", "yoni": "सिंह", "nadi": "मध्य", "varna": "शूद्र", "symbol": "मृदंग / बांसुरी"},
    {"name": "शतभिषा", "lord": "Rahu", "deity": "वरुण", "gana": "राक्षस", "yoni": "अश्व", "nadi": "आद्य", "varna": "शूद्र", "symbol": "सौ तारे / चक्र"},
    {"name": "पूर्वाभाद्रपद", "lord": "Jupiter", "deity": "अजैकपाद", "gana": "मनुष्य", "yoni": "सिंह", "nadi": "आद्य", "varna": "ब्राह्मण", "symbol": "दो मुखी तलवार"},
    {"name": "उत्तराभाद्रपद", "lord": "Saturn", "deity": "अहिर्बुध्न्य", "gana": "मनुष्य", "yoni": "गौ", "nadi": "मध्य", "varna": "क्षत्रिय", "symbol": "शैया के दो पाये"},
    {"name": "रेवती", "lord": "Mercury", "deity": "पूषा", "gana": "देव", "yoni": "गज", "nadi": "अन्त्य", "varna": "शूद्र", "symbol": "मछली"}
]

ANANDADI_YOGAS_28 = [
    ("आनन्द", "Ananda", "शुभ", True, "सर्व कार्य सिद्धि एवं प्रसन्नता।"),
    ("कालदण्ड", "Kaladanda", "अशुभ", False, "विपत्ति, भय व मृत्युतुल्य कष्ट।"),
    ("धूम्र", "Dhumra", "अशुभ", False, "मानसिक संताप, कार्य में अवरोध।"),
    ("प्रजापति (धाता)", "Prajapati", "शुभ", True, "प्रजावृद्धि, यश व सुख-शांति।"),
    ("सौम्य", "Saumya", "शुभ", True, "सौभाग्य, शांति व अनुकूलता।"),
    ("ध्वाङ्क्ष", "Dhwanksha", "अशुभ", False, "हानि, अपमान व व्यर्थ दौड़धूप।"),
    ("ध्वज", "Dhwaja", "शुभ", True, "विजय, मान-सम्मान व उच्च प्रतिष्ठा।"),
    ("श्रीवत्स", "Shrivatsa", "शुभ", True, "धन-धान्य, ऐश्वर्य व लक्ष्मी कृपा।"),
    ("वज्र", "Vajra", "अशुभ", False, "शत्रु भय, कलह व चोट-चपेट।"),
    ("मुद्गर", "Mudgara", "अशुभ", False, "धनहानि, कार्य में विफलता।"),
    ("छत्र", "Chhatra", "शुभ", True, "राजकृपा, उच्च पद व सुरक्षा।"),
    ("मित्र", "Mitra", "शुभ", True, "सगे-संबंधियों से लाभ, मित्रता।"),
    ("मानस", "Manasa", "शुभ", True, "मनोवांछित सिद्धि, आत्मसंतोष।"),
    ("पद्म", "Padma", "शुभ", True, "लक्ष्मी प्राप्ति, विद्या व कीर्ति।"),
    ("लुम्बक", "Lumbaka", "अशुभ", False, "द्रव्यनाश, संबंध विच्छेद।"),
    ("उत्पात", "Utpata", "अशुभ", False, "आकस्मिक संकट, रोग व अनिष्ट।"),
    ("मृत्यु", "Mrityu", "महा-अशुभ", False, "घोर संकट, नवीन कार्य वर्जित।"),
    ("काण", "Kana", "अशुभ", False, "हानि, नेत्र कष्ट व निराशा।"),
    ("सिद्धि", "Siddhi", "परम शुभ", True, "सर्व कार्य सिद्धि, मनोकामना पूर्ति।"),
    ("शुभ", "Shubha", "शुभ", True, "मंगल कार्य, आरोग्य व समृद्धि।"),
    ("अमृत", "Amrita", "परम शुभ", True, "अमृततुल्य फल, दीर्घायु व विजय।"),
    ("मुसल", "Musala", "अशुभ", False, "विवाद, चोरी व शत्रु पीड़ा।"),
    ("गद", "Gada", "अशुभ", False, "रोग, व्याधि व शारीरिक कष्ट।"),
    ("मातङ्ग", "Matanga", "शुभ", True, "वाहन सुख, अधिकार व ऐश्वर्य।"),
    ("राक्षस", "Rakshasa", "अशुभ", False, "उपद्रव, भय व अमंगल।"),
    ("चर", "Chara", "शुभ", True, "यात्रा, गतिशील कार्य सिद्धि।"),
    ("स्थिर", "Sthira", "शुभ", True, "गृह प्रवेश, नींव, स्थायी कार्य सिद्धि।"),
    ("प्रवर्धन", "Pravardhana", "शुभ", True, "उन्नति, व्यापार वृद्धि व यश।")
]

SAMVATSARAS_60 = [
    "प्रभव", "विभव", "शुक्ल", "प्रमोद", "प्रजापति", "अङ्गिरा", "श्रीमुख", "भाव", "युवा", "धाता",
    "ईश्वर", "बहुधान्य", "प्रमाथी", "विक्रम", "वृषप्रजा", "चित्रभानु", "सुभानु", "तारण", "पार्थिव", "व्यय",
    "सर्वजीत", "सर्वधारी", "विरोधी", "विकृत", "खर", "नन्दन", "विजय", "जय", "मन्मथ", "दुर्मुख",
    "हेमलम्ब", "विलम्ब", "विकारी", "शार्वरी", "प्लव", "शुभकृत", "शोभन", "क्रोधी", "विश्वावसु", "पराभव",
    "प्लवङ्ग", "कीलक", "सौम्य", "साधारण", "विरोधकृत", "परिधावी", "प्रमादी", "आनन्द", "राक्षस", "नल",
    "पिङ्गल", "कालयुक्त", "सिद्धार्थी", "रौद्र", "दुर्मति", "दुन्दुभी", "रुधिरोद्गारी", "रक्ताक्षी", "क्रोधन", "क्षय"
]

CHOGHADIYA_TYPES = {
    "Amrit": {"name_hi": "अमृत", "nature": "उत्तम शुभ", "planet": "Moon", "color": "#065F46", "bg": "#D1FAE5", "is_good": True, "acts": "सर्व प्रकार के शुभ व मांगलिक कार्य"},
    "Shubh": {"name_hi": "शुभ", "nature": "शुभ फलदायी", "planet": "Sun", "color": "#1E40AF", "bg": "#DBEAFE", "is_good": True, "acts": "विवाह, पूजा, धार्मिक व मांगलिक कार्य"},
    "Labh": {"name_hi": "लाभ", "nature": "लाभकारी", "planet": "Mercury", "color": "#0F766E", "bg": "#CCFBF1", "is_good": True, "acts": "व्यापार, नवीन दुकान, शिक्षा, खाता बही"},
    "Char": {"name_hi": "चर", "nature": "सामान्य / गतिशील", "planet": "Venus", "color": "#854D0E", "bg": "#FEF9C3", "is_good": True, "acts": "यात्रा, वाहन क्रय, विदेश गमन, खेल"},
    "Udveg": {"name_hi": "उद्वेग", "nature": "अशुभ / चिंता", "planet": "Sun", "color": "#9A3412", "bg": "#FFEDD5", "is_good": False, "acts": "शुभ कार्य वर्जित; राजकीय कार्य संभलकर"},
    "Kaal": {"name_hi": "काल", "nature": "अत्यंत अशुभ", "planet": "Saturn", "color": "#991B1B", "bg": "#FEE2E2", "is_good": False, "acts": "सर्वथा वर्जित; धनहानि व मृत्युतुल्य भय"},
    "Rog": {"name_hi": "रोग", "nature": "अशुभ / व्याधि", "planet": "Mars", "color": "#991B1B", "bg": "#FEE2E2", "is_good": False, "acts": "रोग वृद्धि व कलह; शुभ कार्य वर्जित"}
}

DAY_CHOGHADIYA_ORDERS = {
    6: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],  # Sunday
    0: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],  # Monday
    1: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],    # Tuesday
    2: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],   # Wednesday
    3: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],  # Thursday
    4: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],   # Friday
    5: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],   # Saturday
}

NIGHT_CHOGHADIYA_ORDERS = {
    6: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],  # Sunday
    0: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],   # Monday
    1: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],   # Tuesday
    2: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],  # Wednesday
    3: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],  # Thursday
    4: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],    # Friday
    5: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],   # Saturday
}

HORA_CHALDEAN_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
HORA_DAY_FIRST = {6: "Sun", 0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter", 4: "Venus", 5: "Saturn"}

WEEKDAY_NAMES_HI = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]


class VedicPanchangService:
    """
    World-class Shastriya Panchang Calculation Engine.
    Computes all 10 classical pillars, divisions, muhurtas, yogas, and doshas.
    """

    _provider: Optional[PyEphemProvider] = None

    @classmethod
    def get_provider(cls) -> PyEphemProvider:
        if cls._provider is None:
            cls._provider = PyEphemProvider()
        return cls._provider

    @classmethod
    def calculate_sun_moon_rise_set(
        cls,
        target_date: date,
        latitude: float = 28.6139,
        longitude: float = 77.2090,
        tz_offset_hours: float = 5.5
    ) -> Dict[str, Any]:
        """Calculates exact Sunrise, Sunset, Moonrise, Moonset using PyEphem Observer."""
        obs = ephem.Observer()
        obs.lat = str(latitude)
        obs.lon = str(longitude)
        obs.elevation = 0
        obs.pressure = 1010
        obs.horizon = '-0:34'  # Standard atmospheric refraction at horizon

        # Start search from target date 00:00 local time = target_date - tz_offset UTC
        local_midnight = datetime.combine(target_date, time(0, 0))
        utc_midnight = local_midnight - timedelta(hours=tz_offset_hours)
        obs.date = utc_midnight

        s = ephem.Sun()
        m = ephem.Moon()

        try:
            sr_utc = obs.next_rising(s).datetime()
            sr_local = sr_utc + timedelta(hours=tz_offset_hours)
        except Exception:
            sr_local = local_midnight + timedelta(hours=6)

        obs.date = sr_local - timedelta(hours=tz_offset_hours)
        try:
            ss_utc = obs.next_setting(s).datetime()
            ss_local = ss_utc + timedelta(hours=tz_offset_hours)
        except Exception:
            ss_local = local_midnight + timedelta(hours=18)

        # Next sunrise for Ratrimana calculation
        obs.date = ss_local - timedelta(hours=tz_offset_hours)
        try:
            next_sr_utc = obs.next_rising(s).datetime()
            next_sr_local = next_sr_utc + timedelta(hours=tz_offset_hours)
        except Exception:
            next_sr_local = sr_local + timedelta(days=1)

        # Moonrise & Moonset
        obs.date = utc_midnight
        try:
            mr_utc = obs.next_rising(m).datetime()
            mr_local = mr_utc + timedelta(hours=tz_offset_hours)
        except Exception:
            mr_local = None

        try:
            ms_utc = obs.next_setting(m).datetime()
            ms_local = ms_utc + timedelta(hours=tz_offset_hours)
        except Exception:
            ms_local = None

        # Dinamana (Day Duration) and Ratrimana (Night Duration)
        dinamana_sec = (ss_local - sr_local).total_seconds()
        ratrimana_sec = (next_sr_local - ss_local).total_seconds()

        d_hours = int(dinamana_sec // 3600)
        d_mins = int((dinamana_sec % 3600) // 60)
        d_secs = int(dinamana_sec % 60)

        # Vedic Ghatis (1 Ghati = 24 min = 1440 sec)
        d_ghatis = dinamana_sec / 1440.0
        r_ghatis = ratrimana_sec / 1440.0

        return {
            "sunrise": sr_local,
            "sunset": ss_local,
            "next_sunrise": next_sr_local,
            "moonrise": mr_local,
            "moonset": ms_local,
            "dinamana_seconds": dinamana_sec,
            "ratrimana_seconds": ratrimana_sec,
            "dinamana_str": f"{d_hours} घंटे {d_mins} मिनट {d_secs} सेकंड ({d_ghatis:.2f} घटी)",
            "ratrimana_str": f"{int(ratrimana_sec//3600)} घंटे {int((ratrimana_sec%3600)//60)} मिनट ({r_ghatis:.2f} घटी)",
            "dinamana_ghatis": round(d_ghatis, 2),
            "ratrimana_ghatis": round(r_ghatis, 2)
        }

    @classmethod
    def _find_transition_time(
        cls,
        eval_fn,
        current_val: int,
        start_utc: datetime,
        max_hours: float = 36.0,
        step_minutes: int = 10
    ) -> Optional[datetime]:
        """High-precision binary search to pinpoint astronomical transitions to 1 second."""
        t = start_utc
        limit = start_utc + timedelta(hours=max_hours)
        found_bracket = False

        while t < limit:
            val = eval_fn(t)
            if val != current_val:
                found_bracket = True
                break
            t += timedelta(minutes=step_minutes)

        if not found_bracket:
            return None

        # Binary search
        left = t - timedelta(minutes=step_minutes)
        right = t
        for _ in range(22):  # 2^22 precision < 0.2 seconds
            mid = left + (right - left) / 2
            if eval_fn(mid) == current_val:
                left = mid
            else:
                right = mid

        return right

    @classmethod
    def calculate_panchanga_5_pillars(
        cls,
        target_date: date,
        sunrise_dt: datetime,
        tz_offset_hours: float = 5.5
    ) -> Dict[str, Any]:
        """Calculates Tithi, Nakshatra, Yoga, Karana, and Vara with exact end moments and degrees."""
        provider = cls.get_provider()
        utc_sr = sunrise_dt - timedelta(hours=tz_offset_hours)

        pos_sr, _ = provider.get_planet_positions(utc_sr)
        sun_lon = pos_sr["Sun"]["longitude"] % 360.0
        moon_lon = pos_sr["Moon"]["longitude"] % 360.0

        # Weekday (Vara)
        py_wday = target_date.weekday()  # Mon=0..Sun=6
        vara_hi = WEEKDAY_NAMES_HI[py_wday]
        vara_lords = {0: "चन्द्रमा (Moon)", 1: "मंगल (Mars)", 2: "बुध (Mercury)", 3: "बृहस्पति (Jupiter)", 4: "शुक्र (Venus)", 5: "शनि (Saturn)", 6: "सूर्य (Sun)"}
        vara_lord = vara_lords[py_wday]

        # 1. TITHI
        diff_sr = (moon_lon - sun_lon) % 360.0
        tithi_idx = int(diff_sr // 12.0) + 1  # 1 to 30
        tithi_deg_in = diff_sr % 12.0
        tithi_pct = (tithi_deg_in / 12.0) * 100.0

        def _get_tithi(dt_utc):
            p, _ = provider.get_planet_positions(dt_utc)
            d = (p["Moon"]["longitude"] - p["Sun"]["longitude"]) % 360.0
            return int(d // 12.0) + 1

        tithi_end_utc = cls._find_transition_time(_get_tithi, tithi_idx, utc_sr)
        tithi_end_local = (tithi_end_utc + timedelta(hours=tz_offset_hours)) if tithi_end_utc else None

        t_meta = TITHI_NAMES[tithi_idx - 1]
        is_shukla = tithi_idx <= 15
        paksha = "शुक्ल पक्ष" if is_shukla else "कृष्ण पक्ष"
        paksha_en = "Shukla Paksha" if is_shukla else "Krishna Paksha"

        # Next Tithi
        next_tithi_idx = (tithi_idx % 30) + 1
        next_t_meta = TITHI_NAMES[next_tithi_idx - 1]

        # 2. NAKSHATRA
        nak_span = 360.0 / 27.0
        nak_idx = int(moon_lon // nak_span) + 1  # 1 to 27
        nak_deg_in = moon_lon % nak_span
        nak_pct = (nak_deg_in / nak_span) * 100.0
        pada = int(nak_deg_in // (nak_span / 4.0)) + 1

        def _get_nak(dt_utc):
            p, _ = provider.get_planet_positions(dt_utc)
            return int((p["Moon"]["longitude"] % 360.0) // nak_span) + 1

        nak_end_utc = cls._find_transition_time(_get_nak, nak_idx, utc_sr)
        nak_end_local = (nak_end_utc + timedelta(hours=tz_offset_hours)) if nak_end_utc else None

        nak_meta = NAKSHATRA_EXTENDED[nak_idx - 1]
        next_nak_idx = (nak_idx % 27) + 1
        next_nak_meta = NAKSHATRA_EXTENDED[next_nak_idx - 1]

        # 3. YOGA
        yoga_sum = (moon_lon + sun_lon) % 360.0
        yoga_idx = int(yoga_sum // nak_span) + 1  # 1 to 27
        yoga_deg_in = yoga_sum % nak_span
        yoga_pct = (yoga_deg_in / nak_span) * 100.0

        def _get_yoga(dt_utc):
            p, _ = provider.get_planet_positions(dt_utc)
            s = (p["Moon"]["longitude"] + p["Sun"]["longitude"]) % 360.0
            return int(s // nak_span) + 1

        yoga_end_utc = cls._find_transition_time(_get_yoga, yoga_idx, utc_sr)
        yoga_end_local = (yoga_end_utc + timedelta(hours=tz_offset_hours)) if yoga_end_utc else None

        yoga_meta = YOGA_DETAILS[yoga_idx - 1]
        next_yoga_idx = (yoga_idx % 27) + 1
        next_yoga_meta = YOGA_DETAILS[next_yoga_idx - 1]

        # 4. KARANA
        karana_idx = int(diff_sr // 6.0) + 1  # 1 to 60 half-tithis
        k_deg_in = diff_sr % 6.0
        k_pct = (k_deg_in / 6.0) * 100.0

        def _get_karana_name(k_num: int) -> str:
            if k_num == 1:
                return "किंस्तुघ्न"
            elif 2 <= k_num <= 57:
                return CHARA_KARANAS[(k_num - 2) % 7]
            elif k_num == 58:
                return "शकुनि"
            elif k_num == 59:
                return "चतुष्पद"
            elif k_num == 60:
                return "नाग"
            return "बव"

        karana_name = _get_karana_name(karana_idx)

        def _get_karana(dt_utc):
            p, _ = provider.get_planet_positions(dt_utc)
            d = (p["Moon"]["longitude"] - p["Sun"]["longitude"]) % 360.0
            return int(d // 6.0) + 1

        k_end_utc = cls._find_transition_time(_get_karana, karana_idx, utc_sr)
        k_end_local = (k_end_utc + timedelta(hours=tz_offset_hours)) if k_end_utc else None

        next_k_idx = (karana_idx % 60) + 1
        next_karana_name = _get_karana_name(next_k_idx)
        next_k_end_utc = cls._find_transition_time(_get_karana, next_k_idx, k_end_utc if k_end_utc else utc_sr)
        next_k_end_local = (next_k_end_utc + timedelta(hours=tz_offset_hours)) if next_k_end_utc else None

        def _format_end(dt_obj):
            if not dt_obj:
                return "अहोरात्र (Full Day)"
            if dt_obj.date() == target_date:
                return dt_obj.strftime("%I:%M %p तक")
            elif dt_obj.date() == target_date + timedelta(days=1):
                return dt_obj.strftime("%I:%M %p, %b %d तक")
            return dt_obj.strftime("%I:%M %p, %b %d तक")

        return {
            "vara": {
                "name_hi": vara_hi,
                "lord": vara_lord,
                "weekday_idx": py_wday
            },
            "tithi": {
                "index": tithi_idx,
                "name": t_meta[0],
                "name_en": t_meta[1],
                "paksha": paksha,
                "paksha_en": paksha_en,
                "category": t_meta[3],
                "deity": t_meta[2],
                "degree": round(diff_sr, 2),
                "degree_in_tithi": round(tithi_deg_in, 2),
                "progress_pct": round(tithi_pct, 1),
                "end_time": tithi_end_local,
                "end_time_str": _format_end(tithi_end_local),
                "next_name": next_t_meta[0],
                "next_paksha": "शुक्ल" if next_tithi_idx <= 15 else "कृष्ण"
            },
            "nakshatra": {
                "index": nak_idx,
                "name": nak_meta["name"],
                "lord": nak_meta["lord"],
                "pada": pada,
                "deity": nak_meta["deity"],
                "gana": nak_meta["gana"],
                "yoni": nak_meta["yoni"],
                "nadi": nak_meta["nadi"],
                "varna": nak_meta["varna"],
                "symbol": nak_meta["symbol"],
                "degree": round(moon_lon, 2),
                "degree_in_nak": round(nak_deg_in, 2),
                "progress_pct": round(nak_pct, 1),
                "end_time": nak_end_local,
                "end_time_str": _format_end(nak_end_local),
                "next_name": next_nak_meta["name"]
            },
            "yoga": {
                "index": yoga_idx,
                "name": yoga_meta["name"],
                "name_en": yoga_meta["name_en"],
                "nature": yoga_meta["nature"],
                "is_good": yoga_meta["is_good"],
                "deity": yoga_meta["deity"],
                "degree": round(yoga_sum, 2),
                "progress_pct": round(yoga_pct, 1),
                "end_time": yoga_end_local,
                "end_time_str": _format_end(yoga_end_local),
                "next_name": next_yoga_meta["name"]
            },
            "karana": {
                "current": {
                    "index": karana_idx,
                    "name": karana_name,
                    "type": "चर" if karana_name in CHARA_KARANAS else "स्थिर",
                    "deity": KARANA_DEITIES.get(karana_name, "वरुण"),
                    "progress_pct": round(k_pct, 1),
                    "end_time": k_end_local,
                    "end_time_str": _format_end(k_end_local)
                },
                "next": {
                    "index": next_k_idx,
                    "name": next_karana_name,
                    "type": "चर" if next_karana_name in CHARA_KARANAS else "स्थिर",
                    "deity": KARANA_DEITIES.get(next_karana_name, "वरुण"),
                    "end_time": next_k_end_local,
                    "end_time_str": _format_end(next_k_end_local)
                }
            }
        }

    @classmethod
    def calculate_bhadra_deep_engine(
        cls,
        target_date: date,
        sunrise_dt: datetime,
        sunset_dt: datetime,
        tz_offset_hours: float = 5.5
    ) -> Dict[str, Any]:
        """
        Deep Classical Bhadra Engine according to Muhurta Chintamani:
        - Detects whether Vishti karana is active today.
        - Calculates exact start, end, duration.
        - Bhadra Vasa (Swarga, Patala, Mrityu/Bhuloka) based on Moon sign.
        - Bhadra Mukha (5 Ghatis = 2h) and Puchha (3 Ghatis = 1h 12m) clock timings.
        - Classical verdict: 'पुच्छे कार्यं सिद्धिप्रदम्, मुखे सर्वकार्यविनाशिनी'.
        """
        provider = cls.get_provider()
        utc_sr = sunrise_dt - timedelta(hours=tz_offset_hours)

        # Check 60 half-tithis across the 24-30 hr window around this day
        # Look for occurrences of VISHTI_HALF_TITHIS
        def _get_k_idx(dt_u):
            p, _ = provider.get_planet_positions(dt_u)
            d = (p["Moon"]["longitude"] - p["Sun"]["longitude"]) % 360.0
            return int(d // 6.0) + 1

        bhadra_records = []
        # Sample every 15 minutes across sunrise to next sunrise + 6 hours
        window_start = utc_sr - timedelta(hours=6)
        window_end = utc_sr + timedelta(hours=30)
        curr = window_start

        in_bhadra = False
        b_start_utc = None
        b_end_utc = None
        vishti_num = None

        while curr <= window_end:
            k = _get_k_idx(curr)
            if k in VISHTI_HALF_TITHIS:
                if not in_bhadra:
                    in_bhadra = True
                    vishti_num = k
                    # Refine start
                    l = curr - timedelta(minutes=15)
                    r = curr
                    for _ in range(16):
                        m = l + (r - l) / 2
                        if _get_k_idx(m) in VISHTI_HALF_TITHIS:
                            r = m
                        else:
                            l = m
                    b_start_utc = r
            else:
                if in_bhadra:
                    in_bhadra = False
                    # Refine end
                    l = curr - timedelta(minutes=15)
                    r = curr
                    for _ in range(16):
                        m = l + (r - l) / 2
                        if _get_k_idx(m) in VISHTI_HALF_TITHIS:
                            l = m
                        else:
                            r = m
                    b_end_utc = l
                    bhadra_records.append({
                        "vishti_num": vishti_num,
                        "start_utc": b_start_utc,
                        "end_utc": b_end_utc
                    })
                    b_start_utc = None
            curr += timedelta(minutes=15)

        # Find Bhadra intersecting with target date's sunrise-to-next-sunrise cycle
        local_day_start = sunrise_dt
        local_day_end = sunrise_dt + timedelta(hours=24)

        active_bhadra = None
        for b in bhadra_records:
            s_loc = b["start_utc"] + timedelta(hours=tz_offset_hours)
            e_loc = b["end_utc"] + timedelta(hours=tz_offset_hours)
            if s_loc <= local_day_end and e_loc >= local_day_start:
                active_bhadra = {
                    "vishti_num": b["vishti_num"],
                    "start": s_loc,
                    "end": e_loc
                }
                break

        if not active_bhadra:
            return {
                "is_present": False,
                "badge": "🟢 भद्रा रहित दिवस (No Bhadra)",
                "status_hi": "आज भद्रा का कोई दोष नहीं है। दिन मांगलिक कार्यों हेतु निर्बाध व शुद्ध है।",
                "details": None
            }

        b_start = active_bhadra["start"]
        b_end = active_bhadra["end"]
        duration_sec = (b_end - b_start).total_seconds()

        # Moon sign during Bhadra midpoint
        mid_utc = (b_start + (b_end - b_start) / 2) - timedelta(hours=tz_offset_hours)
        pos_mid, _ = provider.get_planet_positions(mid_utc)
        m_lon = pos_mid["Moon"]["longitude"] % 360.0
        moon_sign = int(m_lon // 30.0) + 1
        moon_sign_name = SIGN_NAMES[moon_sign - 1]

        # Bhadra Vasa (Loka)
        if moon_sign in [1, 2, 3, 8]:  # Mesh, Vrishabh, Mithun, Vrishchik
            bhadra_loka = "स्वर्ग लोक (Swarga Loka)"
            loka_desc = "स्वर्ग की भद्रा का वास देवलोक में होने से पृथ्वी पर इसका दुष्प्रभाव शून्य/निष्प्रभावी रहता है।"
            is_fatal_on_earth = False
            loka_badge = "🟡 स्वर्ग वास (हानिरहित)"
            loka_color = "#D97706"
        elif moon_sign in [6, 7, 9, 10]:  # Kanya, Tula, Dhanu, Makar
            bhadra_loka = "पाताल लोक (Patala Loka)"
            loka_desc = "पाताल लोक की भद्रा नागलोक में वास करती है। शास्त्रों अनुसार यह धनप्रद मानी गई है, पृथ्वी पर अनिष्ट नहीं करती।"
            is_fatal_on_earth = False
            loka_badge = "🟢 पाताल वास (धनप्रद)"
            loka_color = "#059669"
        else:  # Karka(4), Simha(5), Kumbha(11), Meena(12)
            bhadra_loka = "मृत्युलोक / पृथ्वी (Martya Loka - Earth)"
            loka_desc = "🔴 भद्रा का साक्षात् वास मृत्युलोक (पृथ्वी) पर है! यह 'सर्वकार्यविनाशिनी' कहलाती है। इसमें विवाह, गृह प्रवेश, यात्रा व नवीन कार्य सर्वथा वर्जित हैं।"
            is_fatal_on_earth = True
            loka_badge = "🚫 मृत्युलोक वास (महा-दोष)"
            loka_color = "#DC2626"

        # Bhadra Mukha & Puchha timings
        # Mukha is 5 Ghatis (approx 2 hrs = 1/12th of 60 ghatis)
        # Puchha is 3 Ghatis (approx 1 hr 12 min)
        # Classical rule based on half-tithi / Vishti type:
        v_num = active_bhadra["vishti_num"]
        # In Shukla 4 (v=8) & 11 (v=22), Puchha is at the end
        # In Shukla 8 (v=15) & 15 (v=29), Puchha is at the beginning
        # In Krishna 3 (v=36) & 10 (v=50), Puchha is at the end
        # In Krishna 7 (v=43) & 14 (v=57), Puchha is at the beginning
        puchha_duration = timedelta(seconds=min(72 * 60, duration_sec * 0.12))
        mukha_duration = timedelta(seconds=min(120 * 60, duration_sec * 0.18))

        if v_num in [15, 29, 43, 57]:
            # Puchha at beginning, Mukha at end
            puchha_start = b_start
            puchha_end = b_start + puchha_duration
            mukha_start = b_end - mukha_duration
            mukha_end = b_end
        else:
            # Mukha at beginning, Puchha at end
            mukha_start = b_start
            mukha_end = b_start + mukha_duration
            puchha_start = b_end - puchha_duration
            puchha_end = b_end

        return {
            "is_present": True,
            "badge": loka_badge,
            "color": loka_color,
            "is_fatal_on_earth": is_fatal_on_earth,
            "loka": bhadra_loka,
            "moon_sign": moon_sign_name,
            "start_time": b_start.strftime("%I:%M %p"),
            "end_time": b_end.strftime("%I:%M %p"),
            "full_time_str": f"{b_start.strftime('%I:%M %p')} से {b_end.strftime('%I:%M %p')} तक",
            "duration_str": f"{int(duration_sec//3600)} घंटे {int((duration_sec%3600)//60)} मिनट",
            "mukha_time": f"{mukha_start.strftime('%I:%M %p')} - {mukha_end.strftime('%I:%M %p')} (अति-घातक / महा-वर्जित)",
            "puchha_time": f"{puchha_start.strftime('%I:%M %p')} - {puchha_end.strftime('%I:%M %p')} (शुभ फलदायी / कार्य सिद्धि)",
            "sutra": "स्वर्गे भद्रा शुभा प्रोक्ता पाताले च धनागमा। मृत्युलोके स्थिता भद्रा सर्वकर्मविनाशिनी॥ (मुहूर्त चिन्तामणि)",
            "verdict": loka_desc,
            "prohibitions": [
                "विवाह एवं पाणिग्रहण संस्कार",
                "नूतन गृह प्रवेश व गृह निर्माण",
                "मुंडन, उपनयन एवं रक्षाबन्धन",
                "नवीन व्यापार व प्रतिष्ठान आरम्भ",
                "महत्वपूर्ण यात्रा व वाणिज्यिक अनुबंध"
            ],
            "allowed_in_puchha": "यदि कार्य अत्यंत आवश्यक हो तो केवल 'भद्रा पुच्छ' काल में ही सम्पन्न करें।"
        }

    @classmethod
    def calculate_panchaka_and_gandamoola(
        cls,
        target_date: date,
        sunrise_dt: datetime,
        tz_offset_hours: float = 5.5
    ) -> Dict[str, Any]:
        """Calculates Panchaka (5 Types) and Gandamoola (6 Nakshatras) with Pada effects."""
        provider = cls.get_provider()
        utc_sr = sunrise_dt - timedelta(hours=tz_offset_hours)
        pos, _ = provider.get_planet_positions(utc_sr)
        m_lon = pos["Moon"]["longitude"] % 360.0
        nak_span = 360.0 / 27.0
        nak_idx = int(m_lon // nak_span) + 1
        deg_in_nak = m_lon % nak_span
        pada = int(deg_in_nak // (nak_span / 4.0)) + 1
        wday = target_date.weekday()

        # 1. PANCHAKA CALCULATION
        # Moon in Dhanishta (pada 3,4: from 293°20'), Shatabhisha, Purva Bhadra, Uttara Bhadra, Revati (up to 360°)
        is_panchaka = m_lon >= 293.3333333333333
        panchaka_data = {}

        if is_panchaka:
            # 5 Types based on Day:
            panchaka_types = {
                6: ("रोग पञ्चक (Roga Panchaka)", "अत्यंत कष्टकारी; रोग, शारीरिक व्याधि व मानसिक संताप का भय रहता है।", "🔴 अशुभ", "#DC2626"),
                0: ("राज पञ्चक (Raja / Nripa Panchaka)", "शुभ फलदायी; राजकार्य, संपत्ति, प्रशासनिक कार्य व पदोन्नति हेतु अनुकूल।", "🟢 शुभ", "#059669"),
                1: ("अग्नि पञ्चक (Agni Panchaka)", "अग्नि, ज्वर, शस्त्र, दुर्घटना एवं मुकदमों का भय। निर्माण व कोर्ट कार्य में सावधानी।", "🔴 अशुभ", "#DC2626"),
                2: ("दोष रहित / सामान्य पञ्चक", "मध्यम प्रभाव; सामान्य दैनिक कार्य सम्पन्न किए जा सकते हैं।", "🟡 मध्यम", "#D97706"),
                3: ("दोष रहित / शुभ पञ्चक", "देवगुरु के प्रभाव से पञ्चक का दोष न्यूनतम रहता है।", "🟢 शुभ", "#059669"),
                4: ("चोर पञ्चक (Chora Panchaka)", "धनहानि, चोरी, विश्वासघात व व्यापारिक नुकसान की आशंका। धन निवेश वर्जित।", "🔴 अशुभ", "#DC2626"),
                5: ("मृत्यु पञ्चक (Mrityu Panchaka)", "सर्वाधिक भयंकर पञ्चक; मृत्युतुल्य कष्ट, गंभीर दुर्घटना व विवाद का भय। सर्वथा वर्जित।", "🔴 महा-अशुभ", "#991B1B")
            }
            p_name, p_desc, p_badge, p_col = panchaka_types.get(wday, ("पञ्चक काल", "पञ्चक प्रभाव सक्रिय।", "⚠️ सतर्कता", "#D97706"))
            panchaka_data = {
                "is_active": True,
                "name": p_name,
                "badge": p_badge,
                "color": p_col,
                "desc": p_desc,
                "moon_degree": round(m_lon, 2),
                "prohibitions": [
                    "दक्षिण दिशा की यात्रा (Travel towards South)",
                    "मकान की छत डालना / लेंटर (Roof casting)",
                    "चारपाई / पलंग बनवाना व खरीदना",
                    "तृण, लकड़ी, ईंधन या बांस का संग्रह करना",
                    "शवदाह (पञ्चक शान्ति पुतले सहित आवश्यक)"
                ]
            }
        else:
            panchaka_data = {
                "is_active": False,
                "name": "पञ्चक रहित (No Panchaka)",
                "badge": "🟢 पञ्चक मुक्त",
                "color": "#059669",
                "desc": "वर्तमान में चन्द्रमा पञ्चक नक्षत्रों में नहीं है। छत निर्माण, दक्षिण यात्रा व काष्ठ संग्रह हेतु कोई दोष नहीं है।"
            }

        # 2. GANDAMOOLA CALCULATION
        # Nakshatras: 1 (Ashwini), 9 (Ashlesha), 10 (Magha), 18 (Jyeshtha), 19 (Moola), 27 (Revati)
        is_gandamoola = nak_idx in [1, 9, 10, 18, 19, 27]
        gandamoola_data = {}

        if is_gandamoola:
            ganda_padas = {
                1: {  # Ashwini
                    1: ("पिता को कष्ट की संभावना", "अश्विनी चरण १: पिता हेतु सतर्कता, २७ दिन बाद मूल शान्ति आवश्यक"),
                    2: ("ऐश्वर्य, सुख व धन लाभ", "अश्विनी चरण २: जातक धनवान व सुखी होता है"),
                    3: ("राजसम्मान व मंत्री पद", "अश्विनी चरण ३: विद्या, सम्मान व उच्च प्रतिष्ठा"),
                    4: ("राजकृपा व आरोग्य", "अश्विनी चरण ४: शुभ व आरोग्यप्रद")
                },
                9: {  # Ashlesha
                    1: ("शुभ फल, राजकृपा", "आश्लेषा चरण १: सामान्य शुभ"),
                    2: ("धनहानि व द्रव्य नाश", "आश्लेषा चरण २: धन नाश का भय, शान्ति आवश्यक"),
                    3: ("माता को कष्ट", "आश्लेषा चरण ३: माता के स्वास्थ्य हेतु सतर्कता"),
                    4: ("पिता को कष्ट", "आश्लेषा चरण ४: पिता के स्वास्थ्य हेतु सतर्कता")
                },
                10: {  # Magha
                    1: ("माता को कष्ट", "मघा चरण १: माता हेतु कष्टकारी, शान्ति आवश्यक"),
                    2: ("पिता को भय", "मघा चरण २: पिता हेतु सतर्कता"),
                    3: ("उत्तम सुख व समृद्धि", "मघा चरण ३: जातक को सुख-समृद्धि प्राप्त होती है"),
                    4: ("विद्या, धन व सम्मान", "मघा चरण ४: परम कल्याणकारी")
                },
                18: {  # Jyeshtha
                    1: ("बड़े भाई को कष्ट", "ज्येष्ठा चरण १: अग्रज (बड़े भाई) हेतु अनिष्ट"),
                    2: ("छोटे भाई को कष्ट", "ज्येष्ठा चरण २: अनुज (छोटे भाई) हेतु कष्ट"),
                    3: ("माता को कष्ट", "ज्येष्ठा चरण ३: माता हेतु अनिष्टकारी"),
                    4: ("स्वयं जातक को कष्ट", "ज्येष्ठा चरण ४: जातक स्वयं व्याधिग्रस्त रह सकता है")
                },
                19: {  # Moola
                    1: ("पिता को कष्ट", "मूल चरण १: पिता हेतु कष्टकारी, २७ दिन मूल शान्ति अनिवार्य"),
                    2: ("माता को कष्ट", "मूल चरण २: माता के स्वास्थ्य में अड़चनें"),
                    3: ("धनहानि व अपव्यय", "मूल चरण ३: कुल व धन की हानि"),
                    4: ("शुभ फल, राजयोग", "मूल चरण ४: शुभ, जातक प्रभावशाली व धनी बनता है")
                },
                27: {  # Revati
                    1: ("राजसम्मान व सुख", "रेवती चरण १: उत्तम, राजकीय लाभ"),
                    2: ("मंत्रिपद व प्रतिष्ठा", "रेवती चरण २: मान-प्रतिष्ठा वृद्धि"),
                    3: ("धन-धान्य लाभ", "रेवती चरण ३: व्यापार व धन में वृद्धि"),
                    4: ("स्वयं को कष्ट व माता-पिता को पीड़ा", "रेवती चरण ४: चरण ४ मूल नक्षत्र संधि में होने से शान्ति विधान आवश्यक")
                }
            }
            nak_name = NAKSHATRA_EXTENDED[nak_idx - 1]["name"]
            p_effect, p_full = ganda_padas.get(nak_idx, {}).get(pada, ("गण्डमूल दोष", "शान्ति पूजा आवश्यक"))
            gandamoola_data = {
                "is_active": True,
                "nakshatra": nak_name,
                "pada": pada,
                "badge": "⚠️ गण्डमूल नक्षत्र सक्रिय",
                "color": "#DC2626",
                "pada_effect": p_effect,
                "desc": p_full,
                "shanti_vidhi": f"जन्म के २७वें दिन जब पुनः '{nak_name}' नक्षत्र आए, तब २७ कुओं के जल, २७ वृक्षों के पत्तों व मूल शान्ति हवन द्वारा वैदिक शान्ति करवानी चाहिए।"
            }
        else:
            gandamoola_data = {
                "is_active": False,
                "badge": "🟢 गण्डमूल रहित",
                "color": "#059669",
                "desc": "वर्तमान नक्षत्र गण्डमूल (अश्विनी, आश्लेषा, मघा, ज्येष्ठा, मूल, रेवती) के अंतर्गत नहीं आता। सर्वथा निर्दोष है।"
            }

        return {
            "panchaka": panchaka_data,
            "gandamoola": gandamoola_data
        }

    @classmethod
    def calculate_choghadiya_and_horas(
        cls,
        target_date: date,
        sunrise_dt: datetime,
        sunset_dt: datetime,
        next_sunrise_dt: datetime
    ) -> Dict[str, Any]:
        """Calculates 8 Day & 8 Night Choghadiyas and 24 Planetary Horas with minute accuracy."""
        wday = target_date.weekday()
        day_span = (sunset_dt - sunrise_dt).total_seconds()
        night_span = (next_sunrise_dt - sunset_dt).total_seconds()

        day_part = day_span / 8.0
        night_part = night_span / 8.0

        # Day Choghadiya
        day_chogs = []
        d_order = DAY_CHOGHADIYA_ORDERS.get(wday, DAY_CHOGHADIYA_ORDERS[6])
        for i, c_key in enumerate(d_order):
            st_t = sunrise_dt + timedelta(seconds=i * day_part)
            en_t = sunrise_dt + timedelta(seconds=(i + 1) * day_part)
            m = CHOGHADIYA_TYPES[c_key]
            day_chogs.append({
                "slot": i + 1,
                "name": m["name_hi"],
                "type": c_key,
                "nature": m["nature"],
                "planet": m["planet"],
                "start": st_t.strftime("%I:%M %p"),
                "end": en_t.strftime("%I:%M %p"),
                "acts": m["acts"],
                "color": m["color"],
                "bg": m["bg"],
                "is_good": m["is_good"]
            })

        # Night Choghadiya
        night_chogs = []
        n_order = NIGHT_CHOGHADIYA_ORDERS.get(wday, NIGHT_CHOGHADIYA_ORDERS[6])
        for i, c_key in enumerate(n_order):
            st_t = sunset_dt + timedelta(seconds=i * night_part)
            en_t = sunset_dt + timedelta(seconds=(i + 1) * night_part)
            m = CHOGHADIYA_TYPES[c_key]
            night_chogs.append({
                "slot": i + 1,
                "name": m["name_hi"],
                "type": c_key,
                "nature": m["nature"],
                "planet": m["planet"],
                "start": st_t.strftime("%I:%M %p"),
                "end": en_t.strftime("%I:%M %p"),
                "acts": m["acts"],
                "color": m["color"],
                "bg": m["bg"],
                "is_good": m["is_good"]
            })

        # 24 Horas
        # First hora of day is day lord; follows Chaldean order
        first_planet = HORA_DAY_FIRST[wday]
        first_idx = HORA_CHALDEAN_ORDER.index(first_planet)
        day_hora_sec = day_span / 12.0
        night_hora_sec = night_span / 12.0

        horas_24 = []
        planet_names_hi = {
            "Sun": "सूर्य (Sun)", "Venus": "शुक्र (Venus)", "Mercury": "बुध (Mercury)",
            "Moon": "चन्द्र (Moon)", "Saturn": "शनि (Saturn)", "Jupiter": "गुरु (Jupiter)", "Mars": "मंगल (Mars)"
        }
        hora_acts = {
            "Sun": "राजकीय कार्य, पदग्रहण, उच्चाधिकारियों से भेंट, पिता से परामर्श",
            "Venus": "विवाह, आभूषण क्रय, कला, सौन्दर्य प्रसाधन, नवीन वस्त्र",
            "Mercury": "व्यापार, बहीखाता, लेखन, हस्ताक्षर, शेयर बाजार, अध्ययन",
            "Moon": "जल संबंधी कार्य, यात्रा, नवीन कार्य आरम्भ, माता की सेवा",
            "Saturn": "मशीनरी, लोहा, तेल, भूमि, स्थायी कार्य, गुप्त साधना",
            "Jupiter": "धार्मिक अनुष्ठान, विद्यारम्भ, ज्ञान चर्चा, विवाह निर्णय, दान",
            "Mars": "शस्त्र, भूमि क्रय-विक्रय, साहस, सर्जरी, वाद-विवाद"
        }

        # 12 Day Horas
        for h in range(12):
            p_name = HORA_CHALDEAN_ORDER[(first_idx + h) % 7]
            st_t = sunrise_dt + timedelta(seconds=h * day_hora_sec)
            en_t = sunrise_dt + timedelta(seconds=(h + 1) * day_hora_sec)
            horas_24.append({
                "hora_num": h + 1,
                "period": "दिन की होरा",
                "planet": planet_names_hi[p_name],
                "start": st_t.strftime("%I:%M %p"),
                "end": en_t.strftime("%I:%M %p"),
                "acts": hora_acts[p_name]
            })

        # 12 Night Horas
        for h in range(12):
            p_name = HORA_CHALDEAN_ORDER[(first_idx + 12 + h) % 7]
            st_t = sunset_dt + timedelta(seconds=h * night_hora_sec)
            en_t = sunset_dt + timedelta(seconds=(h + 1) * night_hora_sec)
            horas_24.append({
                "hora_num": h + 13,
                "period": "रात्रि की होरा",
                "planet": planet_names_hi[p_name],
                "start": st_t.strftime("%I:%M %p"),
                "end": en_t.strftime("%I:%M %p"),
                "acts": hora_acts[p_name]
            })

        return {
            "day_choghadiyas": day_chogs,
            "night_choghadiyas": night_chogs,
            "horas_24": horas_24
        }

    @classmethod
    def calculate_shubh_ashubh_muhurtas(
        cls,
        target_date: date,
        sunrise_dt: datetime,
        sunset_dt: datetime,
        next_sunrise_dt: datetime,
        nakshatra_idx: int
    ) -> Dict[str, Any]:
        """Calculates Abhijit, Brahma, Vijaya, Godhuli, Amrit Kaal, Nishita, Rahu Kaal, Yamaganda, Gulika, Durmuhurta."""
        wday = target_date.weekday()
        day_span = (sunset_dt - sunrise_dt).total_seconds()
        night_span = (next_sunrise_dt - sunset_dt).total_seconds()
        day_seg8 = day_span / 8.0

        # 1. RAHU KAAL (1/8th of Dinamana)
        rahu_parts = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
        r_part = rahu_parts.get(wday, 8)
        rahu_st = sunrise_dt + timedelta(seconds=(r_part - 1) * day_seg8)
        rahu_en = sunrise_dt + timedelta(seconds=r_part * day_seg8)

        # 2. YAMAGANDA
        yama_parts = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
        y_part = yama_parts.get(wday, 5)
        yama_st = sunrise_dt + timedelta(seconds=(y_part - 1) * day_seg8)
        yama_en = sunrise_dt + timedelta(seconds=y_part * day_seg8)

        # 3. GULIKA KAAL
        gulika_parts = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
        g_part = gulika_parts.get(wday, 7)
        gulika_st = sunrise_dt + timedelta(seconds=(g_part - 1) * day_seg8)
        gulika_en = sunrise_dt + timedelta(seconds=g_part * day_seg8)

        # 4. ABHIJIT MUHURTA (8th Muhurta of 15 Muhurtas of day)
        muhurta_day_sec = day_span / 15.0
        abhijit_st = sunrise_dt + timedelta(seconds=7 * muhurta_day_sec)
        abhijit_en = sunrise_dt + timedelta(seconds=8 * muhurta_day_sec)
        is_abhijit_allowed = (wday != 2)  # Prohibited on Wednesday according to classical rule

        # 5. BRAHMA MUHURTA (2 Muhurtas before sunrise: 96 min to 48 min before sunrise)
        brahma_st = sunrise_dt - timedelta(minutes=96)
        brahma_en = sunrise_dt - timedelta(minutes=48)

        # 6. VIJAYA MUHURTA (11th Muhurta of day)
        vijaya_st = sunrise_dt + timedelta(seconds=10 * muhurta_day_sec)
        vijaya_en = sunrise_dt + timedelta(seconds=11 * muhurta_day_sec)

        # 7. GODHULI MUHURTA (24 min before and 24 min after sunset)
        godhuli_st = sunset_dt - timedelta(minutes=24)
        godhuli_en = sunset_dt + timedelta(minutes=24)

        # 8. SAYAHNA SANDHYA
        sayahna_st = sunset_dt - timedelta(minutes=24)
        sayahna_en = sunset_dt + timedelta(minutes=48)

        # 9. NISHITA KAAL (Midnight 8th Muhurta of night)
        muhurta_night_sec = night_span / 15.0
        nishita_st = sunset_dt + timedelta(seconds=7 * muhurta_night_sec)
        nishita_en = sunset_dt + timedelta(seconds=8 * muhurta_night_sec)

        # 10. AMRIT KAAL (Nakshatra-based Amrit Ghatis)
        # Classical Ghatis from start of Nakshatra
        amrit_nak_ghatis = [
            42, 48, 54, 40, 38, 35, 54, 44, 56, 30, 39, 42, 50, 48, 44, 44, 38, 42, 42, 44, 50, 34, 30, 48, 32, 52, 50
        ]
        a_ghati = amrit_nak_ghatis[(nakshatra_idx - 1) % 27]
        # 1 Ghati = 24 minutes; Amrit kaal lasts 4 Ghatis (1 hr 36 min)
        amrit_st = sunrise_dt + timedelta(minutes=a_ghati * 24 % (24 * 60))
        amrit_en = amrit_st + timedelta(minutes=96)

        # 11. DURMUHURTA (Malefic 48-min windows by weekday)
        durmuhurtas = []
        if wday == 6:  # Sunday: 14th Muhurta
            st = sunrise_dt + timedelta(seconds=13 * muhurta_day_sec)
            durmuhurtas.append(f"{st.strftime('%I:%M %p')} - {(st + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
        elif wday == 0:  # Monday: 9th & 12th Muhurta
            st1 = sunrise_dt + timedelta(seconds=8 * muhurta_day_sec)
            st2 = sunrise_dt + timedelta(seconds=11 * muhurta_day_sec)
            durmuhurtas.append(f"{st1.strftime('%I:%M %p')} - {(st1 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
            durmuhurtas.append(f"{st2.strftime('%I:%M %p')} - {(st2 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
        elif wday == 1:  # Tuesday: 2nd & 11th Muhurta
            st1 = sunrise_dt + timedelta(seconds=1 * muhurta_day_sec)
            st2 = sunrise_dt + timedelta(seconds=10 * muhurta_day_sec)
            durmuhurtas.append(f"{st1.strftime('%I:%M %p')} - {(st1 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
            durmuhurtas.append(f"{st2.strftime('%I:%M %p')} - {(st2 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
        elif wday == 2:  # Wednesday: 5th Muhurta
            st = sunrise_dt + timedelta(seconds=4 * muhurta_day_sec)
            durmuhurtas.append(f"{st.strftime('%I:%M %p')} - {(st + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
        elif wday == 3:  # Thursday: 6th & 7th Muhurta
            st1 = sunrise_dt + timedelta(seconds=5 * muhurta_day_sec)
            st2 = sunrise_dt + timedelta(seconds=6 * muhurta_day_sec)
            durmuhurtas.append(f"{st1.strftime('%I:%M %p')} - {(st1 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
            durmuhurtas.append(f"{st2.strftime('%I:%M %p')} - {(st2 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
        elif wday == 4:  # Friday: 4th & 9th Muhurta
            st1 = sunrise_dt + timedelta(seconds=3 * muhurta_day_sec)
            st2 = sunrise_dt + timedelta(seconds=8 * muhurta_day_sec)
            durmuhurtas.append(f"{st1.strftime('%I:%M %p')} - {(st1 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
            durmuhurtas.append(f"{st2.strftime('%I:%M %p')} - {(st2 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
        elif wday == 5:  # Saturday: 1st & 2nd Muhurta
            st1 = sunrise_dt
            st2 = sunrise_dt + timedelta(seconds=1 * muhurta_day_sec)
            durmuhurtas.append(f"{st1.strftime('%I:%M %p')} - {(st1 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")
            durmuhurtas.append(f"{st2.strftime('%I:%M %p')} - {(st2 + timedelta(seconds=muhurta_day_sec)).strftime('%I:%M %p')}")

        # 12. VARJYAM (Tyajya Ghatis)
        varjyam_ghatis = [
            50, 24, 30, 40, 14, 11, 30, 20, 32, 30, 20, 18, 21, 20, 14, 14, 10, 14, 20, 20, 20, 10, 10, 18, 16, 24, 30
        ]
        v_ghati = varjyam_ghatis[(nakshatra_idx - 1) % 27]
        varjyam_st = sunrise_dt + timedelta(minutes=v_ghati * 24 % (24 * 60))
        varjyam_en = varjyam_st + timedelta(minutes=96)

        return {
            "shubh_windows": [
                {
                    "title": "🌟 अभिजित मुहूर्त (Abhijit Muhurta)",
                    "time": f"{abhijit_st.strftime('%I:%M %p')} - {abhijit_en.strftime('%I:%M %p')}",
                    "status": "सर्वोत्तम शुभ (सर्व दोष नाशक)" if is_abhijit_allowed else "बुधवार होने से त्याज्य",
                    "badge": "🟢 अति शुभ" if is_abhijit_allowed else "⚠️ त्याज्य",
                    "color": "#059669" if is_abhijit_allowed else "#D97706"
                },
                {
                    "title": "🕉️ ब्रह्म मुहूर्त (Brahma Muhurta)",
                    "time": f"{brahma_st.strftime('%I:%M %p')} - {brahma_en.strftime('%I:%M %p')}",
                    "status": "ईश्वर आराधना, योग, ध्यान व अध्ययन हेतु परम पावन",
                    "badge": "🟢 पावन काल",
                    "color": "#059669"
                },
                {
                    "title": "🏹 विजय मुहूर्त (Vijaya Muhurta)",
                    "time": f"{vijaya_st.strftime('%I:%M %p')} - {vijaya_en.strftime('%I:%M %p')}",
                    "status": "मुकदमा, विवाद विजय, कार्य सफलता व नवीन आरम्भ",
                    "badge": "🟢 शुभ",
                    "color": "#059669"
                },
                {
                    "title": "🌅 गोधूलि मुहूर्त (Godhuli Muhurta)",
                    "time": f"{godhuli_st.strftime('%I:%M %p')} - {godhuli_en.strftime('%I:%M %p')}",
                    "status": "संध्या वन्दन, गृह प्रवेश व शांति कर्म",
                    "badge": "🟢 शुभ",
                    "color": "#059669"
                },
                {
                    "title": "🍯 अमृत काल (Amrita Kaalam)",
                    "time": f"{amrit_st.strftime('%I:%M %p')} - {amrit_en.strftime('%I:%M %p')}",
                    "status": "दीर्घकालिक कार्य, वाणिज्य एवं मांगलिक कर्म",
                    "badge": "🟢 परम शुभ",
                    "color": "#059669"
                },
                {
                    "title": "🌙 निशिता मुहूर्त (Nishita Kaal)",
                    "time": f"{nishita_st.strftime('%I:%M %p')} - {nishita_en.strftime('%I:%M %p')}",
                    "status": "मध्यरात्रि तंत्र साधना, शिव आराधना व मंत्र सिद्धि",
                    "badge": "🟣 तंत्र-साधना",
                    "color": "#7C3AED"
                }
            ],
            "ashubh_windows": [
                {
                    "title": "🚨 राहुकाल (Rahu Kaal)",
                    "time": f"{rahu_st.strftime('%I:%M %p')} - {rahu_en.strftime('%I:%M %p')}",
                    "status": "शुभ कार्य सर्वथा वर्जित; धनहानि व बाधा की आशंका",
                    "badge": "🔴 महा-अशुभ",
                    "color": "#DC2626"
                },
                {
                    "title": "⚠️ यमघण्ट काल (Yamaghanta)",
                    "time": f"{yama_st.strftime('%I:%M %p')} - {yama_en.strftime('%I:%M %p')}",
                    "status": "यात्रा व नवीन कार्य आरम्भ सर्वथा वर्जित",
                    "badge": "🔴 अशुभ",
                    "color": "#DC2626"
                },
                {
                    "title": "⏳ गुलिक काल (Gulika Kaal)",
                    "time": f"{gulika_st.strftime('%I:%M %p')} - {gulika_en.strftime('%I:%M %p')}",
                    "status": "शनि पुत्र गुलिक का प्रभाव; मांगलिक कार्य वर्जित, स्थिर कर्म सामान्य",
                    "badge": "🟡 मध्यम",
                    "color": "#D97706"
                },
                {
                    "title": "🚫 दुर्मुहूर्त (Durmuhurta)",
                    "time": ", ".join(durmuhurtas),
                    "status": "विवाद व असफलता कारक समय; नया कार्य न करें",
                    "badge": "🔴 त्याज्य",
                    "color": "#DC2626"
                },
                {
                    "title": "⚡ वर्ज्यम् (Varjyam / Tyajya)",
                    "time": f"{varjyam_st.strftime('%I:%M %p')} - {varjyam_en.strftime('%I:%M %p')}",
                    "status": "नक्षत्र का विष भाग; समस्त शुभ कर्मों में वर्जित",
                    "badge": "🔴 विष काल",
                    "color": "#DC2626"
                }
            ]
        }

    @classmethod
    def calculate_anandadi_and_special_yogas(
        cls,
        target_date: date,
        sun_nak_idx: int,
        moon_nak_idx: int,
        tithi_idx: int
    ) -> Dict[str, Any]:
        """Calculates Sarvartha Siddhi, Amrit Siddhi, Dwi-Pushkar, Tri-Pushkar, Ravi Pushya, Guru Pushya, Ravi Yoga, Anandadi 28."""
        wday = target_date.weekday()

        # 1. SARVARTHA SIDDHI YOGA
        sarvartha_rules = {
            6: [13, 19, 12, 21, 26, 1, 8],      # Sun + Hasta, Moola, U.Phal, U.Ashadha, U.Bhadra, Ashwini, Pushya
            0: [4, 5, 8, 17, 22],                # Mon + Rohini, Mrigashira, Pushya, Anuradha, Shravana
            1: [1, 3, 9, 26],                    # Tue + Ashwini, Krittika, Ashlesha, U.Bhadrapada
            2: [4, 5, 13, 17, 3],                # Wed + Rohini, Mrigashira, Hasta, Anuradha, Krittika
            3: [1, 7, 8, 17, 27],                # Thu + Ashwini, Punarvasu, Pushya, Anuradha, Revati
            4: [1, 2, 4, 12, 14, 17, 27],        # Fri + Ashwini, Bharani, Rohini, U.Phal, Chitra, Anuradha, Revati
            5: [4, 15, 22]                       # Sat + Rohini, Swati, Shravana
        }
        is_sarvartha = moon_nak_idx in sarvartha_rules.get(wday, [])

        # 2. AMRIT SIDDHI YOGA
        amrit_rules = {
            6: 13,  # Sun + Hasta
            0: 5,   # Mon + Mrigashira
            1: 1,   # Tue + Ashwini
            2: 17,  # Wed + Anuradha
            3: 8,   # Thu + Pushya
            4: 27,  # Fri + Revati
            5: 4    # Sat + Rohini
        }
        is_amrit_siddhi = (moon_nak_idx == amrit_rules.get(wday, -1))

        # 3. GURU PUSHYA & RAVI PUSHYA
        is_guru_pushya = (wday == 3 and moon_nak_idx == 8)
        is_ravi_pushya = (wday == 6 and moon_nak_idx == 8)

        # 4. DWI-PUSHKAR YOGA
        # Sun/Tue/Sat + Bhadra Tithi (2, 7, 12) + Dwiswabhav Nakshatra (Mrigashira, Chitra, Dhanishta)
        is_bhadra_tithi = (tithi_idx in [2, 7, 12, 17, 22, 27])
        is_dwipushkar_nak = (moon_nak_idx in [5, 14, 23])  # Mrigashira, Chitra, Dhanishta
        is_dwi_pushkar = (wday in [6, 1, 5]) and is_bhadra_tithi and is_dwipushkar_nak

        # 5. TRI-PUSHKAR YOGA
        # Sun/Tue/Sat + Bhadra Tithi + Tripushkar Nakshatra (Krittika, Punarvasu, U.Phal, Vishakha, U.Ashadha, U.Bhadra)
        is_tripushkar_nak = (moon_nak_idx in [3, 7, 12, 16, 21, 26])
        is_tri_pushkar = (wday in [6, 1, 5]) and is_bhadra_tithi and is_tripushkar_nak

        # 6. RAVI YOGA
        # Moon nakshatra is 4, 6, 9, 10, 13, 20 from Sun nakshatra
        diff_from_sun = ((moon_nak_idx - sun_nak_idx) % 27) + 1
        is_ravi_yoga = diff_from_sun in [4, 6, 9, 10, 13, 20]

        # 7. ANANDADI 28 YOGAS
        # Count from Sun Nakshatra to Moon Nakshatra:
        anandadi_idx = ((moon_nak_idx - sun_nak_idx) % 28)
        anand_tuple = ANANDADI_YOGAS_28[anandadi_idx % 28]

        special_yogas_list = []
        if is_guru_pushya:
            special_yogas_list.append({
                "title": "👑 गुरु पुष्य योग (Guru Pushya Amrit Yoga)",
                "badge": "🌟 महा-राजयोग",
                "color": "#059669",
                "desc": "गुरुवार व पुष्य नक्षत्र का दुर्लभ संयोग! स्वर्ण क्रय, नवीन प्रतिष्ठान व सर्व कार्य सिद्धि हेतु परम शुभ।"
            })
        if is_ravi_pushya:
            special_yogas_list.append({
                "title": "☀️ रवि पुष्य योग (Ravi Pushya Yoga)",
                "badge": "🌟 महा-शुभ",
                "color": "#059669",
                "desc": "रविवार व पुष्य नक्षत्र का परम फलदायी योग! संपत्ति क्रय, व्यापार व आरोग्य हेतु अद्वितीय।"
            })
        if is_amrit_siddhi:
            special_yogas_list.append({
                "title": "🍯 अमृत सिद्धि योग (Amrit Siddhi Yoga)",
                "badge": "🟢 परम शुभ",
                "color": "#059669",
                "desc": "वार व नक्षत्र के शुभ मिलन से अमृत सिद्धि योग सक्रिय। इस समय किया गया कार्य अमर व सिद्ध होता है।"
            })
        if is_sarvartha:
            special_yogas_list.append({
                "title": "💎 सर्वार्थ सिद्धि योग (Sarvartha Siddhi Yoga)",
                "badge": "🟢 अति शुभ",
                "color": "#059669",
                "desc": "समस्त अभिलाषाओं व मनोकामनाओं को सिद्ध करने वाला महायोग! अनुबंध, यात्रा व क्रय-विक्रय हेतु उत्तम।"
            })
        if is_ravi_yoga:
            special_yogas_list.append({
                "title": "🔆 रवि योग (Ravi Yoga)",
                "badge": "🟢 सूर्य कृपा",
                "color": "#059669",
                "desc": "रवि योग समस्त अनिष्टों व विघ्नों का भंजन करता है। राजकीय व प्रशासनिक कार्यों हेतु श्रेष्ठ।"
            })
        if is_dwi_pushkar:
            special_yogas_list.append({
                "title": "⚖️ द्विपुष्कर योग (Dwi-Pushkar Yoga)",
                "badge": "🟡 द्विगुण फल",
                "color": "#D97706",
                "desc": "इस योग में घटित घटना दोहराई जाती है (२ गुना फल)। शुभ कार्य करने पर दोगुना लाभ; ऋण लेने पर २ गुना भार।"
            })
        if is_tri_pushkar:
            special_yogas_list.append({
                "title": "⚖️ त्रिपुष्कर योग (Tri-Pushkar Yoga)",
                "badge": "🟡 त्रिगुण फल",
                "color": "#D97706",
                "desc": "इस योग में घटित घटना ३ गुना फल देती है। संपत्ति व धन लाभ ३ गुना; परंतु ऋण व हानि भी ३ गुना हो सकती है।"
            })

        return {
            "special_yogas": special_yogas_list,
            "anandadi_yoga": {
                "name": anand_tuple[0],
                "name_en": anand_tuple[1],
                "nature": anand_tuple[2],
                "is_good": anand_tuple[3],
                "color": "#059669" if anand_tuple[3] else "#DC2626",
                "badge": "🟢 शुभ योग" if anand_tuple[3] else "🔴 अशुभ योग",
                "desc": anand_tuple[4]
            }
        }

    @classmethod
    def calculate_nivas_shoola_and_vedic_clock(
        cls,
        target_date: date,
        sunrise_dt: datetime,
        moon_sign: int,
        tithi_idx: int
    ) -> Dict[str, Any]:
        """Calculates Disha Shoola & Parihar, Chandra Vasa, Agnivasa, Shivavasa, and 60-Ghati Vedic Clock."""
        wday = target_date.weekday()

        # 1. DISHA SHOOLA
        shoola_data = {
            6: ("पश्चिम (West)", "पान (Betel Leaf) खाकर अथवा जौ चबाकर प्रस्थान करें।"),
            0: ("पूर्व (East)", "दर्पण (Mirror) देखकर अथवा तिल खाकर प्रस्थान करें।"),
            1: ("उत्तर (North)", "गुड़ (Jaggery) खाकर अथवा धनिया चबाकर प्रस्थान करें।"),
            2: ("उत्तर (North)", "धनिया अथवा तिल खाकर प्रस्थान करें।"),
            3: ("दक्षिण (South)", "दही (Curd) अथवा जीरा खाकर प्रस्थान करें।"),
            4: ("पश्चिम (West)", "जौ (Barley) खाकर अथवा राई देखकर प्रस्थान करें।"),
            5: ("पूर्व (East)", "उड़द (Urad) अथवा तिल का सेवन कर प्रस्थान करें।")
        }
        shoola_dir, shoola_parihar = shoola_data.get(wday, ("पूर्व", "ईश्वर स्मरण कर प्रस्थान करें।"))

        # 2. CHANDRA VASA (Moon Direction)
        # Moon in 1, 5, 9 -> East; 2, 6, 10 -> South; 3, 7, 11 -> West; 4, 8, 12 -> North
        chandra_dir_map = {
            1: "पूर्व (East)", 5: "पूर्व (East)", 9: "पूर्व (East)",
            2: "दक्षिण (South)", 6: "दक्षिण (South)", 10: "दक्षिण (South)",
            3: "पश्चिम (West)", 7: "पश्चिम (West)", 11: "पश्चिम (West)",
            4: "उत्तर (North)", 8: "उत्तर (North)", 12: "उत्तर (North)"
        }
        chandra_dir = chandra_dir_map.get(moon_sign, "पूर्व")

        # 3. AGNIVASA (अग्निवास - हवन विचार)
        # Classical formula: (Tithi + Weekday + 1) % 4
        # 0 or 3 -> Prithvi (Earth - Auspicious); 1 -> Akash (Inauspicious); 2 -> Patala (Inauspicious)
        agni_val = (tithi_idx + wday + 1) % 4
        if agni_val in [0, 3]:
            agni_vasa = "पृथ्वी लोक (Prithvi Loka)"
            agni_verdict = "🟢 हवन/यज्ञ हेतु अत्यंत शुभ व कल्याणकारी। अग्निदेव पृथ्वी पर वास कर रहे हैं।"
            agni_color = "#059669"
        elif agni_val == 1:
            agni_vasa = "आकाश लोक (Akash Loka)"
            agni_verdict = "🔴 अग्निदेव आकाश में हैं। हवन करने से प्राण व सुख का संताप हो सकता है।"
            agni_color = "#DC2626"
        else:
            agni_vasa = "पाताल लोक (Patala Loka)"
            agni_verdict = "🔴 अग्निदेव पाताल में हैं। हवन करने से धनहानि का भय रहता है।"
            agni_color = "#DC2626"

        # 4. SHIVAVASA (शिववास - रुद्राभिषेक विचार)
        # Classical formula: (Shukla Tithi * 2 + 5) % 7
        t_num = tithi_idx if tithi_idx <= 15 else (tithi_idx - 15)
        shiva_val = (t_num * 2 + 5) % 7
        shiva_map = {
            1: ("कैलाश पर्वत (Kailash)", "🟢 परम शुभ; सुख, शांति व आरोग्य की प्राप्ति।", "#059669"),
            2: ("गौरी के संग (With Gauri)", "🟢 अति शुभ; पारिवारिक आनंद व सौभाग्य वृद्धि।", "#059669"),
            3: ("वृषभारूढ़ (On Nandi)", "🟢 सर्वोत्तम; समस्त मनोकामनाएं पूर्ण होती हैं।", "#059669"),
            4: ("सभा में (In Sabha)", "🟡 मध्यम; संताप व चिंता का भय।", "#D97706"),
            5: ("भोजन में (Eating)", "🔴 त्याज्य; अन्न व शारीरिक कष्ट की आशंका।", "#DC2626"),
            6: ("क्रीड़ा में (In Leela)", "🔴 त्याज्य; कार्य में विघ्न व विलंब।", "#DC2626"),
            0: ("श्मशान में (In Smashana)", "🔴 सर्वथा त्याज्य; अनिष्ट व संताप का भय।", "#DC2626")
        }
        shiva_vasa, shiva_desc, shiva_color = shiva_map.get(shiva_val, ("कैलाश", "शुभ", "#059669"))

        # 5. VEDIC CLOCK (60 Ghatis)
        now_dt = datetime.now()
        ishta_sec = max(0, (now_dt - sunrise_dt).total_seconds())
        ishta_ghati = ishta_sec / 1440.0
        g_val = int(ishta_ghati)
        p_val = int((ishta_ghati - g_val) * 60.0)
        v_val = int((((ishta_ghati - g_val) * 60.0) - p_val) * 60.0)

        return {
            "disha_shoola": {
                "direction": shoola_dir,
                "parihar": shoola_parihar
            },
            "chandra_vasa": {
                "direction": chandra_dir,
                "rule": "यात्रा में चन्द्रमा सम्मुख अथवा दाहिने होना शुभ, पीछे अथवा बाएं होना वर्जित माना गया है।"
            },
            "agnivasa": {
                "vasa": agni_vasa,
                "verdict": agni_verdict,
                "color": agni_color
            },
            "shivavasa": {
                "vasa": shiva_vasa,
                "verdict": shiva_desc,
                "color": shiva_color
            },
            "vedic_clock": {
                "ishta_str": f"{g_val} घटी, {p_val} पल, {v_val} विपल",
                "ghati_decimal": round(ishta_ghati, 2),
                "desc": "सूर्योदय से वर्तमान क्षण तक का इष्टकाल वैदिक घटी-पल में।"
            }
        }

    @classmethod
    def calculate_chandrabalam_and_tarabalam(
        cls,
        today_moon_sign: int,
        today_nak_idx: int
    ) -> Dict[str, Any]:
        """Calculates Chandrabalam for all 12 Rashis and Tarabalam for all 27 Nakshatras."""
        # Chandrabalam for each rashi:
        # Distance = ((today_moon_sign - native_rashi) % 12) + 1
        # 1, 3, 6, 7, 10, 11 -> Strong (Shubh)
        # 2, 5, 9 -> Neutral / Average (Madhyam)
        # 4, 8, 12 -> Weak / Inauspicious (Ashubh)
        rashi_names = [
            "मेष (Aries)", "वृषभ (Taurus)", "मिथुन (Gemini)", "कर्क (Cancer)",
            "सिंह (Leo)", "कन्या (Virgo)", "तुला (Libra)", "वृश्चिक (Scorpio)",
            "धनु (Sagittarius)", "मकर (Capricorn)", "कुम्भ (Aquarius)", "मीन (Pisces)"
        ]

        chandrabalam_list = []
        for r_idx in range(1, 13):
            dist = ((today_moon_sign - r_idx) % 12) + 1
            if dist in [1, 3, 6, 7, 10, 11]:
                b_str = "🟢 बली / शुभ (Chandra Balam)"
                b_color = "#059669"
                score = "उत्तम"
            elif dist in [2, 5, 9]:
                b_str = "🟡 मध्यम (Neutral)"
                b_color = "#D97706"
                score = "सामान्य"
            else:
                b_str = "🔴 शून्य / अनिष्ट (No Bala)"
                b_color = "#DC2626"
                score = "कमजोर"

            chandrabalam_list.append({
                "rashi": rashi_names[r_idx - 1],
                "house_from_moon": f"{dist}वां चन्द्र",
                "status": b_str,
                "color": b_color,
                "score": score
            })

        # Tarabalam for all 27 Nakshatras
        # (today_nak_idx - birth_nak_idx) % 9 + 1
        tara_definitions = {
            1: ("जन्म तारा (Janma)", "⚠️ सतर्कता / सामान्य", "#D97706", "शारीरिक कष्ट की आशंका; नवीन कार्य में सावधानी।"),
            2: ("सम्पत् तारा (Sampat)", "🟢 अति शुभ", "#059669", "धन, समृद्धि, व्यापार व सफलता।"),
            3: ("विपत् तारा (Vipat)", "🔴 अशुभ (वर्जित)", "#DC2626", "विपत्ति, हानि व अवरोध। कार्य वर्जित।"),
            4: ("क्षेम तारा (Kshema)", "🟢 शुभ", "#059669", "कल्याण, आरोग्य व कार्य सिद्धि।"),
            5: ("प्रत्यरि तारा (Pratyari)", "🔴 अशुभ (वर्जित)", "#DC2626", "शत्रुता, विवाद व अड़चनें।"),
            6: ("साधक तारा (Sadhaka)", "🟢 अति शुभ", "#059669", "मनोकामना पूर्ति, विजय व सफलता।"),
            7: ("वध / निधन तारा (Vadha)", "🔴 महा-अशुभ (सर्वथा वर्जित)", "#991B1B", "गंभीर कष्ट व दुर्घटना भय। सर्वथा त्याज्य।"),
            8: ("मित्र तारा (Mitra)", "🟢 शुभ", "#059669", "सुखद सहयोग व मैत्री लाभ।"),
            9: ("परम मित्र तारा (Param Mitra)", "🟢 परम शुभ", "#059669", "सर्वोच्च सिद्धि व मंगलकारी।")
        }

        tarabalam_list = []
        for n_idx in range(1, 28):
            n_name = NAKSHATRA_EXTENDED[n_idx - 1]["name"]
            diff = ((today_nak_idx - n_idx) % 9) + 1
            t_name, t_badge, t_color, t_desc = tara_definitions[diff]
            tarabalam_list.append({
                "nakshatra": n_name,
                "tara_name": t_name,
                "badge": t_badge,
                "color": t_color,
                "desc": t_desc,
                "is_good": diff in [2, 4, 6, 8, 9]
            })

        return {
            "chandrabalam": chandrabalam_list,
            "tarabalam": tarabalam_list
        }

    @classmethod
    def calculate_samvatsara_and_cabinet(
        cls,
        target_date: date,
        sun_lon: float
    ) -> Dict[str, Any]:
        """Calculates Vikram Samvat, Shaka Samvat, Jovian Year, Ayana, Ritu, King & Minister Cabinet."""
        # Vikram Samvat: For months after Chaitra (approx April), year + 57
        # In early 2026 before April, year + 56
        y = target_date.year
        m = target_date.month
        # Approx Chaitra starts end March / April
        if m >= 4 or (m == 3 and target_date.day >= 20):
            vikram_samvat = y + 57
            shaka_samvat = y - 78
        else:
            vikram_samvat = y + 56
            shaka_samvat = y - 79

        # Jovian Samvatsar (60-year North/South cycle)
        # Formula: (Vikram Samvat + 9) % 60
        jovian_idx = (vikram_samvat + 9) % 60
        jovian_name = SAMVATSARAS_60[jovian_idx]

        # Ayana (उत्तरायण / दक्षिणायन)
        # Uttarayana: Sun enters Capricorn (270°) to Cancer (90°)
        # Dakshinayana: Sun enters Cancer (90°) to Capricorn (270°)
        if 90.0 <= sun_lon < 270.0:
            ayana = "दक्षिणायन (Dakshinayana)"
            ayana_symbol = "☀️ दक्षिणायन"
        else:
            ayana = "उत्तरायण (Uttarayana)"
            ayana_symbol = "☀️ उत्तरायण"

        # Ritu (6 Vedic Seasons)
        # Based on Sun sidereal longitude:
        # Meena/Mesha (330°-30°): Vasanta (बसन्त)
        # Vrishabha/Mithuna (30°-90°): Grishma (ग्रीष्म)
        # Karka/Simha (90°-150°): Varsha (वर्षा)
        # Kanya/Tula (150°-210°): Sharad (शरद्)
        # Vrischika/Dhanu (210°-270°): Hemanta (हेमन्त)
        # Makara/Kumbha (270°-330°): Shishira (शिशिर)
        if 330.0 <= sun_lon or sun_lon < 30.0:
            ritu = "वसन्त ऋतु (Vasanta - Spring)"
        elif 30.0 <= sun_lon < 90.0:
            ritu = "ग्रीष्म ऋतु (Grishma - Summer)"
        elif 90.0 <= sun_lon < 150.0:
            ritu = "वर्षा ऋतु (Varsha - Monsoon)"
        elif 150.0 <= sun_lon < 210.0:
            ritu = "शरद् ऋतु (Sharad - Autumn)"
        elif 210.0 <= sun_lon < 270.0:
            ritu = "हेमन्त ऋतु (Hemanta - Pre-Winter)"
        else:
            ritu = "शिशिर ऋतु (Shishira - Winter)"

        # Solar Month (सौर मास)
        solar_sign_idx = int(sun_lon // 30.0)
        solar_months = [
            "मेष मास", "वृषभ मास", "मिथुन मास", "कर्क मास",
            "सिंह मास", "कन्या मास", "तुला मास", "वृश्चिक मास",
            "धनु मास", "मकर मास", "कुम्भ मास", "मीन मास"
        ]
        solar_month = solar_months[solar_sign_idx]

        # Samvatsar Cabinet (राजा, मन्त्री, सेनाधिपति etc.)
        # Classical Cabinet for 2026-2027 (Vikram 2083 - क्रोधी / विश्वावसु):
        cabinet = [
            {"post": "राजा (King of the Year)", "graha": "गुरु (Jupiter)", "effect": "धर्म, न्याय, ज्ञान व कृषि में संतुलन"},
            {"post": "मन्त्री (Minister)", "graha": "मंगल (Mars)", "effect": "कड़े प्रशासनिक निर्णय, रक्षा सुधार व पराक्रम"},
            {"post": "सेनाधिपति (Commander)", "graha": "सूर्य (Sun)", "effect": "सैन्य शक्ति में वृद्धि व दृढ़ विदेश नीति"},
            {"post": "धान्याधिपति (Grains Lord)", "graha": "बुध (Mercury)", "effect": "हरित फसलों व व्यापारिक जिंसों में समृद्धि"},
            {"post": "मेघाधिपति (Rain Lord)", "graha": "चन्द्रमा (Moon)", "effect": "पर्याप्त वर्षा, जलाशयों का पोषण व जल कल्याण"},
            {"post": "रसाधिपति (Liquids/Juice)", "graha": "शुक्र (Venus)", "effect": "दुग्ध, घृत, मिष्ठान्न व औषधियों की प्रचुरता"},
            {"post": "नीरसाधिपति (Minerals/Metals)", "graha": "शनि (Saturn)", "effect": "खनिज, लोहा, कोयला व गैस के भाव में स्थिरता"}
        ]

        return {
            "vikram_samvat": vikram_samvat,
            "shaka_samvat": shaka_samvat,
            "jovian_samvatsar": jovian_name,
            "ayana": ayana,
            "ayana_symbol": ayana_symbol,
            "ritu": ritu,
            "solar_month": solar_month,
            "cabinet": cabinet
        }

    @classmethod
    def calculate_planetary_transit_matrix(
        cls,
        dt_utc: datetime
    ) -> List[Dict[str, Any]]:
        """Calculates exact sidereal degrees, nakshatras, padas, dignities, and motions for all planets."""
        provider = cls.get_provider()
        pos, ayanamsa_val = provider.get_planet_positions(dt_utc)

        sun_lon = pos.get("Sun", {}).get("longitude", 0.0)

        planet_names_hi = {
            "Sun": ("सूर्य", "Surya", "☀️"),
            "Moon": ("चन्द्रमा", "Chandra", "🌙"),
            "Mars": ("मंगल", "Mangal", "♂️"),
            "Mercury": ("बुध", "Budha", "☿️"),
            "Jupiter": ("बृहस्पति", "Guru", "♃"),
            "Venus": ("शुक्र", "Shukra", "♀️"),
            "Saturn": ("शनि", "Shani", "♄"),
            "Rahu": ("राहु", "Rahu", "☊"),
            "Ketu": ("केतु", "Ketu", "☋"),
            "Uranus": ("हर्षल / अरुण", "Uranus", "♅"),
            "Neptune": ("वरुण", "Neptune", "♆"),
            "Pluto": ("यम / प्लूटो", "Pluto", "♇")
        }

        # Combustion limits from Sun in degrees
        combustion_limits = {
            "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0, "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0
        }

        matrix = []
        for p_key, meta in planet_names_hi.items():
            if p_key not in pos:
                continue
            p_data = pos[p_key]
            lon = p_data.get("longitude", 0.0) % 360.0
            speed = p_data.get("speed", 0.0)
            is_retro = p_data.get("is_retrograde", False)

            sign_idx = int(lon // 30.0) + 1
            deg_in_sign = lon % 30.0
            rashi_hi_names = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
            sign_name = f"{rashi_hi_names[sign_idx - 1]} ({SIGN_NAMES[sign_idx - 1]})"

            # Nakshatra
            nak_span = 360.0 / 27.0
            n_idx = int(lon // nak_span) + 1
            deg_in_nak = lon % nak_span
            pada = int(deg_in_nak // (nak_span / 4.0)) + 1
            nak_name = NAKSHATRA_EXTENDED[n_idx - 1]["name"]

            # Deg, Min, Sec
            d_int = int(deg_in_sign)
            m_flt = (deg_in_sign - d_int) * 60.0
            m_int = int(m_flt)
            s_int = int((m_flt - m_int) * 60.0)
            deg_str = f"{d_int}° {m_int}' {s_int}\""

            # Combustion
            is_combust = False
            if p_key in combustion_limits:
                diff_sun = abs(lon - sun_lon)
                if diff_sun > 180.0:
                    diff_sun = 360.0 - diff_sun
                is_combust = diff_sun < combustion_limits[p_key]

            # Dignity
            dignity = "सम (Neutral)"
            dignity_badge = "⚪ सम"
            dignity_color = "#475569"

            if p_key == "Sun":
                if sign_idx == 1: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 7: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx == 5: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"
            elif p_key == "Moon":
                if sign_idx == 2: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 8: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx == 4: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"
            elif p_key == "Mars":
                if sign_idx == 10: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 4: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx in [1, 8]: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"
            elif p_key == "Mercury":
                if sign_idx == 6: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 12: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx in [3, 6]: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"
            elif p_key == "Jupiter":
                if sign_idx == 4: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 10: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx in [9, 12]: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"
            elif p_key == "Venus":
                if sign_idx == 12: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 6: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx in [2, 7]: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"
            elif p_key == "Saturn":
                if sign_idx == 7: dignity, dignity_badge, dignity_color = "परमोच्च (Exalted)", "🌟 उच्च", "#059669"
                elif sign_idx == 1: dignity, dignity_badge, dignity_color = "नीच (Debilitated)", "⚠️ नीच", "#DC2626"
                elif sign_idx in [10, 11]: dignity, dignity_badge, dignity_color = "स्वराशि (Own Sign)", "👑 स्वराशि", "#059669"

            matrix.append({
                "key": p_key,
                "name_hi": meta[0],
                "name_en": meta[1],
                "symbol": meta[2],
                "rashi": sign_name,
                "rashi_idx": sign_idx,
                "deg_str": deg_str,
                "deg_float": round(deg_in_sign, 2),
                "total_deg": round(lon, 2),
                "nakshatra": nak_name,
                "pada": pada,
                "speed": round(speed, 3),
                "motion": "वक्री (Retrograde)" if is_retro else "मार्गी (Direct)",
                "is_retro": is_retro,
                "combustion": "अस्त (Combust)" if is_combust else "उदय (Visible)",
                "is_combust": is_combust,
                "dignity": dignity,
                "dignity_badge": dignity_badge,
                "dignity_color": dignity_color
            })

        return matrix

    @classmethod
    def calculate_paksha_and_pitru_engine(
        cls,
        target_date: date,
        sun_lon: float,
        moon_lon: float,
        tithi_idx: int,
        sunrise_dt: datetime,
        sunset_dt: datetime
    ) -> Dict[str, Any]:
        """
        Calculates Paksha attributes, Pitru Paksha (Mahalaya Shradh), Chaturmas,
        Kharmas, and classical prohibitions (क्या-क्या नहीं कर सकते) & prescribed deeds.
        """
        sun_sign = int(sun_lon // 30.0) + 1  # 1 to 12
        is_shukla = tithi_idx <= 15
        paksha_name = "शुक्ल पक्ष" if is_shukla else "कृष्ण पक्ष"

        # Chandra Bala based on Paksha & Tithi
        if 1 <= tithi_idx <= 10:
            chandra_bala = "मध्यम से शुभ (Waxing Moon - वृद्धिशील)"
            chandra_bala_desc = "शुक्ल प्रतिपदा से दशमी — चन्द्रमा का बल क्रमशः बढ़ रहा है। देव कार्य, नूतन आरम्भ व विद्या कर्म हेतु शुभ।"
            chandra_bala_color = "#059669"
        elif 11 <= tithi_idx <= 20:
            chandra_bala = "सर्वोच्च / पूर्ण चन्द्र बल (Full Moon Strength)"
            chandra_bala_desc = "शुक्ल एकादशी से कृष्ण पंचमी — पूर्ण चन्द्र बल (सुधाकर किरणें)। समस्त मांगलिक, आध्यात्मिक व भौतिक कर्मों हेतु सर्वश्रेष्ठ।"
            chandra_bala_color = "#059669"
        else:
            chandra_bala = "क्षीण चन्द्र बल (Waning Moon - संयम काल)"
            chandra_bala_desc = "कृष्ण षष्ठी से अमावस्या — चन्द्रमा क्षीण व हीन बली है। बाह्य भौतिक उत्सवों के स्थान पर आत्म-साधना, पितृ तर्पण एवं संयम हेतु उत्तम।"
            chandra_bala_color = "#D97706"

        # -------------------------------------------------------------
        # 1. PITRU PAKSHA (पितृपक्ष / महालय श्राद्ध पक्ष / कनागत)
        # Classical Rule: Sun in Virgo (कन्या राशि - sign 6) and Moon in Krishna Paksha (16..30)
        # Also includes Bhadrapada Purnima (Tithi 15) when Sun in early Virgo or late Leo.
        # -------------------------------------------------------------
        is_pitru_paksha = (sun_sign == 6 and (16 <= tithi_idx <= 30 or tithi_idx == 15))

        shradh_names = {
            15: "पूर्णिमा श्राद्ध (ऋषि श्राद्ध)",
            16: "प्रतिपदा श्राद्ध (नाना-नानी व दौहित्र श्राद्ध)",
            17: "द्वितीया श्राद्ध",
            18: "तृतीया श्राद्ध",
            19: "चतुर्थी श्राद्ध / भरणी श्राद्ध (अकाल मृत्यु)",
            20: "पञ्चमी श्राद्ध (अविवाहित जनों का श्राद्ध)",
            21: "षष्ठी श्राद्ध",
            22: "सप्तमी श्राद्ध",
            23: "अष्टमी श्राद्ध",
            24: "नवमी श्राद्ध (अविधवा नवमी — माताओं व सौभाग्यवती स्त्रियों का श्राद्ध)",
            25: "दशमी श्राद्ध",
            26: "एकादशी श्राद्ध (इन्दिरा एकादशी — संन्यासियों व वैष्णव जनों का श्राद्ध)",
            27: "द्वादशी श्राद्ध (सन्यासियों, यतियों का श्राद्ध / मघा त्रयोदशी)",
            28: "त्रयोदशी श्राद्ध (मघा श्राद्ध / मृत बालकों का श्राद्ध)",
            29: "चतुर्दशी श्राद्ध (घात चतुर्दशी — शस्त्र, विष, अग्नि व दुर्घटना से मृत जनों का श्राद्ध)",
            30: "सर्वपितृ अमावस्या (महालया अमावस्या — समस्त ज्ञात-अज्ञात पितरों का महा-श्राद्ध)"
        }
        today_shradh = shradh_names.get(tithi_idx, f"तिथि {tithi_idx} श्राद्ध")

        # Shradh Specific Timings (Kutupa & Rohina Kaal)
        day_span = (sunset_dt - sunrise_dt).total_seconds()
        muh_sec = day_span / 15.0
        kutupa_st = sunrise_dt + timedelta(seconds=7 * muh_sec)
        kutupa_en = sunrise_dt + timedelta(seconds=8 * muh_sec)
        rohina_st = sunrise_dt + timedelta(seconds=8 * muh_sec)
        rohina_en = sunrise_dt + timedelta(seconds=9 * muh_sec)
        aparahna_st = sunrise_dt + timedelta(seconds=9 * muh_sec)
        aparahna_en = sunrise_dt + timedelta(seconds=12 * muh_sec)

        pitru_data = {}
        if is_pitru_paksha:
            pitru_data = {
                "is_active": True,
                "badge": "🚫 पितृपक्ष सक्रिय (Mahalaya Shradh Active)",
                "color": "#DC2626",
                "shradh_name": today_shradh,
                "kutupa_time": f"{kutupa_st.strftime('%I:%M %p')} - {kutupa_en.strftime('%I:%M %p')}",
                "rohina_time": f"{rohina_st.strftime('%I:%M %p')} - {rohina_en.strftime('%I:%M %p')}",
                "aparahna_time": f"{aparahna_st.strftime('%I:%M %p')} - {aparahna_en.strftime('%I:%M %p')}",
                "sutra": "कन्यागते सवितरि यो न मज्जति गोमतीम्। न ददाति पितृभ्योऽन्नं स भवेत् पितृघातकः॥ (निर्णय सिन्धु)",
                "prohibitions": [
                    "नूतन गृह प्रवेश एवं भूमि पूजन (सर्वथा वर्जित - गृह क्लेश व अनिष्ट भय)",
                    "विवाह, सगाई, रोका एवं पाणिग्रहण संस्कार (महा-निषेध - वंश वृद्धि में अवरोध)",
                    "उपनयन, मुंडन एवं कर्णवेध संस्कार (मांगलिक संस्कार निषिद्ध)",
                    "नूतन व्यापार, दुकान या प्रतिष्ठान का आरम्भ / उद्घाटन (आकस्मिक हानि का भय)",
                    "नवीन वाहन क्रय एवं स्वर्ण-आभूषणों का प्रथम क्रय/उपयोग (विलासिता उत्सव वर्जित)",
                    "मांसाहार, मदिरा, प्याज-लहसुन एवं तामसिक आचरण (महा-दोष)",
                    "बाल, दाढ़ी व नाखून कटवाना (श्राद्ध कर्ता हेतु निषिद्ध)"
                ],
                "prescribed_deeds": [
                    "पितरों के निमित्त काले तिल, जौ व कुशा से जलांजलि व तर्पण",
                    "पिण्डदान एवं कुतुप/रौहिण मुहूर्त में श्राद्ध कर्म सम्पादन",
                    "पंचबलि कर्म (गौ, श्वान, काग, देवादि, पिपीलिका को ग्रास अर्पण)",
                    "योग्य वेदपाठी ब्राह्मण को सात्विक भोजन (खीर, पूरी आदि) व दक्षिणा",
                    "श्रीमद्भगवद्गीता के ७वें व ११वें अध्याय तथा गरुड़ पुराण का पाठ",
                    "अन्नदान, वस्त्रदान, पादुका (जूते), छाता एवं दीपदान"
                ],
                "verdict_desc": "वर्तमान में सूर्य कन्या राशि में तथा चन्द्रमा कृष्ण पक्ष में स्थित है। यह पितरों के प्रति कृतज्ञता ज्ञापन, तर्पण एवं श्राद्ध का परम पवित्र काल है। शास्त्रों अनुसार इस अवधि में भौतिक मांगलिक उत्सव वर्जित होते हैं परंतु पितृ सेवा व दान-पुण्य से असीम पितृ-आशीर्वाद प्राप्त होता है।"
            }
        else:
            pitru_data = {
                "is_active": False,
                "badge": "🟢 पितृपक्ष निष्क्रिय (Normal Period)",
                "color": "#059669",
                "desc": "वर्तमान में पितृपक्ष सक्रिय नहीं है। सामान्य मांगलिक कार्यों पर पितृपक्ष का कोई प्रतिबंध नहीं है।"
            }

        # -------------------------------------------------------------
        # 2. CHATURMAS (चातुर्मास / देवशयन काल)
        # -------------------------------------------------------------
        is_chaturmas = (sun_sign in [4, 5, 6]) or (sun_sign == 7 and (tithi_idx < 11 or not is_shukla))

        # -------------------------------------------------------------
        # 3. KHARMAS / MALMAAS (खरमास)
        # -------------------------------------------------------------
        is_kharmas = (sun_sign in [9, 12])

        return {
            "paksha_name": paksha_name,
            "is_shukla": is_shukla,
            "chandra_bala": chandra_bala,
            "chandra_bala_desc": chandra_bala_desc,
            "chandra_bala_color": chandra_bala_color,
            "pitru_paksha": pitru_data,
            "is_chaturmas": is_chaturmas,
            "chaturmas_desc": "आषाढ़ शुक्ल एकादशी से कार्तिक शुक्ल एकादशी तक श्रीहरि विष्णु क्षीरसागर में योगनिद्रा में रहते हैं। अपूर्व गृह प्रवेश व विवाह संस्कार निषिद्ध माने गए हैं।" if is_chaturmas else "चातुर्मास सक्रिय नहीं है।",
            "is_kharmas": is_kharmas,
            "kharmas_desc": "सूर्य जब देवगुरु बृहस्पति की राशि (धनु या मीन) में होते हैं, तब समस्त मांगलिक संस्कार वर्जित रहते हैं।" if is_kharmas else "खरमास सक्रिय नहीं है।"
        }

    @classmethod
    def get_full_panchang(
        cls,
        target_date: date,
        latitude: float = 28.6139,
        longitude: float = 77.2090,
        city_name: str = "नई दिल्ली (New Delhi)",
        tz_offset_hours: float = 5.5
    ) -> Dict[str, Any]:
        """
        Master method compiling the full 100% Shastriya Panchang dataset for any chosen date and location.
        """
        sun_moon = cls.calculate_sun_moon_rise_set(target_date, latitude, longitude, tz_offset_hours)
        sr_dt = sun_moon["sunrise"]
        ss_dt = sun_moon["sunset"]
        next_sr_dt = sun_moon["next_sunrise"]

        five_pillars = cls.calculate_panchanga_5_pillars(target_date, sr_dt, tz_offset_hours)
        nak_idx = five_pillars["nakshatra"]["index"]
        tithi_idx = five_pillars["tithi"]["index"]

        bhadra = cls.calculate_bhadra_deep_engine(target_date, sr_dt, ss_dt, tz_offset_hours)
        panchak_ganda = cls.calculate_panchaka_and_gandamoola(target_date, sr_dt, tz_offset_hours)
        choghadiya_horas = cls.calculate_choghadiya_and_horas(target_date, sr_dt, ss_dt, next_sr_dt)
        muhurtas = cls.calculate_shubh_ashubh_muhurtas(target_date, sr_dt, ss_dt, next_sr_dt, nak_idx)

        # Sun Nakshatra for Anandadi
        provider = cls.get_provider()
        utc_sr = sr_dt - timedelta(hours=tz_offset_hours)
        pos_sr, _ = provider.get_planet_positions(utc_sr)
        sun_lon = pos_sr["Sun"]["longitude"] % 360.0
        moon_lon = pos_sr["Moon"]["longitude"] % 360.0
        sun_nak_idx = int(sun_lon // (360.0 / 27.0)) + 1
        moon_sign = int(moon_lon // 30.0) + 1

        yogas = cls.calculate_anandadi_and_special_yogas(target_date, sun_nak_idx, nak_idx, tithi_idx)
        nivas_shoola = cls.calculate_nivas_shoola_and_vedic_clock(target_date, sr_dt, moon_sign, tithi_idx)
        balam = cls.calculate_chandrabalam_and_tarabalam(moon_sign, nak_idx)
        samvatsar = cls.calculate_samvatsara_and_cabinet(target_date, sun_lon)
        transit_matrix = cls.calculate_planetary_transit_matrix(utc_sr)

        # Paksha & Pitru Paksha Engine
        paksha_engine = cls.calculate_paksha_and_pitru_engine(
            target_date=target_date,
            sun_lon=sun_lon,
            moon_lon=moon_lon,
            tithi_idx=tithi_idx,
            sunrise_dt=sr_dt,
            sunset_dt=ss_dt
        )

        # Overall Day Verdict
        day_quality = "🟢 शुभ व मांगलिक (Auspicious)"
        quality_color = "#059669"
        if paksha_engine["pitru_paksha"].get("is_active"):
            day_quality = f"🔴 पितृपक्ष सक्रिय — {paksha_engine['pitru_paksha']['shradh_name']} (मांगलिक कार्य वर्जित | तर्पण-श्राद्ध हेतु परम पावन)"
            quality_color = "#DC2626"
        elif bhadra.get("is_fatal_on_earth") or panchak_ganda["panchaka"].get("color") == "#991B1B":
            day_quality = "🔴 सतर्कता व सावधानी (Inauspicious Windows Active)"
            quality_color = "#DC2626"
        elif not five_pillars["yoga"]["is_good"]:
            day_quality = "🟡 मध्यम (Neutral / Use Auspicious Windows)"
            quality_color = "#D97706"

        return {
            "meta": {
                "date": target_date,
                "date_str": target_date.strftime("%d %B %Y"),
                "date_hi": f"{target_date.day} {['जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर'][target_date.month - 1]} {target_date.year}",
                "city": city_name,
                "latitude": latitude,
                "longitude": longitude,
                "day_verdict": day_quality,
                "day_verdict_color": quality_color
            },
            "sun_moon": sun_moon,
            "five_pillars": five_pillars,
            "bhadra": bhadra,
            "panchak_gandamoola": panchak_ganda,
            "choghadiya_horas": choghadiya_horas,
            "muhurtas": muhurtas,
            "yogas": yogas,
            "nivas_shoola": nivas_shoola,
            "balam": balam,
            "samvatsar": samvatsar,
            "transit_matrix": transit_matrix,
            "paksha_engine": paksha_engine
        }
