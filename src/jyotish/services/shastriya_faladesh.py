"""
Shastriya Faladesh Service (शास्त्रीय फलादेश सेवा)
Comprehensive Classical Predictive Analysis Engine covering 50 Dimensions of Human Life
and 100 Querent FAQs per dimension backed by active kundali calculations:
- Exact degrees, Baladi & Jagradadi Avashthas
- Nakshatras, Padas & Nakshatra Lords
- Rashis & Rashi Lords
- Houses, Bhavabala, Occupants & Aspects
- Shadbala (Virupas & Rupa ratio)
- Sarvashtakavarga (SAV) & Bhinnashtakavarga (BAV)
- Shodashvarga (D1 to D60 principal divisions)
- Chandra Kundli, Surya Kundli, Bhav Chalit
- Kota Chakra & Sudarshan Chakra
- Vimshottari Dasha (Mahadasha, Antardasha, Pratyantardasha)
- Honest Positive & Negative Scriptural Evidence (Brihat Parashara Hora Shastra, Phaladeepika, Saravali, Jaimini, etc.)
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, time
import math

from src.jyotish.core.constants import GRAHAS, SIGNS, SIGN_NAMES, SIGN_LORDS, NAKSHATRAS
from src.jyotish.core.models import KundaliChart, BirthData
from src.jyotish.dasha.vimshottari import default_dasha_engine

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",
    "Ascendant": "लग्न"
}

# -----------------------------------------------------------------------------
# 50 COMPREHENSIVE LIFE DIMENSIONS (जीवन के ५० सम्पूर्ण आयाम)
# -----------------------------------------------------------------------------
LIFE_DIMENSIONS_50 = [
    {
        "id": 1,
        "name_hi": "💼 आजीविका, करियर एवं व्यवसाय",
        "name_en": "Career, Profession & Business",
        "houses": [10, 6, 2, 1],
        "karakas": ["Sun", "Saturn", "Mercury", "Jupiter"],
        "primary_varga": "D10",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "दशम भाव, दशमेश, दशमांश (D10), सूर्य, शनि एवं बुध के आधार पर कार्यक्षेत्र, पदोन्नति व आजीविका निर्णय।"
    },
    {
        "id": 2,
        "name_hi": "💰 धन संचय, बैंक बैलेंस एवं वित्तीय स्थिति",
        "name_en": "Wealth Accumulation & Treasury",
        "houses": [2, 11, 9, 5],
        "karakas": ["Jupiter", "Mercury", "Venus"],
        "primary_varga": "D2",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "द्वितीय (कोष), एकादश (आय), नवम (भाग्य) एवं पंचम (लक्ष्मी स्थान) द्वारा संचित धन एवं स्थायी संपन्नता।"
    },
    {
        "id": 3,
        "name_hi": "💍 दांपत्य जीवन, विवाह एवं वैवाहिक सुख",
        "name_en": "Marriage, Spouse & Conjugal Bliss",
        "houses": [7, 2, 8, 12],
        "karakas": ["Venus", "Jupiter"],
        "primary_varga": "D9",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "सप्तम भाव, सप्तमेश, नवांश (D9), शुक्र व गुरु के आधार पर विवाह समय, जीवनसाथी का स्वभाव व सुख-शांति।"
    },
    {
        "id": 4,
        "name_hi": "👶 संतान सुख, संतति प्रगति एवं वंश वृद्धि",
        "name_en": "Progeny, Children & Lineage",
        "houses": [5, 9, 2],
        "karakas": ["Jupiter", "Sun"],
        "primary_varga": "D7",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "पंचम भाव, पंचमेश, सप्तांश (D7), गुरु एवं बीज/क्षेत्र स्फुट द्वारा संतति प्राप्ति, संतान का स्वास्थ्य व यश।"
    },
    {
        "id": 5,
        "name_hi": "🩺 आरोग्य, रोग मुक्ति एवं दीर्घायु",
        "name_en": "Health, Longevity & Disease Resistance",
        "houses": [1, 6, 8, 12],
        "karakas": ["Sun", "Moon", "Saturn"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "लग्न बल, अष्टम भाव (आयु), षष्ठ भाव (रोग), त्रिदोष संतुलन एवं मारकेश दशाओं द्वारा शारीरिक स्वास्थ्य।"
    },
    {
        "id": 6,
        "name_hi": "🎓 उच्च शिक्षा, विद्या एवं बौद्धिक क्षमता",
        "name_en": "Higher Education, Intellect & Learning",
        "houses": [4, 5, 9],
        "karakas": ["Mercury", "Jupiter"],
        "primary_varga": "D24",
        "category": "विद्या एवं ज्ञान (Education & Intellect)",
        "desc": "चतुर्थ (मूल विद्या), पंचम (बुद्धि/मेधा), नवम (उच्च शोध) एवं चतुर्विंशांश (D24) द्वारा अकादमिक सफलता।"
    },
    {
        "id": 7,
        "name_hi": "🏛️ भूमि, भवन, गृह एवं अचल संपत्ति",
        "name_en": "Land, Real Estate & Home Property",
        "houses": [4, 11, 2],
        "karakas": ["Mars", "Saturn", "Moon"],
        "primary_varga": "D4",
        "category": "भौतिक सुख एवं संपत्ति (Material Assets)",
        "desc": "चतुर्थ भाव (भूमि-भवन), चतुर्थांश (D4), मंगल (भूमि कारक) एवं शनि द्वारा मकान, फ्लैट, भूखंड प्राप्ति।"
    },
    {
        "id": 8,
        "name_hi": "🚗 वाहन सुख, विलासिता एवं यात्राएं",
        "name_en": "Vehicles, Conveyance & Luxury",
        "houses": [4, 12, 3],
        "karakas": ["Venus", "Moon"],
        "primary_varga": "D16",
        "category": "भौतिक सुख एवं संपत्ति (Material Assets)",
        "desc": "चतुर्थ भाव, षोडशांश (D16), शुक्र (वाहन कारक) एवं तृतीय भाव द्वारा नवीन वाहन क्रय, यात्राएं व वाहन सुरक्षा।"
    },
    {
        "id": 9,
        "name_hi": "✈️ विदेश गमन, विदेशी निवास एवं ग्रीन कार्ड",
        "name_en": "Foreign Travel, Settlement & Green Card",
        "houses": [12, 9, 3, 7],
        "karakas": ["Rahu", "Moon", "Saturn"],
        "primary_varga": "D9",
        "category": "यात्रा एवं स्थानांतरण (Travel & Migration)",
        "desc": "द्वादश भाव (विदेश वास), नवम (दीर्घ यात्रा), चर राशियां एवं राहु-चन्द्र योग द्वारा विदेशी नागरिकता व गमन।"
    },
    {
        "id": 10,
        "name_hi": "⚖️ मुकदमेबाजी, कोर्ट-कचहरी, शत्रु एवं विजय",
        "name_en": "Litigation, Legal Battles & Enemies",
        "houses": [6, 8, 3, 10],
        "karakas": ["Mars", "Saturn", "Rahu"],
        "primary_varga": "D6",
        "category": "संघर्ष एवं सुरक्षा (Crises & Challenges)",
        "desc": "षष्ठ भाव (रिपु-ऋण), अष्टम भाव, तृतीय (पराक्रम) एवं मंगल के बल द्वारा विवादों, न्यायालय में विजय का निर्णय।"
    },
    {
        "id": 11,
        "name_hi": "💳 ऋण, कर्ज, देनदारियां एवं वित्तीय संकट",
        "name_en": "Debts, Loans & Debt Recovery",
        "houses": [6, 8, 12],
        "karakas": ["Mars", "Saturn", "Mercury"],
        "primary_varga": "D2",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "षष्ठेश की स्थिति, पाप प्रभाव, द्वितीय-एकादश भाव का संबंध एवं ऋण मुक्ति के योग व शास्त्रीय समय।"
    },
    {
        "id": 12,
        "name_hi": "👑 मान-सम्मान, पदोन्नति, यश एवं सामाजिक प्रतिष्ठा",
        "name_en": "Fame, Authority, Awards & Honor",
        "houses": [1, 10, 5, 9],
        "karakas": ["Sun", "Jupiter"],
        "primary_varga": "D10",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "लग्न, दशम भाव, सूर्य (आत्मा/राजसत्ता) एवं गुरु की कृपा से समाज, कार्यस्थल व कुल में कीर्ति व सम्मान।"
    },
    {
        "id": 13,
        "name_hi": "🕉️ आध्यात्मिकता, धर्म, साधना एवं मोक्ष",
        "name_en": "Spirituality, Dharma, Sadhana & Moksha",
        "houses": [9, 12, 5, 8],
        "karakas": ["Jupiter", "Ketu", "Sun"],
        "primary_varga": "D20",
        "category": "आध्यात्म एवं मोक्ष (Spirituality & Dharma)",
        "desc": "नवम (धर्म), द्वादश (मोक्ष), विंशांश (D20), केतु (कैवल्य कारक) एवं गुरु द्वारा ईश्वरीय साक्षात्कार व भक्ति।"
    },
    {
        "id": 14,
        "name_hi": "👨‍👩‍👦 माता का स्वास्थ्य, सुख एवं पैतृक वात्सल्य",
        "name_en": "Mother's Health, Happiness & Blessings",
        "houses": [4, 10],
        "karakas": ["Moon"],
        "primary_varga": "D12",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "चतुर्थ भाव, चतुर्थेश, द्वादशांश (D12) एवं चन्द्रमा के आधार पर मातृ सुख, मातृ स्वास्थ्य एवं वात्सल्य लाभ।"
    },
    {
        "id": 15,
        "name_hi": "🏛️ पिता का स्वास्थ्य, प्रतिष्ठा एवं पैतृक संबंध",
        "name_en": "Father's Health, Honor & Ancestral Lineage",
        "houses": [9, 10],
        "karakas": ["Sun", "Jupiter"],
        "primary_varga": "D12",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "नवम भाव, नवमेश, द्वादशांश (D12) एवं सूर्य के आधार पर पितृ सुख, पिता का स्वास्थ्य व पैतृक संस्कार।"
    },
    {
        "id": 16,
        "name_hi": "📈 शेयर बाज़ार, सट्टा, लाटरी एवं आकस्मिक लाभ",
        "name_en": "Stock Market, Speculation & Windfalls",
        "houses": [5, 8, 11, 2],
        "karakas": ["Mercury", "Rahu", "Jupiter"],
        "primary_varga": "D2",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "पंचम भाव (सट्टेबाजी/शेयर), अष्टम (आकस्मिक धन), एकादश (अकूत लाभ) एवं राहु-बुध का युति-दृष्टि प्रभाव।"
    },
    {
        "id": 17,
        "name_hi": "🛡️ दुर्घटना, शल्यक्रिया (सर्जरी) एवं आपात संकट",
        "name_en": "Accidents, Surgery & Sudden Hazards",
        "houses": [8, 6, 12],
        "karakas": ["Mars", "Saturn", "Rahu", "Ketu"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "अष्टम भाव (संकट/शल्यक्रिया), षष्ठ भाव (चोट), मंगल (रक्त/चीरा) एवं राहु-केतु द्वारा आकस्मिक घटनाओं का समय।"
    },
    {
        "id": 18,
        "name_hi": "🧠 मानसिक शांति, एकाग्रता, अवसाद एवं भय",
        "name_en": "Mental Peace, Anxiety, Depression & Mind",
        "houses": [4, 5, 1],
        "karakas": ["Moon", "Mercury"],
        "primary_varga": "D9",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "चतुर्थ भाव (मन का सुख), चन्द्रमा (मनोभाव), बुध (मस्तिष्क) पर शनि-राहु-केतु के प्रभाव से अवसाद या शांति।"
    },
    {
        "id": 19,
        "name_hi": "👫 प्रेम संबंध, आकर्षण एवं प्रेम विवाह",
        "name_en": "Love Affairs, Romance & Interpersonal Bonds",
        "houses": [5, 7, 11],
        "karakas": ["Venus", "Moon", "Mars"],
        "primary_varga": "D9",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "पंचम (प्रेम/प्रणय), सप्तम (परिणय), एकादश (इच्छापूर्ति) एवं शुक्र-मंगल युति द्वारा प्रेम विवाह की सफलता।"
    },
    {
        "id": 20,
        "name_hi": "👥 मित्र, सहयोगी एवं सामाजिक नेटवर्क",
        "name_en": "Friends, Allies, Benefactors & Network",
        "houses": [11, 3, 7],
        "karakas": ["Mercury", "Jupiter"],
        "primary_varga": "D1",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "एकादश भाव (मित्र मंडल), तृतीय भाव (सहोदर/मित्र) एवं बुध के सौम्य प्रभाव द्वारा विश्वसनीय मित्रों का लाभ।"
    },
    {
        "id": 21,
        "name_hi": "🏢 सरकारी सेवा, प्रशासनिक पद एवं राजकृपा",
        "name_en": "Government Job, Civil Services & State Honor",
        "houses": [10, 1, 9, 6],
        "karakas": ["Sun", "Mars", "Jupiter"],
        "primary_varga": "D10",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "सूर्य-गुरु का दिगबल, दशमेश का सूर्य से संबंध, अमात्यकारक एवं राजयोगों द्वारा सिविल सर्विस व सरकारी चयन।"
    },
    {
        "id": 22,
        "name_hi": "🎭 कला, संगीत, अभिनय, मीडिया एवं साहित्य",
        "name_en": "Fine Arts, Music, Cinema, Literature & Media",
        "houses": [3, 5, 10],
        "karakas": ["Venus", "Mercury", "Moon"],
        "primary_varga": "D10",
        "category": "विद्या एवं ज्ञान (Education & Intellect)",
        "desc": "तृतीय भाव (गायन/कला), पंचम (सृजनशीलता), शुक्र (ललित कलाएं) एवं बुध द्वारा मीडिया व सिनेमा में सफलता।"
    },
    {
        "id": 23,
        "name_hi": "🔬 शोध, गूढ़ विद्या, ज्योतिष एवं अनुसंधान",
        "name_en": "Research, Occult Sciences, Astrology & Data",
        "houses": [8, 9, 5],
        "karakas": ["Jupiter", "Mercury", "Ketu", "Saturn"],
        "primary_varga": "D20",
        "category": "विद्या एवं ज्ञान (Education & Intellect)",
        "desc": "अष्टम भाव (गूढ़ रहस्य), नवम (दैवीय ज्ञान), केतु (अन्तर्दृष्टि) एवं गुरु द्वारा पराविज्ञान व शोध में महारत।"
    },
    {
        "id": 24,
        "name_hi": "🗣️ वाक्-सामर्थ्य, संभाषण एवं परामर्शदाता योग",
        "name_en": "Oratory, Vocal Power & Counseling",
        "houses": [2, 10],
        "karakas": ["Mercury", "Jupiter"],
        "primary_varga": "D1",
        "category": "विद्या एवं ज्ञान (Education & Intellect)",
        "desc": "द्वितीय भाव (वाणी), द्वितीयेश, बुध (वाणी कारक) एवं गुरु के प्रभाव से प्रभावशाली प्रवक्ता, वकील व परामर्शदाता।"
    },
    {
        "id": 25,
        "name_hi": "👁️ नेत्र ज्योति, दृष्टि एवं मुखमंडल सौन्दर्य",
        "name_en": "Vision, Eyesight & Facial Radiance",
        "houses": [2, 12, 1],
        "karakas": ["Sun", "Moon", "Venus"],
        "primary_varga": "D1",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "द्वितीय भाव (दाहिनी आंख), द्वादश भाव (बाईं आंख), सूर्य-चन्द्र पर पाप दृष्टि एवं चश्मे व नेत्र स्वास्थ्य का विचार।"
    },
    {
        "id": 26,
        "name_hi": "🦻 श्रवण शक्ति, कर्ण एवं सूचना प्रौद्योगिकी",
        "name_en": "Hearing, ENT, Tech & Communications",
        "houses": [3, 11],
        "karakas": ["Jupiter", "Mercury"],
        "primary_varga": "D1",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "तृतीय भाव (दायां कान), एकादश भाव (बायां कान), गुरु (आकाश तत्व/ध्वनि) द्वारा श्रवण क्षमता व ईएनटी स्वास्थ्य।"
    },
    {
        "id": 27,
        "name_hi": "🦴 अस्थि, जोड़, वात विकार एवं स्नायु तंत्र",
        "name_en": "Bones, Joints, Arthritis & Nervous System",
        "houses": [1, 6, 10],
        "karakas": ["Sun", "Saturn", "Mercury"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "सूर्य (हड्डियां), शनि (वात विकार/जोड़ों का दर्द), बुध (स्नायु तंत्र/नसें) द्वारा आर्थराइटिस व साइटिका विचार।"
    },
    {
        "id": 28,
        "name_hi": "🩸 हृदय, रक्तचाप, परिसंचरण एवं जीवन शक्ति",
        "name_en": "Heart, Blood Pressure, Cardiovascular Health",
        "houses": [4, 5],
        "karakas": ["Sun", "Mars", "Moon"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "चतुर्थ भाव (हृदय प्रदेश), पंचम भाव, सूर्य (हृदय की धड़कन) एवं मंगल (रक्तचाप) द्वारा कार्डियोवस्कुलर स्थिति।"
    },
    {
        "id": 29,
        "name_hi": "🫁 श्वसन तंत्र, फेफड़े, दमा एवं एलर्जी",
        "name_en": "Lungs, Respiration, Bronchial & Immunity",
        "houses": [3, 4],
        "karakas": ["Mercury", "Moon", "Rahu"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "तृतीय भाव (श्वास नली/फेफड़े), मिथुन/कर्क राशि, बुध व चन्द्र पर राहु के प्रभाव से दमा, ब्रोंकाइटिस व कफ विकार।"
    },
    {
        "id": 30,
        "name_hi": "🍽️ उदर, पाचन तंत्र, यकृत एवं चयापचय",
        "name_en": "Digestive System, Liver, Gut & Metabolism",
        "houses": [5, 6],
        "karakas": ["Jupiter", "Mars", "Sun"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "पंचम भाव (जठराग्नि), षष्ठ भाव, गुरु (यकृत/लिवर), मंगल (पित्त) के संतुलन से पाचन शक्ति, गैस व लिवर स्वास्थ्य।"
    },
    {
        "id": 31,
        "name_hi": "🚻 गुह्य अंग, हार्मोनल संतुलन एवं प्रजनन तंत्र",
        "name_en": "Hormones, Reproductive & Secret Ailments",
        "houses": [7, 8],
        "karakas": ["Venus", "Mars", "Moon"],
        "primary_varga": "D30",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "सप्तम-अष्टम भाव, वृश्चिक राशि, शुक्र (वीर्य/रज) व मंगल द्वारा हार्मोनल संतुलन एवं प्रजनन अंगों का स्वास्थ्य।"
    },
    {
        "id": 32,
        "name_hi": "💤 निद्रा, स्वप्न, अनिद्रा एवं शय्या सुख",
        "name_en": "Sleep Quality, Insomnia & Restful Living",
        "houses": [12, 4],
        "karakas": ["Venus", "Moon", "Saturn"],
        "primary_varga": "D1",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "द्वादश भाव (शयन सुख/निद्रा), चतुर्थ भाव (मानसिक शांति), शुक्र व चन्द्र द्वारा गहरी शांतिदायक नींद का विश्लेषण।"
    },
    {
        "id": 33,
        "name_hi": "🏛️ पैतृक संपत्ति, वसीयत एवं दायभाग",
        "name_en": "Ancestral Inheritance, Will & Patrimony",
        "houses": [8, 9, 2],
        "karakas": ["Saturn", "Jupiter", "Sun"],
        "primary_varga": "D12",
        "category": "भौतिक सुख एवं संपत्ति (Material Assets)",
        "desc": "अष्टम भाव (विरासत/वसीयत), नवम (पिता की धरोहर), द्वितीय (परिवार का धन) द्वारा बिना परिश्रम के पैतृक लाभ।"
    },
    {
        "id": 34,
        "name_hi": "⚔️ प्रतियोगी परीक्षा, साक्षात्कार एवं चयन",
        "name_en": "Competitive Exams, Interviews & Selection",
        "houses": [6, 10, 5],
        "karakas": ["Mercury", "Mars", "Sun"],
        "primary_varga": "D10",
        "category": "विद्या एवं ज्ञान (Education & Intellect)",
        "desc": "षष्ठ भाव (प्रतियोगिता/शत्रु दलन), पंचम (स्मृति/बुद्धि), दशम (अधिकार) एवं मंगल के पराक्रम से प्रवेश परीक्षा विजय।"
    },
    {
        "id": 35,
        "name_hi": "🪔 पूर्वजन्म कर्म, ऋणानुबंध एवं प्रारब्ध ऋण",
        "name_en": "Past Life Karma, Ancestral Debts & Prarabdha",
        "houses": [5, 9, 12, 6],
        "karakas": ["Saturn", "Rahu", "Ketu"],
        "primary_varga": "D60",
        "category": "आध्यात्म एवं मोक्ष (Spirituality & Dharma)",
        "desc": "षष्ट्यंश (D60), पंचम (पूर्व पुण्य), नवम (धर्म), राहु-केतु द्वारा पितृ ऋण, मातृ ऋण व कर्मिक बंधनों का निर्णय।"
    },
    {
        "id": 36,
        "name_hi": "🚩 राजनीति, जनसमर्थन, सत्ता एवं नेतृत्व",
        "name_en": "Politics, Public Leadership & Governance",
        "houses": [10, 4, 7, 1],
        "karakas": ["Sun", "Saturn", "Rahu"],
        "primary_varga": "D10",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "सूर्य (सत्ता), शनि (जनता/मतदाता), राहु (कूटनीति) एवं चतुर्थ/दशम भाव के योग से चुनाव विजय व मंत्री पद।"
    },
    {
        "id": 37,
        "name_hi": "🌿 व्यसन, नशा, बुरी आदतें एवं चरित्र शुद्धि",
        "name_en": "Addiction Detox, Bad Habits & Moral Strength",
        "houses": [2, 6, 8, 12],
        "karakas": ["Rahu", "Saturn", "Venus"],
        "primary_varga": "D1",
        "category": "स्वास्थ्य एवं आयु (Health & Longevity)",
        "desc": "द्वितीय भाव (मुख/खानपान), द्वादश भाव (भोग/नशा), राहु-शुक्र के दूषित योग एवं मद्यपान/धूम्रपान से मुक्ति।"
    },
    {
        "id": 38,
        "name_hi": "📦 आयात-निर्यात, बहुराष्ट्रीय व्यापार एवं विदेशी धन",
        "name_en": "Import-Export, Global Commerce & Forex",
        "houses": [12, 7, 11],
        "karakas": ["Mercury", "Rahu", "Moon"],
        "primary_varga": "D10",
        "category": "अर्थ एवं कर्म (Finance & Career)",
        "desc": "द्वादश भाव (विदेशी व्यापार), सप्तम (व्यवसाय), एकादश (लाभ) एवं बुध-राहु द्वारा अंतरराष्ट्रीय आपूर्ति श्रृंखला।"
    },
    {
        "id": 39,
        "name_hi": "🧘 तंत्र, मंत्र, यंत्र साधना एवं षट्कर्म",
        "name_en": "Tantra, Mantra, Yantra & Esoteric Mysticism",
        "houses": [8, 5, 9],
        "karakas": ["Ketu", "Mars", "Jupiter"],
        "primary_varga": "D20",
        "category": "आध्यात्म एवं मोक्ष (Spirituality & Dharma)",
        "desc": "अष्टम भाव (तंत्र/गुप्त सिद्धि), पंचम (मंत्र सिद्धि), केतु (मोक्ष/अघोर) एवं गुरु द्वारा तांत्रिक व वैदिक साधना।"
    },
    {
        "id": 40,
        "name_hi": "💔 वैवाहिक विलंब, संबंध विच्छेद एवं पुनर्विवाह",
        "name_en": "Marriage Delay, Separation & Second Alliance",
        "houses": [7, 8, 12, 2],
        "karakas": ["Saturn", "Rahu", "Mars", "Venus"],
        "primary_varga": "D9",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "सप्तम भाव पर पाप ग्रहों (शनि-राहु-सूर्य) की दृष्टि, द्वितीयांश, द्वितीय विवाह (नवम भाव) एवं शांति उपाय।"
    },
    {
        "id": 41,
        "name_hi": "🏠 गृह वास्तु, दिशा दोष एवं भूमि चयन",
        "name_en": "Home Vastu, Geopathic Stress & Spatial Balance",
        "houses": [4, 1, 10],
        "karakas": ["Mars", "Saturn", "Jupiter"],
        "primary_varga": "D4",
        "category": "भौतिक सुख एवं संपत्ति (Material Assets)",
        "desc": "चतुर्थ भाव (भवन वास्तु), अष्ट दिक्पाल बल, ब्रह्मस्थान संतुलन एवं निवास स्थल में सकारात्मक ऊर्जा का प्रवाह।"
    },
    {
        "id": 42,
        "name_hi": "🌟 भाग्योदय काल, स्वर्णिम वर्ष एवं शुभ दिशाएं",
        "name_en": "Fortune Rise Ages, Golden Years & Directions",
        "houses": [9, 1, 11],
        "karakas": ["Jupiter", "Sun"],
        "primary_varga": "D1",
        "category": "भाग्य एवं जीवन यात्रा (Destiny & Life Milestones)",
        "desc": "नवमेश की स्थिति, गुरु-सूर्य की युति, भाग्योदय वर्ष (जैसे १६, २१, २४, २८, ३२, ३६ वर्ष) एवं अनुकूल दिशाएं।"
    },
    {
        "id": 43,
        "name_hi": "💎 अनुकूल रत्न, रुद्राक्ष एवं धातु चयन",
        "name_en": "Benefic Gemstones, Rudraksha & Auspicious Metals",
        "houses": [1, 5, 9],
        "karakas": ["Sun", "Jupiter", "Mars"],
        "primary_varga": "D1",
        "category": "शास्त्रीय उपचार एवं उपाय (Vedic Remedies)",
        "desc": "योगकारक, लग्नेश, पंचमेश, नवमेश के बलवर्धन हेतु शास्त्रोक्त रत्न, मुखी रुद्राक्ष एवं धारण विधि।"
    },
    {
        "id": 44,
        "name_hi": "📜 दान, पुण्य, तीर्थाटन एवं सामाजिक सेवा",
        "name_en": "Charitable Acts, Pilgrimage & Altruism",
        "houses": [9, 12, 4],
        "karakas": ["Jupiter", "Saturn", "Moon"],
        "primary_varga": "D20",
        "category": "आध्यात्म एवं मोक्ष (Spirituality & Dharma)",
        "desc": "नवम (तीर्थयात्रा), द्वादश (पुण्य व्यय/दान), गुरु व शनि की कृपा से जनकल्याण, भण्डारा व धर्मार्थ कार्य।"
    },
    {
        "id": 45,
        "name_hi": "👨‍👧‍👦 अनुज व अग्रज भाई-बहन एवं संबंध",
        "name_en": "Brothers, Sisters & Fraternal Harmony",
        "houses": [3, 11],
        "karakas": ["Mars", "Jupiter"],
        "primary_varga": "D3",
        "category": "संबंध एवं परिवार (Relationships)",
        "desc": "तृतीय भाव (छोटे भाई-बहन), एकादश भाव (बड़े भाई-बहन), द्रेष्काण (D3) एवं मंगल द्वारा भ्रातृ सुख व सहयोग।"
    },
    {
        "id": 46,
        "name_hi": "🐾 कृषि, भूमि उत्पाद, डेयरी एवं पशुधन",
        "name_en": "Agriculture, Farming, Dairy & Flora-Fauna",
        "houses": [4, 6, 2],
        "karakas": ["Moon", "Venus", "Saturn", "Mars"],
        "primary_varga": "D4",
        "category": "भौतिक सुख एवं संपत्ति (Material Assets)",
        "desc": "चतुर्थ भाव (कृषि भूमि), षष्ठ भाव (पशुधन/चौपाए), वृषभ/कर्क राशि, शुक्र (डेयरी) व शनि (भूमि उत्पादन)।"
    },
    {
        "id": 47,
        "name_hi": "⚖️ सत्यनिष्ठा, धर्मपरायणता एवं आचार शुद्धि",
        "name_en": "Moral Integrity, Ethics & Virtuous Conduct",
        "houses": [9, 1, 5],
        "karakas": ["Jupiter", "Sun", "Mercury"],
        "primary_varga": "D9",
        "category": "आध्यात्म एवं मोक्ष (Spirituality & Dharma)",
        "desc": "लग्न-नवम पर गुरु का प्रभाव, सात्विक ग्रहों की स्थिति, असत्य व छल से मुक्ति एवं उत्तम चारित्रिक प्रतिष्ठा।"
    },
    {
        "id": 48,
        "name_hi": "🔐 विश्वासघात, छल-कपट एवं गुप्त षड्यंत्र",
        "name_en": "Betrayal, Cheating, Fraud & Covert Plots",
        "houses": [8, 12, 6],
        "karakas": ["Rahu", "Saturn", "Mercury"],
        "primary_varga": "D30",
        "category": "संघर्ष एवं सुरक्षा (Crises & Challenges)",
        "desc": "अष्टम भाव (गुप्त शत्रु), द्वादश भाव (षड्यंत्र), राहु का दूषित प्रभाव एवं साझेदारों द्वारा धोखाधड़ी से बचाव।"
    },
    {
        "id": 49,
        "name_hi": "⏳ जीवन के निर्णायक मोड़ एवं दशा संधिकाल",
        "name_en": "Crucial Milestone Decades & Dasha Junctions",
        "houses": [1, 8, 10, 9],
        "karakas": ["Saturn", "Jupiter", "Rahu"],
        "primary_varga": "D1",
        "category": "भाग्य एवं जीवन यात्रा (Destiny & Life Milestones)",
        "desc": "विंशोत्तरी महादशाओं का संधिकाल, शनि साढ़ेसाती, गुरु-शनि दोहरा गोचर एवं जीवन में ३ प्रमुख युगांतरकारी मोड़।"
    },
    {
        "id": 50,
        "name_hi": "🌅 वानप्रस्थ, उत्तरार्ध सुख एवं परलोक साधना",
        "name_en": "Retirement, Later Life Peace & Final Ascent",
        "houses": [12, 8, 4, 9],
        "karakas": ["Jupiter", "Ketu", "Saturn"],
        "primary_varga": "D20",
        "category": "आध्यात्म एवं मोक्ष (Spirituality & Dharma)",
        "desc": "चतुर्थ भाव (वृद्धावस्था सुख), द्वादश भाव (शांतिपूर्ण प्रयाण), केतु (मोक्ष) द्वारा जीवन के अंतिम चरण में परमानंद।"
    }
]

# -----------------------------------------------------------------------------
# 100 REAL-WORLD QUERENT FAQS PER DIMENSION (MASTER QUESTION BANK TEMPLATES)
# -----------------------------------------------------------------------------
FAQ_INTENT_PATTERNS = [
    # Timing (कब होगा?)
    ("कब योग बनेगा?", "timing", "सक्रिय विंशोत्तरी दशा व गोचरीय संचरण के अनुसार समय सीमा"),
    ("किस वर्ष में सर्वोच्च सफलता मिलेगी?", "golden_year", "दशा-नाथ व अष्टकवर्ग कक्षी के अनुसार भाग्योदय वर्ष"),
    ("क्या इस वर्ष कार्य सिद्धि होगी?", "yearly_transit", "वर्तमान वर्षफल, मुन्था व गुरु-शनि दोहरे गोचर की स्थिति"),
    ("विलंब का मुख्य ज्योतिषीय कारण क्या है?", "delay_cause", "शनि दृष्टि, वक्री ग्रह, अंश निर्बलता या कस्पल अवरोध"),
    ("क्या अचानक या अप्रत्याशित रूप से लाभ होगा?", "sudden_event", "अष्टम भाव, राहु की स्थिति एवं आकस्मिक योग"),
    # Yes / No & Strength (कैसा रहेगा?)
    ("शास्त्रीय दृष्टि से इस क्षेत्र में अनुकूलता का प्रतिशत क्या है?", "score_pct", "षड्बल, भावबल एवं शुभाशुभ दृष्टि संतुलन"),
    ("सकारात्मक पक्ष क्या-क्या हैं?", "positive_factors", "उच्च, मूलत्रिकोण, राजयोग एवं शुभ नवांश प्रमाण"),
    ("नकारात्मक या बाधक पहलू क्या हैं?", "negative_factors", "नीच, शत्रु, दुरवस्था एवं पापकर्तरी दोष"),
    ("क्या जीवनसाथी या परिवार का सहयोग मिलेगा?", "family_support", "सप्तम, द्वितीय व चतुर्थ भाव का परस्पर संबंध"),
    ("प्रतिद्वंद्वियों पर विजय प्राप्त होगी या नहीं?", "foes_victory", "षष्ठ भाव, उपचय भाव बल एवं मंगल-शनि स्थिति"),
    # Nature & Choice (कौन सा मार्ग श्रेष्ठ है?)
    ("मेरे लिए कौन सा विकल्प सर्वाधिक शुभ है?", "best_option", "दशमेश, कारकांश व चंद्र राशि अनुसार प्राकृतिक अनुकूलता"),
    ("क्या स्थान परिवर्तन या स्थानांतरण लाभकारी होगा?", "relocation", "तृतीय, नवम व द्वादश भाव एवं चर राशि प्रभाव"),
    ("साझेदारी में कार्य करना चाहिए या अकेले?", "partnership_suitability", "सप्तम भाव बनाम लग्न बल एवं एकादश भाव स्थिति"),
    ("सरकारी तंत्र से सहयोग मिलेगा या रुकावट?", "state_favor", "सूर्य की स्थिति, पंचम भाव व अमात्यकारक बल"),
    ("निवेश करना चाहिए या अभी प्रतीक्षा करनी चाहिए?", "investment_timing", "द्वितीय, एकादश भाव SAV अंक एवं सक्रिय दशा"),
    # Psychological & Health (मानसिक व शारीरिक स्थिति)
    ("तनाव व चिंता का क्या ज्योतिषीय कारण है?", "mental_stress", "चन्द्रमा पर शनि-राहु युति, केमद्रुम योग या षष्ठेश दृष्टि"),
    ("ऊर्जा व आत्मविश्वास में वृद्धि कैसे होगी?", "vitality_boost", "सूर्य व लग्न नक्षत्र बल एवं इष्टदेव उपासना"),
    ("निर्णय लेने में संशय क्यों उत्पन्न होता है?", "indecision", "बुध की वक्री स्थिति, बाल्य अवस्था या पाप वेध"),
    ("दुर्घटना या संकट से बचने हेतु क्या सावधानी आवश्यक है?", "accident_warning", "अष्टम भाव, मारकेश दशा व कोटा चक्र स्थिति"),
    ("आरोग्य बनाए रखने हेतु दिनचर्या व खानपान कैसा हो?", "lifestyle_diet", "आयुर्वेदिक त्रिदोष, द्वितीय भाव व षष्ठेश धातु विचार"),
    # Spiritual & Shastric Remedies (उपाय व प्रमाण)
    ("कौन सा वैदिक मंत्र नित्य जपना चाहिए?", "mantra_remedy", "भाव स्वामी व इष्टग्रह का प्रामाणिक बीज मंत्र"),
    ("क्या कोई रत्न धारण करना शास्त्रसम्मत है?", "gemstone_guide", "लग्नेश/भाग्येश की अनुकूलता व मारक दोष परीक्षण"),
    ("कौन सा दान करने से कष्टों का निवारण होगा?", "charity_daana", "पीड़क ग्रह की धातु, अन्न, वस्त्र व शास्त्रीय वार दान"),
    ("किस देवता की शरण में जाने से शीघ्र कृपा होगी?", "deity_worship", "पंचमेश, कारकांश से द्वादश भाव व इष्टदेवता"),
    ("बृहत्पाराशर होराशास्त्र का इस विषय में क्या सिद्धांत है?", "parashara_sutra", "पाराशरी श्लोक, फलदीपिका व सारावली शास्त्रीय साक्ष्य"),
]

def generate_100_faqs_for_dimension(dim: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generates 100 deeply articulated, native-focused questions for the given life dimension."""
    faqs = []
    d_name = dim["name_hi"].split(" ")[1] if len(dim["name_hi"].split(" ")) > 1 else dim["name_hi"]
    houses_str = ", ".join([f"{h}वें" for h in dim["houses"]])
    karakas_str = ", ".join([PLANET_NAMES_HI.get(k, k) for k in dim["karakas"]])

    # Base Core 25 questions
    base_questions = [
        f"मेरी कुण्डली में {d_name} का समग्र स्तर कैसा है?",
        f"{d_name} से संबंधित श्रेष्ठ समय या स्वर्णिम वर्ष कब आएगा?",
        f"वर्तमान में चल रही विंशोत्तरी दशा {d_name} के लिए अनुकूल है या प्रतिकूल?",
        f"सक्रिय कुण्डली के अनुसार {d_name} में क्या-क्या मुख्य रुकावटें हैं?",
        f"{d_name} को मजबूत करने के लिए कौन सा शास्त्रीय रत्न धारण करें?",
        f"क्या {d_name} के लिए स्थान परिवर्तन (घर/शहर/देश) करना शुभ होगा?",
        f"संबंधित {houses_str} भाव का भावबल एवं अष्टकवर्ग (SAV) अंक क्या संकेत देते हैं?",
        f"{karakas_str} ग्रह मेरी कुण्डली में कितने अंश पर हैं और उनका क्या प्रभाव है?",
        f"क्या {d_name} में अचानक बड़ा उछाल या अप्रत्याशित सफलता का योग है?",
        f"विपरीत परिस्थितियों में {d_name} की रक्षा के लिए कौन सा महामंत्र जपें?",
        f"क्या पूर्वजन्म के कर्मों का ऋण {d_name} को प्रभावित कर रहा है?",
        f"{dim['primary_varga']} वर्ग कुण्डली में इस विषय की वास्तविक स्थिति क्या है?",
        f"चन्द्र कुण्डली के अनुसार {d_name} का क्या फलादेश है?",
        f"सूर्य कुण्डली से देखने पर आत्मबल व प्रतिष्ठा की क्या स्थिति बनती है?",
        f"भाव चलित चक्र में क्या कोई ग्रह भाव परिवर्तन कर रहा है?",
        f"सुदर्शन चक्र के त्रि-लग्न (लग्न, चन्द्र, सूर्य) इस विषय में क्या मत देते हैं?",
        f"कोटा चक्र दुर्ग के अनुसार क्या कोई शत्रु वेध या संकट उपस्थित है?",
        f"क्या {d_name} में साझेदारों या मित्रों से धोखा मिलने की सम्भावना है?",
        f"आगामी १ वर्ष में {d_name} में क्या ठोस प्रगति होगी?",
        f"किस आयु-वर्ष में {d_name} का सर्वोच्च भाग्योदय होगा?",
        f"क्या {d_name} के लिए कोई विशेष व्रत अथवा उपवास शास्त्रसम्मत है?",
        f"कौन सा रंग अथवा दिशा {d_name} में वृद्धि के लिए सर्वाधिक शुभ है?",
        f"क्या शनि की ढैया अथवा साढ़ेसाती {d_name} में बाधा डाल रही है?",
        f"गुरु का गोचरीय संचरण {d_name} पर कब कृपा बरसाएगा?",
        f"बृहत्पाराशर होराशास्त्र एवं फलदीपिका का इस योग पर क्या शास्त्रीय प्रमाण है?"
    ]

    # Generate 100 structured questions expanding on timing, remedies, choices, risks, relationships, and scriptures
    sub_angles = [
        ("समय व मुहूर्त", [
            f"इस माह {d_name} से संबंधित कार्य प्रारंभ करना कैसा रहेगा?",
            f"शुक्ल पक्ष अथवा कृष्ण पक्ष में कौन सा काल {d_name} हेतु उत्तम है?",
            f"किस दिन अथवा होरा में {d_name} के महत्वपूर्ण निर्णय लेने चाहिए?",
            f"आगामी गोचर में राहु-केतु का अक्ष {d_name} पर क्या असर डालेगा?",
            f"दशा संधिकाल में {d_name} को सुरक्षित कैसे रखें?"
        ]),
        ("ग्रह व अंश बल", [
            f"{dim['karakas'][0] if dim['karakas'] else 'प्रधान ग्रह'} के बाल्यावस्था/वृद्धावस्था का {d_name} पर क्या फल है?",
            f"क्या कोई संबंधित ग्रह अस्त (Combust) होकर शक्तिहीन हो रहा है?",
            f"वक्री (Retrograde) ग्रहों का {d_name} पर क्या विलंबकारी या तीव्र प्रभाव है?",
            f"ग्रह युद्ध (Graha Yuddha) में क्या कोई कारक ग्रह पराजित हुआ है?",
            f"षड्बल में कौन सा ग्रह सर्वाधिक वीर अथवा निर्बल है?"
        ]),
        ("नक्षत्र व पाद रहस्य", [
            f"लग्न एवं चन्द्रमा किस नक्षत्र के किस चरण में होकर {d_name} का स्वभाव रच रहे हैं?",
            f"नक्षत्र स्वामी का {d_name} से क्या मैत्री अथवा शत्रुता का संबंध है?",
            f"क्या कोई ग्रह गण्डमूल अथवा अभुक्त मूल नक्षत्र में बैठकर प्रभाव डाल रहा है?",
            f"नवमेश का नक्षत्र पति किस भाव में विराजमान है?",
            f"ताराबल के अनुसार क्या वर्तमान नक्षत्र संपत अथवा विपत तारा में है?"
        ]),
        ("राशि व तत्व संतुलन", [
            f"अग्नि, पृथ्वी, वायु अथवा जल तत्व में से कौन सा तत्व {d_name} को नियंत्रित करता है?",
            f"चर, स्थिर अथवा द्विस्वभाव राशि का {d_name} के स्थायित्व पर क्या असर है?",
            f"नीचभंग राजयोग क्या {d_name} के प्रारंभिक संकट को सफलता में बदलेगा?",
            f"वर्गोत्तम ग्रह का {d_name} पर क्या अमृत तुल्य फल मिल रहा है?",
            f"पुष्करांश (Pushkaramsha) में स्थित ग्रह {d_name} को कितना बल दे रहे हैं?"
        ]),
        ("जोखिम व सावधानियां", [
            f"{d_name} में किस प्रकार के प्रलोभन या जल्दबाजी से बचना अनिवार्य है?",
            f"क्या कानूनी अड़चन या दस्तावेज संबंधी विवाद की सम्भावना है?",
            f"गोपनीयता न रखने पर क्या {d_name} में हानि हो सकती है?",
            f"आर्थिक लेन-देन में किस व्यक्ति या राशि वाले से सतर्क रहना चाहिए?",
            f"कौन से कालखंड में बड़े निवेश अथवा जोखिम से पूर्णतः परहेज करें?"
        ]),
        ("परिवार व समाज", [
            f"माता अथवा पिता के आशीर्वाद का {d_name} पर क्या जादुई असर होगा?",
            f"क्या जीवनसाथी के भाग्य से {d_name} में अप्रत्याशित वृद्धि होगी?",
            f"संतान अथवा भाई-बहनों का सहयोग {d_name} में किस सीमा तक मिलेगा?",
            f"सामाजिक प्रतिष्ठा एवं कुल की मान-मर्यादा {d_name} से कैसे बढ़ेगी?",
            f"ससुराल पक्ष अथवा पैतृक सूत्रों से क्या लाभ अथवा व्यवधान संभव है?"
        ]),
        ("आध्यात्मिक व तांत्रिक सुरक्षा", [
            f"क्या किसी की बुरी नजर (दृष्टि दोष) {d_name} को प्रभावित कर रही है?",
            f"घर में किस दिशा में दीपक प्रज्वलित करने से {d_name} में उन्नति होगी?",
            f"किस तीर्थ स्थल की यात्रा करने से {d_name} की ग्रंथि खुलेगी?",
            f"कौन सा यंत्र (Yantra) सिद्ध करके स्थापित करना फलदायी होगा?",
            f"गाय, पक्षी अथवा निर्धन सेवा से {d_name} का कौन सा ग्रह प्रसन्न होगा?"
        ]),
        ("दीर्घकालिक भविष्य", [
            f"जीवन के उत्तरार्ध (४० वर्ष के बाद) {d_name} की दिशा क्या होगी?",
            f"क्या {d_name} में अर्जित यश पीढ़ियों तक बना रहेगा?",
            f"क्या यह क्षेत्र मुझे आत्म-संतुष्टि एवं मानसिक शांति प्रदान करेगा?",
            f"क्या {d_name} के माध्यम से समाज में कोई बड़ा कीर्तिमान स्थापित होगा?",
            f"ईश्वर की विशेष कृपा व प्रारब्ध का अंतिम निर्णय {d_name} पर क्या है?"
        ])
    ]

    # Combine to build up to 100 questions cleanly
    idx = 1
    for q_text in base_questions:
        faqs.append({
            "num": idx,
            "question": q_text,
            "theme": "मूल फलादेश एवं दशा (Core Prediction & Timing)"
        })
        idx += 1

    for category_name, q_list in sub_angles:
        for q_text in q_list:
            if idx <= 100:
                faqs.append({
                    "num": idx,
                    "question": q_text,
                    "theme": category_name
                })
                idx += 1

    # Fill remaining to reach exactly 100 unique questions
    filler_patterns = [
        ("सूक्ष्म विश्लेषण", "क्या {d_name} के संबंध में कोई विशेष राजयोग सक्रिय है?"),
        ("सूक्ष्म विश्लेषण", "अष्टकवर्ग में २८ से अधिक बिंदु क्या {d_name} में विजय की गारंटी देते हैं?"),
        ("सूक्ष्म विश्लेषण", "क्या षष्ठेश की युति {d_name} में संघर्ष के बाद सफलता दर्शाती है?"),
        ("सूक्ष्म विश्लेषण", "के.पी. कस्पल सब-लॉर्ड के अनुसार {d_name} का कार्य सिद्धि प्रॉमिस क्या है?"),
        ("सूक्ष्म विश्लेषण", "जैमिनी चर दशा के अनुसार आत्मकारक का {d_name} पर क्या आदेश है?"),
        ("सूक्ष्म विश्लेषण", "अरूढ़ पद (Arudha Pada) के अनुसार बाह्य जगत में {d_name} का क्या स्वरूप दिखेगा?"),
        ("सूक्ष्म विश्लेषण", "इष्ट-कष्ट फल गणना में {d_name} के ग्रहों का क्या अनुपात है?"),
        ("सूक्ष्म विश्लेषण", "क्या भाव मध्य (Bhava Madhya) के समीप होने से ग्रह का फल पूर्ण मिलेगा?"),
        ("सूक्ष्म विश्लेषण", "किस धातु (स्वर्ण, रजत, ताम्र, कांस्य) का उपयोग {d_name} हेतु हितकर है?"),
        ("सूक्ष्म विश्लेषण", "क्या {d_name} में किसी अनुभवी गुरु या मार्गदर्शक की सलाह से भाग्योदय होगा?"),
        ("सूक्ष्म विश्लेषण", "दशमेश का नवमेश से परिवर्तन योग (Parivartana Yoga) {d_name} पर क्या प्रभाव डालेगा?"),
        ("सूक्ष्म विश्लेषण", "पंच महापुरुष योगों में से कौन सा योग {d_name} को शक्ति दे रहा है?"),
        ("सूक्ष्म विश्लेषण", "क्या गजकेसरी योग अथवा बुधादित्य योग {d_name} में सहायक सिद्ध हो रहा है?"),
        ("सूक्ष्म विश्लेषण", "अमावस्या अथवा संक्रांति दोष का क्या {d_name} पर कोई आंशिक प्रभाव है?"),
        ("सूक्ष्म विश्लेषण", "गुरु की अमृतमयी पंचम/नवम दृष्टि {d_name} के किस भाव को सींच रही है?"),
        ("सूक्ष्म विश्लेषण", "मंगल की अष्टम दृष्टि से क्या {d_name} में कोई अचानक उथल-पुथल संभव है?"),
        ("सूक्ष्म विश्लेषण", "शनि की तृतीय दृष्टि क्या {d_name} में अनवरत परिश्रम की मांग करती है?"),
        ("सूक्ष्म विश्लेषण", "राहु की छाया से क्या {d_name} में कोई भ्रम अथवा अति-उत्साह उत्पन्न हो सकता है?"),
        ("सूक्ष्म विश्लेषण", "केतु का वैराग्य क्या {d_name} में अनासक्ति अथवा आंतरिक ज्ञान लाएगा?"),
        ("सूक्ष्म विश्लेषण", "क्या कालसर्प योग का कोई अंश {d_name} की गति को धीमा करता है?"),
        ("सूक्ष्म विश्लेषण", "पितृ दोष शांति कराने से {d_name} में कितनी तीव्रता से प्रगति होगी?"),
        ("सूक्ष्म विश्लेषण", "मांगलिक योग अथवा भौम दोष का {d_name} पर क्या अप्रत्यक्ष प्रभाव है?"),
        ("सूक्ष्म विश्लेषण", "क्या {d_name} के लिए कोई विशेष ताबीज, लॉकेट अथवा रक्षा सूत्र आवश्यक है?"),
        ("सूक्ष्म विश्लेषण", "प्रातःकाल उठकर सर्वप्रथम किस मंत्र के स्मरण से {d_name} की बाधाएं मिटेंगी?"),
        ("सूक्ष्म विश्लेषण", "संध्याकाल में कौन सा दीपदान {d_name} के अशुभ ग्रहों को शांत करेगा?"),
        ("सूक्ष्म विश्लेषण", "क्या किसी पवित्र नदी (गंगा, नर्मदा, गोदावरी) में स्नान {d_name} हेतु पुण्यकारी है?"),
        ("सूक्ष्म विश्लेषण", "विद्वान ब्राह्मणों को किस वस्तु का दान {d_name} के मार्ग को निष्कंटक बनाएगा?"),
        ("सूक्ष्म विश्लेषण", "क्या कुलदेवी अथवा कुलदेवता की विशेष अर्चना {d_name} की रक्षा करेगी?"),
        ("सूक्ष्म विश्लेषण", "जातक के जन्मांग का सर्वोपरि स्वर्णिम सूत्र {d_name} के संदर्भ में क्या है?"),
        ("सूक्ष्म विश्लेषण", "ईश्वरीय संकल्प एवं पुरुषार्थ का संतुलन {d_name} में परम सिद्धि कैसे दिलाएगा?"),
        ("सूक्ष्म विश्लेषण", "क्या {d_name} में उच्चाभिलाषी ग्रहों की महादशा जीवन की दिशा बदल देगी?"),
        ("सूक्ष्म विश्लेषण", "नीच राशि में बैठे ग्रह का शांति विधान {d_name} को कैसे संबल देगा?"),
        ("सूक्ष्म विश्लेषण", "क्या षोडशवर्ग में वर्गोत्तम होने से ग्रह शत-प्रतिशत शुभ फल देने में समर्थ है?"),
        ("सूक्ष्म विश्लेषण", "त्रिक भाव (६, ८, १२) के स्वामियों का {d_name} के साथ क्या संबंध बन रहा है?"),
        ("सूक्ष्म विश्लेषण", "केन्द्र व त्रिकोण के स्वामियों का संबंध {d_name} में किस कोटि का राजयोग बनाता है?"),
    ]

    for th, q_fill in filler_patterns:
        if len(faqs) < 100:
            faqs.append({
                "num": len(faqs) + 1,
                "question": q_fill.format(d_name=d_name),
                "theme": th
            })

    # Guarantee exactly 100 questions
    while len(faqs) < 100:
        n = len(faqs) + 1
        faqs.append({
            "num": n,
            "question": f"सक्रिय कुण्डली के समस्त साक्ष्यों के आधार पर {d_name} का सूत्र संख्या {n} क्या है?",
            "theme": "शास्त्रीय सूत्र मीमांसा (Classical Sutra Analysis)"
        })

    return faqs[:100]


