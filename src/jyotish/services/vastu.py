"""
Vastu-Jyotish Directional Mandala and Remedial Architecture Engine for JyotishOS.

Correlates planetary positions, strengths, and afflictions from the natal Kundali
with the 8 cardinal/ordinal directions and Brahmasthan of residential/commercial spaces.
Provides comprehensive bilingual (English/Hindi) diagnostic reports, architectural zones,
panchatatva elemental analysis, and authentic 5-fold shastriya remedies.
"""

from typing import Dict, Any, List, Optional
from ..core.models import KundaliChart, PlanetPosition
from ..core.constants import SIGN_LORDS


VASTU_DIRECTIONS = {
    "East": {
        "hindi": "पूर्व (Purva)",
        "lord": "Sun",
        "deity": "Indra / Surya Dev",
        "element": "Agni / Light (तेज व प्रकाश)",
        "degree_range": "67.5° – 112.5° (मध्य 90°)",
        "associated_house": "१म भाव (तनु / लग्न - देह व आत्मशक्ति)",
        "vastu_purusha_organ": "वास्तु पुरुष का मस्तक, कपाल व नेत्र",
        "gemstone": "माणिक्य (Ruby)",
        "metal": "तांबा (Copper)",
        "botanical": "आक (मदार), लाल कनेर, जामुन",
        "color_therapy": "सूर्योदय नारंगी, स्वर्णिम, गहरा केसरिया (Sunrise Orange / Gold)",
        "symptoms_of_defect": "हृदय विकार, नेत्र रोग, सिरदर्द, पिता से मतभेद, सरकारी कार्यों में बाधा, मानहानि व ऊर्जाहीनता।",
        "ideal_uses": ["मुख्य द्वार (Main Entrance)", "बालकनी व खुला बरामदा", "पूजा / ध्यान कक्ष", "लिविंग रूम की खिड़कियां"],
        "avoid": ["भारी स्टोरेज / गोदाम", "शौचालय व सेप्टिक टैंक", "सीढ़ियां", "ऊंची ठोस दीवारें"],
        "chakra_organ": "Vitality, Eye Sight, Heart, Head, Father, Social Prestige",
        "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः ॥",
        "remedy_en": "Keep eastern wall low, clean, and light. Install a consecrated Copper Surya Yantra or brass sun emblem on the eastern wall. Incorporate golden-orange lighting.",
        "remedy_hi": "पूर्व दिशा को स्वच्छ, खुला और हल्का रखें। भारी सामान न रखें। पूर्व की दीवार पर तांबे का सूर्य यंत्र या पीतल का सूर्य स्थापित करें। शुद्ध तांबे का जल पात्र रखें।",
        "non_destructive_remedy": "यदि पूर्व दिशा बंद या भारी हो तो दीवार पर 100% तांबे की पट्टी (Copper Strip) जमीन में स्थापित करें तथा पूर्व दिशा में सूर्य पिरामिड लगाएं।",
        "shastra_shloka": "पूर्वे शक्रः श्रियं दद्याद् दक्षिणे यमराड्भयम् । वरुणे पश्चिमे सौम्यं कुबेरश्चोत्तरे धनम् ॥"
    },
    "South-East": {
        "hindi": "आग्नेय (Agneya)",
        "lord": "Venus",
        "deity": "Agni Dev (अग्नि देव)",
        "element": "Fire (अग्नि तत्व)",
        "degree_range": "112.5° – 157.5° (मध्य 135°)",
        "associated_house": "२य व ११वां भाव (धन प्रवाह, नकदी व भोग)",
        "vastu_purusha_organ": "वास्तु पुरुष का दक्षिण वक्षस्थल व दायां कंधा",
        "gemstone": "हीरा / ओपल (Diamond / White Zircon)",
        "metal": "चांदी व कांसा (Silver / Bronze)",
        "botanical": "गूलर (Udumbara), अनार, गुलाब, पलाश",
        "color_therapy": "क्रीम, हल्का गुलाबी, चमकदार सफेद, पेस्टल पीच (Cream / Pastel Pink)",
        "symptoms_of_defect": "महिलाओं का निरंतर अस्वस्थ रहना, नकदी की तंगी, वैवाहिक कलह, अग्नि भय, दुर्घटना, हार्मोनल असंतुलन।",
        "ideal_uses": ["रसोईघर (Kitchen)", "गैस बर्नर / कुकटॉप", "विद्युत मीटर / इन्वर्टर / जनरेटर", "बॉयलर व गीजर"],
        "avoid": ["पानी का बोरिंग / अंडरग्राउंड टैंक", "मुख्य द्वार", "मास्टर बेडरूम", "पूजा घर"],
        "chakra_organ": "Hormones, Reproductive Health, Liquid Cash Flow, Marital Bliss, Cooking Fire",
        "mantra": "ॐ शुं शुक्राय नमः ॥",
        "remedy_en": "Place cooktop facing East. Strictly avoid water bodies, toilets, or underground tanks here. Use cream or pastel peach shades.",
        "remedy_hi": "रसोईघर और विद्युत उपकरण आग्नेय कोण में रखें। इस दिशा में पानी का बोरिंग या भूमिगत टंकी कभी न बनाएं। क्रीम या हल्का गुलाबी रंग प्रयोग करें।",
        "non_destructive_remedy": "यदि आग्नेय में जल तत्व या टॉयलेट हो तो जिंक/कॉपर स्ट्रिप से ऊर्जा सील करें और आग्नेय कोण में २४ घंटे जलने वाला शून्य वाट का लाल बल्ब लगाएं।",
        "shastra_shloka": "आग्नेय्यां हुतभुक् पाको भोक्ता चैव न सीदति । अत्रैव पावकस्थानं धनधान्यविवर्धनम् ॥"
    },
    "South": {
        "hindi": "दक्षिण (Dakshina)",
        "lord": "Mars",
        "deity": "Yama (धर्मराज यम)",
        "element": "Tejas / Heavy Earth (तेज व भू-तत्व)",
        "degree_range": "157.5° – 202.5° (मध्य 180°)",
        "associated_house": "१०म भाव (कर्म, पद-प्रतिष्ठा, पराक्रम व कीर्ति)",
        "vastu_purusha_organ": "वास्तु पुरुष की दाईं कोहनी व पसलियां",
        "gemstone": "लाल मूंगा (Red Coral)",
        "metal": "तांबा (Copper) व पीतल",
        "botanical": "खैर (Khadira), नीम, अशोक, लाल कनेर",
        "color_therapy": "गहरा लाल, टेराकोटा, कत्थई, महोगनी (Deep Red / Terracotta)",
        "symptoms_of_defect": "रक्त विकार, कानूनी विवाद, भाइयों में वैमनस्य, दुर्घटना का भय, मान-प्रतिष्ठा में हानि, अनपेक्षित शत्रुता।",
        "ideal_uses": ["शयनकक्ष (Bedroom)", "भारी स्टोरेज / गोदाम", "सीढ़ियां (Staircase)", "ओवरहेड पानी की टंकी"],
        "avoid": ["मुख्य द्वार (३रे/४थे पद को छोड़कर)", "अंडरग्राउंड वाटर टैंक / बोरिंग", "बड़े शीशे / दर्पण", "खुला गड्ढा"],
        "chakra_organ": "Blood, Bone Marrow, Muscular Strength, Courage, Siblings, Executive Action",
        "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः ॥",
        "remedy_en": "Keep southern boundary walls higher and heavier than northern walls. Plant Neem or Ashoka trees along the perimeter. Install Mars Yantra.",
        "remedy_hi": "दक्षिण की दीवारें उत्तर से ऊँची और भारी रखें। दक्षिण द्वार दोष पर तांबे की पट्टी व मंगल यंत्र स्थापित करें। नीम या अशोक का वृक्ष लगाएं।",
        "non_destructive_remedy": "दक्षिण दिशा में 3 ब्रास या कॉपर हेलिक्स लगाएं। यदि दक्षिण दिशा खुली हो तो वहां भारी वजनदार वस्तुएं अथवा लाल त्रिकोण पिरामिड रखें।",
        "shastra_shloka": "याम्ये यमः शमं कुर्याद् विश्रामं च विनिर्दिशेत् । उच्चता भारसंयुक्ता सर्वकल्याणकारिणी ॥"
    },
    "South-West": {
        "hindi": "नैऋत्य (Nairutya)",
        "lord": "Rahu",
        "deity": "Nirriti / Pitrus (पितृ देव)",
        "element": "Prithvi (स्थिर पृथ्वी तत्व)",
        "degree_range": "202.5° – 247.5° (मध्य 225°)",
        "associated_house": "८म व १२वां भाव (आयु, स्थायित्व, मोक्ष व अवचेतन)",
        "vastu_purusha_organ": "वास्तु पुरुष की जांघ, गुदा व पैर",
        "gemstone": "गोमेद (Hessonite)",
        "metal": "रांगा / सीसा (Lead) व भारी पीतल",
        "botanical": "दूर्वा, चंदन, भारी बड़े छायादार वृक्ष",
        "color_therapy": "पीला-भूरा, मिट्टी का रंग, खाकी, सरसों पीला (Earthy Brown / Ochre Yellow)",
        "symptoms_of_defect": "पारिवारिक अस्थिरता, अकाल मृत्यु भय, गृहस्वामी का कमजोर स्वास्थ्य, निर्णय दोष, कोर्ट कचहरी, असहनीय ऋण।",
        "ideal_uses": ["मास्टर बेडरूम (Master Bedroom)", "भारी तिजोरी / अलमारी", "सीढ़ियां", "भवन का सर्वाधिक ऊँचा भाग"],
        "avoid": ["मुख्य प्रवेश द्वार", "बोरवेल / भूमिगत पानी", "शौचालय", "कटौतियां (Cuts) या बालकनी"],
        "chakra_organ": "Stability, Lifespan, Nervous Balance, Ancestral Blessings, Authority of Head of Family",
        "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः ॥",
        "remedy_en": "Keep South-West corner completely solid, highest, and heaviest. Install Lead helix/pyramids and place heavy solid brass elephants.",
        "remedy_hi": "नैऋत्य कोण को घर का सबसे भारी और ऊँचा कोना बनाएं। यहाँ बोरिंग, गड्ढा या शौचालय कभी न बनाएं। दोष निवारण हेतु राहु यंत्र एवं लेड पिरामिड लगाएं।",
        "non_destructive_remedy": "नैऋत्य में टॉयलेट या कट होने पर 3 लेड (सीसा) हेलिक्स जमीन में दबाएं तथा भारी ब्रास नंदी अथवा हाथी का जोड़ा रखें।",
        "shastra_shloka": "नैऋत्यां नैऋतो रक्षो भारं तत्र समाचरेत् । गभीरं न खनेद् भूमिं स्थिरत्वं तत्र संस्थितम् ॥"
    },
    "West": {
        "hindi": "पश्चिम (Pashchima)",
        "lord": "Saturn",
        "deity": "Varuna (वरुण देव)",
        "element": "Vayu / Jala (वायु व जल समन्वय)",
        "degree_range": "247.5° – 292.5° (मध्य 270°)",
        "associated_house": "७म व ११वां भाव (व्यापार, साझेदारी, लाभ व कर्मफल)",
        "vastu_purusha_organ": "वास्तु पुरुष का उदर व बायां घुटना",
        "gemstone": "नीलम (Blue Sapphire) / जामुनिया",
        "metal": "लोहा (Iron) व स्टेनलेस स्टील",
        "botanical": "शमी (खेजड़ी), पीपल (भवन से दूर), नीले पुष्प",
        "color_therapy": "गहरा नीला, जामुनी, स्लेटी, चारकोल (Navy Blue / Charcoal Gray)",
        "symptoms_of_defect": "गठिया, जोड़ों का दर्द, व्यापार में धोखा, कर्म का फल न मिलना, अकारण विलंब, सेवकों का विद्रोह, असंतोष।",
        "ideal_uses": ["भोजन कक्ष (Dining Room)", "अध्ययन कक्ष (Study)", "ओवरहेड पानी की टंकी", "स्टाफ क्वार्टर"],
        "avoid": ["उत्तर-पश्चिम मुखी मुख्य द्वार", "रसोईघर", "खुला नीचा स्थान", "पानी का भूमिगत गड्ढा"],
        "chakra_organ": "Bones, Joints, Discipline, Long-term Gains, Longevity, Karma Realization",
        "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः ॥",
        "remedy_en": "Plant Shami tree on a Saturday. Place heavy overhead water storage tanks here. Install an energised Shani Yantra on western wall.",
        "remedy_hi": "पश्चिम दिशा में शमी का वृक्ष शनिवार या शनि होरा में लगाएं। लोहे का शनि यंत्र अथवा नीले क्रिस्टल स्थापित करें। ओवरहेड वाटर टैंक लगाएं।",
        "non_destructive_remedy": "पश्चिम दिशा के दोष पर स्टील या ब्रास हेलिक्स लगाएं और शनिवार को सरसों के तेल का दीपक पश्चिम दिशा में प्रज्वलित करें।",
        "shastra_shloka": "वारुणे वरुणो दद्याद् भोजनं पानमेव च । लाभस्थानं विदुः प्राज्ञाः पश्चिमे स्थिरवृद्धये ॥"
    },
    "North-West": {
        "hindi": "वायव्य (Vayavya)",
        "lord": "Moon",
        "deity": "Vayu Dev (वायु देव)",
        "element": "Air (गतिशील वायु तत्व)",
        "degree_range": "292.5° – 337.5° (मध्य 315°)",
        "associated_house": "३य व १२वां भाव (यात्रा, गति, मनोभाव व संबंध)",
        "vastu_purusha_organ": "वास्तु पुरुष की बाईं कोहनी व पसलियां",
        "gemstone": "मोती (Natural Pearl) / मूनस्टोन",
        "metal": "चांदी (Pure Silver) व कांस्य",
        "botanical": "पलाश (Dhak), चमेली, मोगरा, सफेद फूल",
        "color_therapy": "दूधिया सफेद, पर्ल व्हाइट, चमकदार सिल्वर (Milk White / Pearl Silver)",
        "symptoms_of_defect": "अनिद्रा, अत्यधिक मानसिक चंचलता व अवसाद, माता का अस्वस्थ रहना, यात्राओं में हानि, अनपेक्षित कानूनी उलझनें।",
        "ideal_uses": ["अतिथि कक्ष (Guest Room)", "तैयार माल का स्टॉक (Finished Goods)", "अविवाहित कन्याओं का शयनकक्ष", "गैरेज"],
        "avoid": ["मास्टर बेडरूम", "अत्यधिक भारी कंक्रीट निर्माण", "किचन चूल्हा", "अवरुद्ध वेंटिलेशन"],
        "chakra_organ": "Mind, Mental Peace, Fluids, Mother's Health, Travel, Supportive Relationships",
        "mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः ॥",
        "remedy_en": "Ensure unrestricted cross-ventilation. Decorate with white/pearl silver tones. Install Chandra Yantra and brass wind chimes.",
        "remedy_hi": "वायव्य दिशा में हवा का आवागमन सुगम रखें। श्वेत रंग, चांदी का स्वास्तिक या बहते पानी का छोटा फव्वारा लगाएं। चंद्र यंत्र स्थापित करें।",
        "non_destructive_remedy": "वायव्य में 3 पीतल की विंड चाइम (Wind Chimes) लटकाएं। वायव्य कोण में सफेद संगमरमर की चौकी पर शंख में गंगाजल भरकर रखें।",
        "shastra_shloka": "वायव्ये मारुतः स्थानं गतिशीलं विधीयते । धान्यागारं च कुर्याद्धि पशुस्थानं तथैव च ॥"
    },
    "North": {
        "hindi": "उत्तर (Uttara)",
        "lord": "Mercury",
        "deity": "Kubera / Lord Vishnu",
        "element": "Jala / Wealth (जल व धन तत्व)",
        "degree_range": "337.5° – 22.5° (मध्य 0°/360°)",
        "associated_house": "४था व ११वां भाव (बुध, कुबेर व सुख-संपत्ति)",
        "vastu_purusha_organ": "वास्तु पुरुष का हृदय व वक्षस्थल",
        "gemstone": "पन्ना (Emerald) / हरा ओनेक्स",
        "metal": "कांसा व पीतल (Bronze / Brass)",
        "botanical": "अपामार्ग, तुलसी, मनी प्लांट, हरसिंगार",
        "color_therapy": "हल्का हरा, पिस्ता, समुद्री हरा, पुदीना (Pista Green / Sea Green)",
        "symptoms_of_defect": "व्यापार में अचानक रुकावट, वाणी दोष, नए अवसर न मिलना, फेफड़े व स्नायु विकार, संचित कोष का विनाश।",
        "ideal_uses": ["तिजोरी / कैश लॉकर (उत्तर मुखी)", "अकाउंट्स / अध्ययन कक्ष", "हरा-भरा लॉन / खुला बरामदा", "तुलसी वाटिका"],
        "avoid": ["शौचालय व सेप्टिक टैंक", "सीढ़ियां", "भारी कबाड़ / स्टोरेज", "ऊंची ठोस दीवारें"],
        "chakra_organ": "Intellect, Communication, Financial Growth, Nervous System, Business Trade",
        "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः ॥",
        "remedy_en": "Keep northern zone light, open, and vibrant green. Place safe facing North. Install a consecrated Kubera Yantra or Budha Yantra.",
        "remedy_hi": "उत्तर दिशा कुबेर का स्थान है। यहाँ तिजोरी उत्तर दिशा की ओर खुलती हुई रखें। तुलसी का पौधा, बुध यंत्र व कुबेर यंत्र लगाएं।",
        "non_destructive_remedy": "यदि उत्तर दिशा भारी या दोषयुक्त हो तो वहां ब्रास की सील पट्टी लगाएं तथा ग्रीन एवेंच्यूरिन पिरामिड व कुबेर पात्र स्थापित करें।",
        "shastra_shloka": "कौबेरे तु कुबेरः स्यात् सर्वद्रव्यप्रदायकः । खुला जलं च तत्रैव धनवृद्धिकरं परम् ॥"
    },
    "North-East": {
        "hindi": "ईशान (Ishanya)",
        "lord": "Jupiter",
        "deity": "Shiva / Ishana (देवाधिदेव महादेव)",
        "element": "Jala / Ether (पवित्र जल व आकाश)",
        "degree_range": "22.5° – 67.5° (मध्य 45°)",
        "associated_house": "५म व ९वां भाव (धर्म, सात्विक बुद्धि व गुरु कृपा)",
        "vastu_purusha_organ": "वास्तु पुरुष का सिर, शिखा व ललाट",
        "gemstone": "पीला पुखराज (Yellow Sapphire)",
        "metal": "स्वर्ण व पीतल (Gold / Brass)",
        "botanical": "केला, पीपल, चंपा, तुलसी, चंदन",
        "color_therapy": "हल्का पीला, नींबू पीला, स्वर्णिम, शुभ्र श्वेत (Lemon Yellow / Bright White)",
        "symptoms_of_defect": "संतान कष्ट, मानसिक अवसाद, भ्रम, पूजा-पाठ में मन न लगना, वंश वृद्धि में बाधा, घोर दरिद्रता व ज्ञान शून्यता।",
        "ideal_uses": ["पूजा घर / मंदिर (Mandir)", "ध्यान व योग स्थल", "भूमिगत स्वच्छ जल स्रोत / बोरवेल", "अध्ययन कक्ष"],
        "avoid": ["शौचालय / सेप्टिक टैंक (महादोष)", "रसोईघर (अग्नि)", "भारी स्टोरेज / कबाड़", "सीढ़ियां", "ओवरहेड वाटर टैंक"],
        "chakra_organ": "Spiritual Wisdom, Progeny, Family Harmony, Higher Divine Knowledge, Brain Crown",
        "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः ॥",
        "remedy_en": "Absolute sacred cleanliness. Maintain the lowest elevation of the entire plot here. Install consecrated Guru Yantra and keep Ganga Jal.",
        "remedy_hi": "ईशान कोण भगवान शिव और बृहस्पति का पावन स्थान है। यहाँ पूजा घर या भूमिगत जल स्रोत रखें। यहाँ शौचालय या भारी सीढ़ी महादोष उत्पन्न करती है।",
        "non_destructive_remedy": "ईशान में टॉयलेट या भारी सीढ़ी का दोष होने पर पीतल का गुरु यंत्र, स्फटिक श्रीयंत्र एवं 24 घंटे तांबे के पात्र में गंगाजल भरकर रखें।",
        "shastra_shloka": "ईशाने च महादेवो जलस्थानं प्रशस्यते । देवस्थानं च तत्रैव सर्वसिद्धिकरं भवेत् ॥"
    },
    "Center": {
        "hindi": "ब्रह्मस्थान (Brahmasthan)",
        "lord": "Cosmic (Lord Brahma)",
        "deity": "Lord Brahma (सृष्टिकर्ता ब्रह्मा)",
        "element": "Akasha (विस्तृत आकाश तत्व)",
        "degree_range": "केंद्रीय 9 पद (Central Cosmic Core)",
        "associated_house": "समस्त केंद्र भाव (१, ४, ७, १० - विष्णु स्थान)",
        "vastu_purusha_organ": "वास्तु पुरुष की नाभि व उदर केंद्र",
        "gemstone": "नवरत्न (Navaratna)",
        "metal": "अष्टधातु व शुद्ध सोना (Ashtadhatu / Gold)",
        "botanical": "तुलसी क्यारी, सुगंधित पुष्प पात्र",
        "color_therapy": "पारदर्शी, प्राकृतिक प्रकाश, स्फटिक श्वेत (Crystal Clear / Sky White)",
        "symptoms_of_defect": "गृहस्वामी को हृदय व उदर विकार, पूरे परिवार में मानसिक अशान्ति, धन का निरंतर पलायन, जीवन में संतुलनहीनता।",
        "ideal_uses": ["खुला आंगन / चौक (Courtyard)", "हल्का केंद्रीय हॉल", "प्राकृतिक प्रकाश (Skylight)", "ध्यान स्थान"],
        "avoid": ["खंभे / पिलर्स (Pillars)", "भारी बीम (Heavy Beams)", "शौचालय", "रसोई", "भूमिगत गड्ढा या बोरिंग"],
        "chakra_organ": "Universal Cosmic Energy, Life Equilibrium, Navel of Vastu Purusha",
        "mantra": "ॐ नमो भगवते वासुदेवाय ॥",
        "remedy_en": "Keep the exact architectural center of the building completely open, clean, and unweighted. Allow natural daylight if possible.",
        "remedy_hi": "घर के मध्य भाग को ब्रह्मस्थान कहते हैं। इसे पूर्णतः खुला, प्रकाशयुक्त और भारमुक्त रखें। यहां कोई खंभा या गड्ढा न बनाएं।",
        "non_destructive_remedy": "यदि ब्रह्मस्थान में बीम या दीवार हो तो बीम के दोनों ओर कॉपर हेलिक्स लगाएं तथा केंद्र में स्फटिक श्रीयंत्र अथवा ब्रास चक्र स्थापित करें।",
        "shastra_shloka": "ब्रह्मस्थाने स्वयं ब्रह्मा मध्यभागे प्रतिष्ठितः । भारस्तत्र न कर्तव्यः स्तम्भो वाऽपि जलाशयः ॥"
    }
}