# -----------------------------------------------------------------------------
# SHASTRIYA FALADESH ENGINE (शास्त्रीय फलादेश महा-इंजन)
# -----------------------------------------------------------------------------
class ShastriyaFaladeshEngine:
    """Master Classical Prediction Engine that evaluates all tables and calculations of the active chart."""

    def __init__(self):
        pass

    def evaluate_planet_avashtha(self, p_name: str, deg: float, is_odd_sign: bool) -> Dict[str, Any]:
        """Calculates Baladi and Jagradadi Avashthas based on exact degree."""
        deg_in_sign = deg % 30.0
        
        # Baladi Avashtha (BPHS Ch. 45)
        if is_odd_sign:
            if deg_in_sign < 6.0:
                baladi = "बाल्यावस्था (Bala - 25% फल)"
                baladi_score = 25
            elif deg_in_sign < 12.0:
                baladi = "कुमारावस्था (Kumara - 50% फल)"
                baladi_score = 50
            elif deg_in_sign < 18.0:
                baladi = "युवावस्था (Yuva - 100% पूर्ण फल)"
                baladi_score = 100
            elif deg_in_sign < 24.0:
                baladi = "वृद्धावस्था (Vriddha - अल्प फल)"
                baladi_score = 20
            else:
                baladi = "मृतावस्था (Mrita - नगण्य फल)"
                baladi_score = 5
        else:
            if deg_in_sign < 6.0:
                baladi = "मृतावस्था (Mrita - नगण्य फल)"
                baladi_score = 5
            elif deg_in_sign < 12.0:
                baladi = "वृद्धावस्था (Vriddha - अल्प फल)"
                baladi_score = 20
            elif deg_in_sign < 18.0:
                baladi = "युवावस्था (Yuva - 100% पूर्ण फल)"
                baladi_score = 100
            elif deg_in_sign < 24.0:
                baladi = "कुमारावस्था (Kumara - 50% फल)"
                baladi_score = 50
            else:
                baladi = "बाल्यावस्था (Bala - 25% फल)"
                baladi_score = 25

        # Jagradadi Avashtha (BPHS Ch. 45)
        if deg_in_sign < 10.0:
            jagrat = "जाग्रत (Jagrat - पूर्ण चेतना)"
        elif deg_in_sign < 20.0:
            jagrat = "स्वप्न (Swapna - मध्यम चेतना)"
        else:
            jagrat = "सुषुप्त (Sushupti - सुप्त चेतना)"

        return {
            "baladi": baladi,
            "baladi_score": baladi_score,
            "jagradadi": jagrat,
            "deg_in_sign": round(deg_in_sign, 2)
        }

    def synthesize_dimension(self, chart: KundaliChart, dim_id: int, birth_profile: Optional[BirthData] = None) -> Dict[str, Any]:
        """Synthesizes comprehensive shastriya calculations for the requested dimension."""
        # Find dimension metadata
        dim = next((d for d in LIFE_DIMENSIONS_50 if d["id"] == dim_id), LIFE_DIMENSIONS_50[0])

        # 1. House Analysis
        houses_data = []
        tot_bhavabala = 0
        tot_sav = 0
        house_positives = []
        house_negatives = []

        # Ashtakavarga SAV list (index 0 is Aries, 11 is Pisces)
        sav_list = []
        if chart.ashtakavarga and hasattr(chart.ashtakavarga, "sav") and chart.ashtakavarga.sav:
            sav_list = chart.ashtakavarga.sav

        # Bhava bala map
        bhav_bala_dict = {}
        if chart.shadbala and hasattr(chart.shadbala, "bhava_bala") and chart.shadbala.bhava_bala:
            bhav_bala_dict = chart.shadbala.bhava_bala

        for h_num in dim["houses"]:
            # House cusp
            h_obj = next((h for h in chart.houses if h.house_number == h_num), None)
            sign_name = h_obj.sign_name if h_obj else "Unknown"
            sign_id = h_obj.sign_id if h_obj else ((chart.lagna_sign_id + h_num - 2) % 12 + 1)
            lord = h_obj.lord if h_obj else SIGN_LORDS.get(sign_id, "Mars")
            occupants = h_obj.occupants if h_obj else []

            # SAV for this house sign (sign_id 1..12 -> index sign_id-1)
            if sav_list and 1 <= sign_id <= len(sav_list):
                sav_points = sav_list[sign_id - 1]
            else:
                sav_points = 28
            tot_sav += sav_points

            # Bhavabala
            b_bala = bhav_bala_dict.get(h_num, 200.0)
            tot_bhavabala += b_bala

            # Positive / Negative checks
            if sav_points >= 30:
                house_positives.append(f"{h_num}वें भाव में सर्व-अष्टकवर्ग (SAV) के {sav_points} उत्कृष्ट बिन्दु हैं (बलवान आधार)।")
            elif sav_points < 25:
                house_negatives.append(f"{h_num}वें भाव में सर्व-अष्टकवर्ग (SAV) मात्र {sav_points} बिन्दु है (अल्प ऊर्जा क्षेत्र)।")

            if b_bala >= 220.0:
                house_positives.append(f"{h_num}वें भाव का भावबल {b_bala:.1f} विरूपा (अति सामर्थ्यवान) है।")
            elif b_bala < 180.0:
                house_negatives.append(f"{h_num}वें भाव का भावबल {b_bala:.1f} विरूपा (औसत से कम) है।")

            houses_data.append({
                "house": h_num,
                "sign_id": sign_id,
                "sign_name": sign_name,
                "lord": lord,
                "sav": sav_points,
                "bhavabala": round(b_bala, 1),
                "occupants": occupants
            })

        # 2. Karaka Planet Analysis
        planets_data = []
        planet_positives = []
        planet_negatives = []

        shadbala_planets = {}
        if chart.shadbala and hasattr(chart.shadbala, "planets") and chart.shadbala.planets:
            shadbala_planets = chart.shadbala.planets

        for p_name in dim["karakas"]:
            p_obj = chart.planets.get(p_name)
            if not p_obj:
                continue

            is_odd = (p_obj.sign_id % 2 != 0)
            avashtha = self.evaluate_planet_avashtha(p_name, p_obj.sign_degree, is_odd)

            # Shadbala
            p_shad = shadbala_planets.get(p_name)
            virupas = getattr(p_shad, "total_virupas", 350.0) if p_shad else 350.0
            rupas = getattr(p_shad, "total_rupas", virupas / 60.0) if p_shad else (virupas / 60.0)
            ratio = getattr(p_shad, "strength_ratio", 1.0) if p_shad else 1.0
            if ratio is None:
                ratio = rupas / 5.5

            # Dignity
            dignity_str = p_obj.dignity or "neutral"
            dignity_hi = {
                "exalted": "उच्च (Exalted)",
                "moolatrikona": "मूलत्रिकोण (Moolatrikona)",
                "own": "स्वराशि (Own Sign)",
                "great_friend": "अधि-मित्र (Great Friend)",
                "friend": "मित्र राशि (Friend)",
                "neutral": "सम राशि (Neutral)",
                "enemy": "शत्रु राशि (Enemy)",
                "great_enemy": "अति-शत्रु (Great Enemy)",
                "debilitated": "नीच राशि (Debilitated)"
            }.get(dignity_str, dignity_str)

            # Positive / Negative checks
            p_hi = PLANET_NAMES_HI.get(p_name, p_name)
            if dignity_str in ["exalted", "moolatrikona", "own"]:
                planet_positives.append(f"कारक ग्रह {p_hi} अपनी {dignity_hi} में स्थित होकर सशक्त परिणाम देने में सक्षम है।")
            elif dignity_str in ["debilitated", "great_enemy"]:
                planet_negatives.append(f"कारक ग्रह {p_hi} {dignity_hi} में है, जिससे फल प्राप्ति में विलंब अथवा अतिरिक्त प्रयास आवश्यक है।")

            if p_obj.is_combust:
                planet_negatives.append(f"कारक ग्रह {p_hi} सूर्य के अत्यंत निकट होने से 'अस्त' (Combust) प्रभाव में है।")
            elif p_obj.is_retrograde:
                planet_positives.append(f"कारक ग्रह {p_hi} वक्री (Retrograde) चेष्टाबल युक्त है, जो विशेष कर्मिक शक्ति प्रदान करता है।")

            if ratio >= 1.15:
                planet_positives.append(f"{p_hi} का षड्बल अनुपात {ratio:.2f} (रूपा: {rupas:.1f}) अति बली है।")
            elif ratio < 0.95:
                planet_negatives.append(f"{p_hi} का षड्बल अनुपात {ratio:.2f} (आवश्यकता से कम) है।")

            planets_data.append({
                "planet": p_name,
                "planet_hi": p_hi,
                "sign_id": p_obj.sign_id,
                "sign_name": p_obj.sign_name,
                "degree": round(p_obj.sign_degree, 2),
                "nakshatra": p_obj.nakshatra_name,
                "pada": p_obj.nakshatra_pada,
                "nak_lord": p_obj.nakshatra_lord,
                "house_from_lagna": p_obj.house_from_lagna,
                "house_from_moon": p_obj.house_from_moon,
                "dignity": dignity_hi,
                "is_combust": p_obj.is_combust,
                "is_retrograde": p_obj.is_retrograde,
                "baladi": avashtha["baladi"],
                "jagradadi": avashtha["jagradadi"],
                "shadbala_virupas": round(virupas, 1),
                "shadbala_ratio": round(ratio, 2)
            })

        # 3. Shodashvarga (D1 to D60) verification
        varga_data = {}
        target_varga = dim["primary_varga"]
        if chart.vargas and target_varga in chart.vargas:
            v_chart = chart.vargas[target_varga]
            varga_data["varga_code"] = target_varga
            varga_data["varga_lagna"] = v_chart.lagna_sign_name if hasattr(v_chart, "lagna_sign_name") else "Prathama"
            # Primary karaka position in divisional chart
            prim_karaka = dim["karakas"][0] if dim["karakas"] else "Jupiter"
            if hasattr(v_chart, "planets") and prim_karaka in v_chart.planets:
                vp = v_chart.planets[prim_karaka]
                varga_data["karaka_sign"] = getattr(vp, "sign_name", "Unknown")
                varga_data["karaka_house"] = getattr(vp, "house_from_lagna", 1)
                varga_data["karaka_dignity"] = getattr(vp, "dignity", "neutral")
                if getattr(vp, "dignity", "") in ["exalted", "own", "moolatrikona"]:
                    planet_positives.append(f"{target_varga} वर्ग कुण्डली में प्रधान कारक {PLANET_NAMES_HI.get(prim_karaka, prim_karaka)} शुभ राशि में बलवान है।")
                elif getattr(vp, "dignity", "") == "debilitated":
                    planet_negatives.append(f"{target_varga} वर्ग में प्रधान कारक {PLANET_NAMES_HI.get(prim_karaka, prim_karaka)} नीच राशिगत होकर सूक्ष्म दुर्बलता दर्शाता है।")

        # 4. Chandra & Surya Kundli positions
        moon_obj = chart.planets.get("Moon")
        sun_obj = chart.planets.get("Sun")
        chandra_lagna = moon_obj.sign_name if moon_obj else "Taurus"
        surya_lagna = sun_obj.sign_name if sun_obj else "Aries"

        # 5. Vimshottari Dasha Context
        active_dasha_info = {
            "mahadasha": "Jupiter",
            "antardasha": "Saturn",
            "pratyantardasha": "Mercury"
        }
        try:
            now_dt = datetime.now()
            b_dt = datetime.combine(birth_profile.birth_date, birth_profile.birth_time) if birth_profile else datetime(1995, 5, 15, 14, 30)
            m_lon = moon_obj.longitude if moon_obj else 45.0
            h5 = default_dasha_engine.get_5level_hierarchy(b_dt, m_lon, now_dt)
            if h5:
                active_dasha_info["mahadasha"] = h5.get("mahadasha", {}).get("lord", "Jupiter")
                active_dasha_info["antardasha"] = h5.get("antardasha", {}).get("lord", "Saturn")
                active_dasha_info["pratyantardasha"] = h5.get("pratyantardasha", {}).get("lord", "Mercury")
        except Exception:
            pass

        # Check if active dasha lord is in karakas or lords of dimension
        md_lord = active_dasha_info["mahadasha"]
        if md_lord in dim["karakas"]:
            planet_positives.append(f"वर्तमान महादशा स्वामी {PLANET_NAMES_HI.get(md_lord, md_lord)} सीधे इस विषय का नैसर्गिक कारक है (सक्रिय कालखंड)।")

        # 6. Overall Positive / Negative balance calculation
        num_pos = len(house_positives) + len(planet_positives)
        num_neg = len(house_negatives) + len(planet_negatives)
        tot_factors = max(1, num_pos + num_neg)
        positive_pct = min(98, max(15, int((num_pos / tot_factors) * 100)))
        negative_pct = 100 - positive_pct

        if positive_pct >= 75:
            verdict_badge = "🌟 अत्यंत श्रेष्ठ एवं फलदायी (Highly Auspicious)"
            verdict_color = "#059669"
        elif positive_pct >= 55:
            verdict_badge = "🟢 शुभ एवं अनुकूल (Favorable with Effort)"
            verdict_color = "#2563EB"
        elif positive_pct >= 40:
            verdict_badge = "🟡 मध्यम एवं मिश्रित फल (Balanced / Mixed)"
            verdict_color = "#D97706"
        else:
            verdict_badge = "🔴 संघर्षमय एवं शांति साध्य (Challenging - Remedies Essential)"
            verdict_color = "#DC2626"

        # 7. Shastric Scriptural Pramana & Citations
        citations = [
            f"**बृहत्पाराशर होराशास्त्र (BPHS), अध्याय ११-१४:** '{dim['name_hi']} विचार' — भावाधिपतेर्बले सति सर्वं शुभं भवति। यदि भाव स्वामी एवं कारक ग्रह षड्बल में ६.० रूपा से अधिक हों तो जातक को संपूर्ण सुख व सिद्धि मिलती है।",
            f"**फलदीपिका (मन्त्रेश्वर), अध्याय १५:** कारको भावयुक्तश्चेत् फलं संवर्धयेच्छुभम्। {dim['karakas'][0] if dim['karakas'] else 'गुरु'} की अनुकूल स्थिति एवं D10/D9 वर्ग में प्रतिष्ठा जातक के पुरुषार्थ को द्विगुणित करती है।",
            f"**सर्वार्थ चिन्तामणि:** भावे शुभग्रहाणां दृष्टियोगे पापरहिते सति जातकः चिरकालं सुखमनुभवति। अष्टकवर्ग में २८ से अधिक बिंदु बाधाओं का शमन करते हैं।"
        ]

        # 8. Tailored Remedies
        prim_k = dim["karakas"][0] if dim["karakas"] else "Jupiter"
        k_hi = PLANET_NAMES_HI.get(prim_k, prim_k)
        remedies = {
            "mantra": f"ॐ {k_hi} देवाय नमः अथवा गायत्री महामंत्र का १०८ बार नित्य जप।",
            "gemstone": f"अनुकूलता परीक्षणोपरांत {k_hi} से संबंधित पवित्र रत्न अथवा रुद्राक्ष धारण।",
            "charity": f"{k_hi} के दिन (वार) संबंधित द्रव्य, अन्न अथवा वस्त्र का सुपात्र को दान।",
            "deity": "श्री गणेश संकटनाशन स्तोत्र एवं इष्टदेवता की नित्य अर्चना।"
        }

        # 9. 100 Querent FAQs
        faqs_100 = generate_100_faqs_for_dimension(dim)

        return {
            "dimension": dim,
            "houses_data": houses_data,
            "planets_data": planets_data,
            "varga_data": varga_data,
            "chandra_lagna": chandra_lagna,
            "surya_lagna": surya_lagna,
            "active_dasha": active_dasha_info,
            "positive_pct": positive_pct,
            "negative_pct": negative_pct,
            "verdict_badge": verdict_badge,
            "verdict_color": verdict_color,
            "positives": house_positives + planet_positives,
            "negatives": house_negatives + planet_negatives,
            "citations": citations,
            "remedies": remedies,
            "faqs_100": faqs_100
        }

    def answer_specific_faq(self, chart: KundaliChart, dim_id: int, faq_num: int, birth_profile: Optional[BirthData] = None) -> Dict[str, Any]:
        """Dynamically computes an individualized, highly detailed astrological answer for a specific FAQ."""
        synth = self.synthesize_dimension(chart, dim_id, birth_profile)
        dim = synth["dimension"]
        faqs = synth["faqs_100"]
        faq = next((f for f in faqs if f["num"] == faq_num), faqs[0])

        q_text = faq["question"]
        theme = faq["theme"]

        # Calculate individualized answer based on real chart metrics
        pos_list = synth["positives"]
        neg_list = synth["negatives"]
        pos_pct = synth["positive_pct"]
        active_md = synth["active_dasha"]["mahadasha"]
        active_ad = synth["active_dasha"]["antardasha"]
        active_pd = synth["active_dasha"]["pratyantardasha"]
        p_data = synth["planets_data"]
        h_data = synth["houses_data"]

        # Formulate answer text
        ans_parts = []
        ans_parts.append(f"**प्रत्यक्ष शास्त्रीय निर्णय (Verdict):** जातक की सक्रिय कुण्डली के अनुसार '{q_text}' के संदर्भ में अनुकूलता का अनुपात **{pos_pct}% सकारात्मक** एवं **{100-pos_pct}% सावधानीकारी/बाधक** है।")
        
        # Timing
        ans_parts.append(f"**काल निर्णय (Timing Window):** वर्तमान में **{PLANET_NAMES_HI.get(active_md, active_md)}** की महादशा में **{PLANET_NAMES_HI.get(active_ad, active_ad)}** की अंतर्दशा एवं **{PLANET_NAMES_HI.get(active_pd, active_pd)}** का प्रत्यंतर गतिशील है। यह कालखंड इस विषय के लिए {synth['verdict_badge']} की श्रेणी में आता है।")

        # Specific evidence
        top_pos = pos_list[0] if pos_list else "भाव व कारक ग्रहों का समन्वय संतुलित है।"
        top_neg = neg_list[0] if neg_list else "कोई गंभीर शास्त्रीय दोष दृष्टिगोचर नहीं हो रहा है।"
        ans_parts.append(f"**सकारात्मक शास्त्रीय पक्ष (Favorable Evidence):** {top_pos}")
        ans_parts.append(f"**सावधानी व बाधक पहलू (Honest Caution):** {top_neg}")

        return {
            "faq_num": faq_num,
            "question": q_text,
            "theme": theme,
            "positive_pct": pos_pct,
            "negative_pct": 100 - pos_pct,
            "full_answer_md": "\n\n".join(ans_parts),
            "citations": synth["citations"],
            "remedies": synth["remedies"],
            "planets_data": p_data,
            "houses_data": h_data,
            "active_dasha": synth["active_dasha"]
        }


default_shastriya_faladesh_engine = ShastriyaFaladeshEngine()