class VastuJyotishEngine:
    """Engine mapping natal chart strengths and afflictions to architectural Vastu layout."""

    def __init__(self, chart: KundaliChart):
        self.chart = chart

    def evaluate_vastu_zones(self) -> List[Dict[str, Any]]:
        """
        Evaluates each direction based on the native's chart:
        - Planetary status (Exalted, Own, Friendly, Enemy, Debilitated, Combust)
        - Dusthana placement (6th, 8th, 12th)
        - Directional strength (Digbala)
        - House rulership in chart
        - Vastu zone harmony score (0 to 100)
        - Specific architectural defects and comprehensive remedies
        """
        results = []

        def get_digbala_info(p_name: str, h_num: int) -> tuple[str, int]:
            if p_name in ["Sun", "Mars"]:
                if h_num == 10: return "पूर्ण दिग्बली (100% Digbala)", 15
                elif h_num in [9, 11, 1]: return "आंशिक दिग्बली (60-80%)", 8
                elif h_num == 4: return "दिग्बल शून्य (0% - निर्बली)", -12
                else: return "सामान्य दिग्बल (40-60%)", 0
            elif p_name in ["Jupiter", "Mercury"]:
                if h_num == 1: return "पूर्ण दिग्बली (100% Digbala)", 15
                elif h_num in [4, 5, 9, 10]: return "आंशिक दिग्बली (60-80%)", 8
                elif h_num == 7: return "दिग्बल शून्य (0% - निर्बली)", -12
                else: return "सामान्य दिग्बल (40-60%)", 0
            elif p_name == "Saturn":
                if h_num == 7: return "पूर्ण दिग्बली (100% Digbala)", 15
                elif h_num in [6, 8, 10, 11]: return "आंशिक दिग्बली (60-80%)", 8
                elif h_num == 1: return "दिग्बल शून्य (0% - निर्बली)", -12
                else: return "सामान्य दिग्बल (40-60%)", 0
            elif p_name in ["Moon", "Venus"]:
                if h_num == 4: return "पूर्ण दिग्बली (100% Digbala)", 15
                elif h_num in [1, 5, 7, 9]: return "आंशिक दिग्बली (60-80%)", 8
                elif h_num == 10: return "दिग्बल शून्य (0% - निर्बली)", -12
                else: return "सामान्य दिग्बल (40-60%)", 0
            elif p_name == "Rahu":
                if h_num in [3, 6, 10, 11]: return "उपचय प्रबल बल (Upachaya Strength)", 10
                elif h_num in [8, 12]: return "त्रिक भाव पीड़ित (Dusthana Affliction)", -10
                else: return "सामान्य स्थिति (Neutral)", 0
            return "तटस्थ", 0

        for direction, meta in VASTU_DIRECTIONS.items():
            lord_name = meta["lord"]
            if lord_name == "Cosmic (Lord Brahma)" or lord_name == "All":
                # Compute Brahmasthan score from Kendra strength
                kendra_planets = [p for p, pos in self.chart.planets.items() if pos.house_from_lagna in [1, 4, 7, 10]]
                k_score = 80 + min(15, len(kendra_planets) * 4)
                results.append({
                    "direction": direction,
                    "hindi": meta["hindi"],
                    "lord": "Cosmic (Lord Brahma)",
                    "planet_symbol": "🕉️",
                    "sign_name": "सर्वव्यापी (All Signs)",
                    "degree_str": "नाभि केंद्र",
                    "house": "केन्द्र (1, 4, 7, 10)",
                    "element": meta["element"],
                    "status": "दिव्य चेतना (Cosmic)",
                    "is_combust": False,
                    "is_retrograde": False,
                    "digbala": "अक्षय ब्रह्म बल",
                    "score": min(100, k_score),
                    "defect_risk": "Harmonious" if k_score >= 75 else "Moderate Risk",
                    "meta": meta
                })
                continue

            pos: Optional[PlanetPosition] = self.chart.planets.get(lord_name)
            if not pos:
                continue

            status = pos.dignity.capitalize()
            score = 65.0

            # Dignity adjustments
            if status in ["Exalted", "उच्च"]:
                score += 25.0
            elif status in ["Own", "स्वराशि"]:
                score += 18.0
            elif status in ["Moolatrikona", "मूलत्रिकोण"]:
                score += 15.0
            elif status in ["Friend", "मित्र"]:
                score += 8.0
            elif status in ["Debilitated", "नीच"]:
                score -= 30.0
            elif status in ["Enemy", "Great_enemy", "शत्रु"]:
                score -= 15.0

            # Digbala adjustment
            dig_lbl, dig_pts = get_digbala_info(lord_name, pos.house_from_lagna)
            score += dig_pts

            # Dusthana check
            if pos.house_from_lagna in [6, 8, 12]:
                score -= 14.0
            elif pos.house_from_lagna in [1, 4, 5, 9, 10]:
                score += 10.0

            # Combustion penalty
            if pos.is_combust:
                score -= 16.0

            # Retrograde influence
            if pos.is_retrograde:
                if lord_name in ["Jupiter", "Venus", "Mercury"]:
                    score += 4.0  # Benefics gain Chesta Bala
                else:
                    score -= 4.0  # Malefics become erratic

            score = max(15.0, min(100.0, score))
            defect_risk = "High Risk" if score < 50 else "Moderate Risk" if score < 75 else "Harmonious"

            results.append({
                "direction": direction,
                "hindi": meta["hindi"],
                "lord": lord_name,
                "planet_symbol": pos.name[:2],
                "sign_name": pos.sign_name,
                "degree_str": f"{pos.sign_degree:.2f}°",
                "house": pos.house_from_lagna,
                "element": meta["element"],
                "status": status,
                "is_combust": pos.is_combust,
                "is_retrograde": pos.is_retrograde,
                "digbala": dig_lbl,
                "score": int(round(score)),
                "defect_risk": defect_risk,
                "meta": meta
            })

        return results
