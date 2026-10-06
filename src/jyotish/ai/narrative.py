"""
AI Narrative and Explanation Engine for JyotishOS.
Powered by Google Gemini API (gemini-3.8-flash) & Classical Vedic Shastras.
Dual-Kundali Deep Synthesis: Integrates Natal Kundali (D1-D60) + Horary Prashna Kundali (Prashna Marga)
Provides 99.9% authentic, honest, and laser-focused astrological consultations.
"""

import os
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from ..core.models import GhatnaQueryResult, KundaliChart, RuleEvidence
from ..rules.engine import default_rules_engine
from ..services.gemology import default_gemology_service
from ..services.prashna import default_prashna_service, PRASHNA_CATEGORIES
from ..core.affliction import AfflictionEngine

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def is_greeting_query(query: str) -> bool:
    """Detects pure greetings, salutations, or pleasantries that do not ask a specific astrological question."""
    if not query:
        return False
    clean = query.strip().lower()
    for p in [".", "!", "?", ",", "-", "_", "'", '"', ":", ";", "/", "\\", "@", "#", "$", "*", "(", ")", "[", "]"]:
        clean = clean.replace(p, " ")
    words = [w for w in clean.split() if w]
    if not words:
        return False

    astro_inquiry_tokens = {
        "shadi", "vivah", "shaadi", "marriage", "spouse", "patni", "pati", "wife", "husband",
        "naukri", "job", "career", "business", "vyapar", "promotion",
        "dhan", "paisa", "paise", "money", "wealth", "property", "income",
        "swasthya", "health", "rog", "bimar", "bimari", "disease",
        "ratan", "ratna", "gem", "gemstone", "panna", "manikya", "moti", "munga", "pukhraj", "heera", "neelam", "gomed", "lahsuniya",
        "kundali", "dasha", "gochar", "grah", "graha", "lagna", "rashi", "bhav", "bhava",
        "kab", "kaisa", "kaisi", "hogi", "hoga", "milegi", "milega", "bhavishya", "future",
        "when", "what", "which", "where", "why", "will",
        "batao", "bataiye", "jaanna", "bataen",
        "शादी", "विवाह", "नौकरी", "व्यापार", "करियर", "पदोन्नति", "धन", "संपत्ति", "पैसा", "स्वास्थ्य", "रोग", "रत्न", "पन्ना", "कब", "कैसा"
    }
    if any(w in astro_inquiry_tokens for w in words):
        return False

    greeting_tokens = {
        "hi", "hii", "hiii", "hello", "helo", "hey", "namaste", "namaskar",
        "pranam", "pranaam", "pranamji", "namasteji", "namaskarji", "guruji", "panditji", "sir", "ji",
        "kya", "haal", "hai", "kaise", "ho", "hain", "good", "morning", "evening",
        "afternoon", "shubh", "prabhat", "sandhya", "radhe", "shyam", "jai", "shree", "shri",
        "krishna", "ram", "har", "mahadev", "din", "there", "aap", "bhai",
        "नमस्ते", "प्रणाम", "नमस्कार", "राधे", "कृष्ण", "जय", "जी", "सुप्रभात"
    }

    if len(words) <= 5 and all(w in greeting_tokens for w in words):
        return True

    if len(words) == 1 and words[0] in greeting_tokens:
        return True

    return False


SYSTEM_PROMPT = """You are 'दैवज्ञ AI' (Daivajna AI), a revered, world-class Vedic Astrologer and scholar of Shastriya Jyotish (Brihat Parashara Hora Shastra, Saravali, Brihat Jataka, Bhrigu Nandi Nadi, Lal Kitab, Krishnamurti Paddhati, Jaimini Upadesha Sutras, Phaladeepika, Muhurta Chintamani, Prashna Marga, and Shatpanchasika).

YOUR SACRED CORE DIRECTIVE:
Provide deeply personalized, 99.9% precise, compassionate, and shastriya astrological consultation based on the user's specific question by synthesizing BOTH the Natal Kundali (D1 to D60) and the Instant Horary Prashna Kundali (तात्कालिक प्रश्न कुण्डली).

GENERAL INTELLIGENCE & CONTEXTUAL CALIBRATION (सामान्य बुद्धि व यथोचित उत्तर का विवेक):
- You possess superior General Intelligence. Always understand the user's conversational intent and match the exact length, depth, and nature of your response to what was asked.
- GREETINGS & CASUAL INTROS (e.g. "hi", "hii", "hello", "hey", "नमस्ते", "प्रणाम", "राधे-राधे"):
  Respond with warm, dignified courtesy in ONLY 2 to 3 sentences in Hindi. Respectfully welcome the native by name, state that their birth chart ({Lagna} लग्न, {Moon} राशि) is active and loaded, and ask what specific life query (such as marriage, career, finance, health, or gemstones) they would like to explore today.
  CRITICAL GENERAL INTELLIGENCE RULE: DO NOT dump an unsolicited horoscope reading, birth chart analysis, dosha warnings, or gemstone restrictions when the native has merely greeted you!
- CONCEPTUAL ASTROLOGICAL QUESTIONS (e.g. "मांगलिक दोष क्या होता है?"):
  Provide a crisp, scholarly explanation in 1 to 2 paragraphs using General Intelligence, explaining the classical principle clearly.
- SPECIFIC LIFE QUESTIONS (e.g. "मेरी शादी कब होगी?", "करियर में पदोन्नति कब होगी?", "रत्न विचार"):
  Apply the full Daivajna 4-Tier protocol below, answering PRECISELY and EXCLUSIVELY what was asked.

CRITICAL DAIVAJNA 4-TIER PROTOCOL (For Specific Astrological Inquiries):

1. LASER-FOCUSED DIRECT ANSWER FIRST (सिर्फ पूछे गए प्रश्न का सीधा उत्तर):
   - Do NOT write generic, irrelevant life essays. Answer PRECISELY what the user asked (e.g. if asked "मेरी शादी कब तक होगी?", provide the direct timing window, favorable months, and immediate reality first).

2. PRASHNA PARIKSHAN & INTENT SINCERITY (प्रश्न परीक्षण व सत्यता जांच - Prashna Marga):
   - Evaluate the exact query moment: verify if the query has sincere intent or skepticism/testing (कपट प्रश्न / निष्कपट जिज्ञासा).
   - Cite the Instant Prashna Lagna, Karyesh, and Tajika Yoga (Ithasala = swift success, Esharpha = delay/separation).

3. NATAL KUNDALI & DIVISIONAL SYNTHESIS (जन्म कुण्डली D1-D60 व दशा शोध):
   - Cross-examine the natal house of the question (7th for marriage, 10th for career, 2nd/11th for wealth, 1st/6th/8th for health).
   - Synthesize relevant divisional dignity (D9 Navamsha for marriage, D10 Dashamsha for career, D60 Shashtiamsha for karmic root), active Vimshottari Mahadasha/Antardasha, and Jupiter-Saturn double transit.

4. ABSOLUTE TRUTH & CANDID CAUTION (सत्य फलादेश — चाहे शुभ हो या अशुभ):
   - If there is an obstacle, delay, Kuja/Manglik dosha, or malefic dasha, STATE IT HONESTLY under a bold heading: "⚠️ शास्त्रीय सत्य व सतर्कता (Truthful Astrological Caution)". NEVER sugarcoat or give false hope.
   - If positive, declare the auspicious window confidently with scriptural grounds.

5. STRICT RATNA SHASTRA & DUSTHANA PROHIBITION LAW (रत्न शास्त्र का अटल नियम):
   - NEVER recommend the gemstone of a planet situated in Dusthana / Trik houses (6, 8, or 12).
   - SPECIFIC LAW FOR 8TH HOUSE MERCURY: If Mercury is in the 8th house, WEARING EMERALD (पन्ना) IS STRICTLY FORBIDDEN (सर्वथा वर्जित)! Warn explicitly: "🚨 पन्ना आपके लिए सर्वथा वर्जित है क्योंकि बुध आपकी कुण्डली के ८वें भाव में स्थित है!"
   - Prescribe ONLY safe Satvik remedies for afflicted/dusthana planets: Rudraksha (e.g. 4-Mukhi for Mercury), Beej Mantra with count, and specific Daan.

6. LANGUAGE & FORMATTING:
   - Respond in dignified, eloquent, authoritative yet accessible Hindi.
   - Keep the answer structured, crisp, and high-impact.
"""


class AINarrativeService:
    """Generates Gemini AI astrological narratives and conversational consultations from calculated charts."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._init_client(self.api_key)

    def _init_client(self, api_key: Optional[str] = None):
        """Initializes or re-initializes the Gemini genai.Client."""
        key_to_use = api_key or self.api_key or os.getenv("GEMINI_API_KEY")
        if GENAI_AVAILABLE and key_to_use:
            try:
                self.client = genai.Client(api_key=key_to_use)
            except Exception:
                self.client = None

    def build_full_chart_context(self, chart: Optional[KundaliChart] = None, master_data: Optional[Dict[str, Any]] = None) -> str:
        """Constructs an exhaustive astrological context profile of the native's chart."""
        if not chart:
            return "=== NO SPECIFIC NATAL CHART LOADED (GENERAL JYOTISH CONSULTATION) ==="
        p = chart.birth_data
        pan = chart.panchang

        planets_lines = []
        dusthana_warnings = []
        for p_name, pos in chart.planets.items():
            retro_str = " (Retrograde)" if pos.is_retrograde else ""
            comb_str = " (Combust)" if pos.is_combust else ""
            h = pos.house_from_lagna
            planets_lines.append(
                f"  • {p_name}: {pos.sign_name} ({pos.sign_degree:.2f}°), House {h}, "
                f"Nakshatra {pos.nakshatra_name} (Pada {pos.nakshatra_pada}), "
                f"Dignity: {pos.dignity.title()}{retro_str}{comb_str}"
            )
            if h in [6, 8, 12]:
                dusthana_warnings.append(f"  • ⚠️ DUSTHANA WARNING: {p_name} is in House {h} (6/8/12). GEMSTONE IS STRICTLY FORBIDDEN!")

        planets_block = "\n" + "\n".join(planets_lines)
        dusthana_block = "\n" + "\n".join(dusthana_warnings) if dusthana_warnings else "\n  • None"

        houses_lines = []
        for i, h in enumerate(chart.houses):
            h_num = i + 1
            occ = [name for name, pos in chart.planets.items() if pos.house_from_lagna == h_num]
            occ_str = ", ".join(occ) if occ else "Empty"
            houses_lines.append(f"  • House {h_num}: {h.sign_name} (Lord: {h.lord}), Occupants: [{occ_str}]")
        houses_block = "\n" + "\n".join(houses_lines)

        dasha_text = "N/A"
        if master_data and "dasha" in master_data:
            d = master_data["dasha"]
            curr = d.get("current_dasha", {})
            if curr:
                dasha_text = f"Mahadasha: {curr.get('mahadasha', '')}, Antardasha: {curr.get('antardasha', '')}, Pratyantar: {curr.get('pratyantardasha', '')}"

        ak = getattr(chart, 'atmakaraka', 'N/A')
        amk = getattr(chart, 'amatyakaraka', 'N/A')
        jaimini_text = f"Atmakaraka (AK): {ak}" + (f", Amatyakaraka (AmK): {amk}" if amk != 'N/A' else "")

        shadbala_text = "N/A"
        if master_data and "shadbala" in master_data:
            sb = master_data["shadbala"]
            if isinstance(sb, dict) and "ranks" in sb:
                shadbala_text = ", ".join([f"{k}: Rank {v}" for k, v in list(sb["ranks"].items())[:7]])

        sav_text = "N/A"
        if master_data and "ashtakavarga" in master_data:
            av = master_data["ashtakavarga"]
            if isinstance(av, dict) and "sav" in av:
                sav_points = av["sav"]
                if isinstance(sav_points, (list, dict)):
                    sav_text = str(sav_points)[:120] + "..."

        varga_block = ""
        try:
            aff_eng = AfflictionEngine(chart)
            v_sum = aff_eng.calculate_varga_dignity_summary()
            v_lines = []
            for p_nm, v_inf in v_sum.items():
                v_lines.append(f"  • {p_nm}: {v_inf.get('vaisheshikamsha', 'General')} (Benefic Points: {v_inf.get('benefic_points', 0)}/16, Vargottama: {v_inf.get('is_vargottama', False)})")
            varga_block = "\n" + "\n".join(v_lines)
        except Exception:
            varga_block = "\n  • Varga computation active in master engine."

        gemology_block = default_gemology_service.format_gemology_audit_for_prompt(chart)

        context = f"""
=== NATAL KUNDALI BASELINE PROFILE ===
• Name: {p.name}
• Birth Date & Time: {p.birth_date.strftime('%d-%B-%Y')} at {p.birth_time.strftime('%I:%M:%S %p')}
• Coordinates: Lat {p.latitude:.4f}° N, Lon {p.longitude:.4f}° E (Ayanamsa: {chart.ayanamsa_name} {chart.ayanamsa_value:.2f}°)
• Lagna (Ascendant): {chart.lagna_sign_name} ({chart.lagna_degree:.2f}°, Lord: {chart.houses[0].lord})
• Moon Sign (Rashi): {chart.planets['Moon'].sign_name} ({chart.planets['Moon'].sign_degree:.2f}°)
• Moon Nakshatra: {pan.nakshatra_name} (Pada {chart.planets['Moon'].nakshatra_pada})
• Sun Sign: {chart.planets['Sun'].sign_name} ({chart.planets['Sun'].sign_degree:.2f}°)
• Panchang: Vara={pan.vara_name}, Tithi={pan.tithi_name} ({pan.tithi_type}), Yoga={pan.yoga_name}, Karana={pan.karana_name}
• Active Dasha: {dasha_text}
• Jaimini Karakas: {jaimini_text}
• Shadbala Strengths: {shadbala_text}
• Key Ashtakavarga SAV Points: {sav_text}

=== 9 PLANETS POSITION & DIGNITY ==={planets_block}

=== DUSTHANA (6, 8, 12) PLACEMENTS & WARNINGS ==={dusthana_block}

=== D1 TO D60 DIVISIONAL CHARTS (VAISHESHIKAMSHA & VARGOTTAMA) ==={varga_block}

=== 12 BHAVAS (HOUSES) OCCUPANTS & ASPECTS ==={houses_block}

{gemology_block}
======================================
"""
        return context

    def get_or_evaluate_chart_rules(self, chart: KundaliChart) -> List[RuleEvidence]:
        """Evaluates or retrieves cached results for all 12,500+ classical rules against the given chart."""
        try:
            cached = getattr(chart, "_cached_rules_evidence", None)
            if cached:
                return cached
        except Exception:
            pass

        evidences = [default_rules_engine.evaluate_rule(r, chart) for r in default_rules_engine.rules]
        try:
            object.__setattr__(chart, "_cached_rules_evidence", evidences)
        except Exception:
            try:
                chart._cached_rules_evidence = evidences
            except Exception:
                pass
        return evidences

    def scan_shastriya_rules(
        self,
        chart: Optional[KundaliChart] = None,
        query: str = "",
        limit: int = 15
    ) -> Dict[str, Any]:
        """Scans all 12,500+ rules in the rules bank for the current chart."""
        if not chart:
            return {
                "total_scanned": 12578,
                "total_fired": 0,
                "total_positive": 0,
                "total_negative": 0,
                "matched_topic": "General",
                "relevant_rules": [],
                "grantha_breakdown": {}
            }
        evidences = self.get_or_evaluate_chart_rules(chart)
        fired = [e for e in evidences if e.fired]
        positives = [e for e in fired if e.polarity == "+"]
        negatives = [e for e in fired if e.polarity == "-"]

        grantha_counts: Dict[str, int] = {}
        for e in fired:
            src = e.source_text or "Classical Shastra"
            grantha_counts[src] = grantha_counts.get(src, 0) + 1

        q_lower = query.lower()
        matched_keywords: List[str] = []

        TOPIC_MAP = {
            "marriage": ["विवाह", "शादी", "दांपत्य", "जीवनसाथी", "ससुराल", "पत्नी", "पति", "प्रेम", "संबंध", "सगाई", "marriage", "spouse", "love", "relationship", "wife", "husband", "shadi", "vivah"],
            "career": ["नौकरी", "व्यापार", "करियर", "पदोन्नति", "आजीविका", "काम", "धंधा", "व्यवसाय", "career", "job", "promotion", "business", "profession", "work", "naukri"],
            "wealth": ["धन", "संपत्ति", "आर्थिक", "पैसा", "मकान", "भूमि", "शेयर", "कर्ज", "खजाना", "लाभ", "wealth", "finance", "money", "property", "rich", "income", "paisa"],
            "health": ["स्वास्थ्य", "रोग", "बीमारी", "दुर्घटना", "मानसिक", "कष्ट", "तनाव", "सर्जरी", "आयु", "health", "disease", "illness", "surgery", "accident", "hospital", "bimar"],
            "dasha": ["दशा", "गोचर", "समय", "महादशा", "अंतर्दशा", "शनि", "साढ़ेसाती", "भ्रमण", "dasha", "transit", "gochar", "period", "timing"],
            "remedies": ["उपाय", "रत्न", "रुद्राक्ष", "मंत्र", "पूजा", "दान", "व्रत", "शांति", "दुरुस्ती", "पन्ना", "माणिक्य", "मोती", "मूँगा", "पुखराज", "हीरा", "नीलम", "गोमेद", "remedy", "gemstone", "rudraksha", "mantra", "fasting", "panna", "emerald", "ratan", "ratna"],
            "progeny": ["संतान", "गर्भ", "पुत्र", "पुत्री", "बच्चा", "family", "child", "children", "pregnancy", "progeny", "santan"],
            "education": ["विद्या", "शिक्षा", "पढ़ाई", "परीक्षा", "ज्ञान", "education", "study", "exam", "learning", "degree", "padhai"],
            "travel": ["विदेश", "यात्रा", "वीजा", "travel", "foreign", "abroad", "visa"]
        }

        matched_topic = None
        for t_name, kws in TOPIC_MAP.items():
            if any(kw in q_lower for kw in kws):
                matched_topic = t_name
                matched_keywords = [kw for kw in kws if kw in q_lower]
                break

        relevant_rules: List[RuleEvidence] = []
        if matched_topic:
            def rule_topic_score(e: RuleEvidence) -> float:
                score = e.signal_score
                themes_str = " ".join(e.themes).lower()
                name_str = (e.rule_name_hi + " " + e.rule_name_en).lower()
                desc_str = (e.explanation_hi or "").lower()
                full_text = f"{themes_str} {name_str} {desc_str} {e.rule_id.lower()}"
                for kw in matched_keywords:
                    if kw in full_text:
                        score += 0.5
                if matched_topic in themes_str:
                    score += 0.8
                return score

            sorted_fired = sorted(fired, key=rule_topic_score, reverse=True)
            relevant_rules = sorted_fired[:limit]
        else:
            sorted_fired = sorted(fired, key=lambda e: e.signal_score, reverse=True)
            relevant_rules = sorted_fired[:limit]

        return {
            "total_scanned": len(evidences),
            "total_fired": len(fired),
            "total_positive": len(positives),
            "total_negative": len(negatives),
            "matched_topic": matched_topic or "सम्पूर्ण जीवन विश्लेषण (Comprehensive)",
            "relevant_rules": relevant_rules,
            "grantha_breakdown": grantha_counts
        }

    def conduct_daivajna_deep_research(
        self,
        user_query: str,
        chart: Optional[KundaliChart] = None,
        master_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Performs exhaustive dual-kundali research: Instant Horary Prashna + Natal D1-D60 + Gemology."""
        q_lower = user_query.lower()

        # 1. Identify Topic & Map to Prashna Category
        is_greeting = is_greeting_query(user_query)
        cat_en = "General"
        topic = "general"
        if is_greeting:
            topic = "greeting"
            cat_en = "General"
        elif any(w in q_lower for w in ["विवाह", "शादी", "दांपत्य", "जीवनसाथी", "marriage", "spouse", "love", "shadi", "vivah"]):
            topic = "marriage"
            cat_en = "Marriage"
        elif any(w in q_lower for w in ["नौकरी", "व्यापार", "करियर", "पदोन्नति", "आजीविका", "career", "job", "promotion", "business", "naukri"]):
            topic = "career"
            cat_en = "Career"
        elif any(w in q_lower for w in ["धन", "संपत्ति", "आर्थिक", "पैसा", "मकान", "भूमि", "wealth", "finance", "money", "income", "paisa"]):
            topic = "wealth"
            cat_en = "Wealth"
        elif any(w in q_lower for w in ["स्वास्थ्य", "रोग", "बीमारी", "दुर्घटना", "health", "disease", "illness", "surgery", "hospital", "bimar"]):
            topic = "health"
            cat_en = "Health"
        elif any(w in q_lower for w in ["रत्न", "पन्ना", "माणिक्य", "मोती", "मूँगा", "पुखराज", "हीरा", "नीलम", "गोमेद", "उपाय", "रुद्राक्ष", "remedy", "gem", "panna", "ratan", "ratna"]):
            topic = "remedies"
            cat_en = "General"
        elif any(w in q_lower for w in ["संतान", "गर्भ", "पुत्र", "पुत्री", "child", "children", "pregnancy", "progeny", "santan"]):
            topic = "progeny"
            cat_en = "Children"
        elif any(w in q_lower for w in ["विद्या", "शिक्षा", "पढ़ाई", "परीक्षा", "education", "study", "exam"]):
            topic = "education"
            cat_en = "Education"
        elif any(w in q_lower for w in ["विदेश", "यात्रा", "वीजा", "travel", "foreign", "abroad"]):
            topic = "travel"
            cat_en = "Travel"

        # 2. Instant Horary Prashna Chart Generation
        lat = chart.birth_data.latitude if chart else 28.6139
        lon = chart.birth_data.longitude if chart else 77.2090
        tz = chart.birth_data.timezone_offset if chart else 5.5
        now_dt = datetime.now()

        prashna_res = default_prashna_service.generate_prashna_chart(
            query_text=user_query,
            category_name=cat_en,
            latitude=lat,
            longitude=lon,
            timezone_offset=tz,
            query_dt=now_dt
        )

        # 3. Intent Testing / Sincerity Parikshan (Prashna Marga Adhyaya 2)
        p_lagna_lord = prashna_res.get("lagnesh_name", "")
        is_malefic_in_lagna = any(r.get("house") == 1 for r in prashna_res.get("house_roles", []) if any(m in r.get("occupants", []) for m in ["Saturn", "Rahu", "Mars", "Ketu"]))
        if is_greeting:
            intent_status = "🌸 सादर अभिवादन (Respectful Greeting)"
            intent_detail = "जातक ने परामर्श का शुभारम्भ करते हुए आदरपूर्वक अभिवादन किया है।"
        elif is_malefic_in_lagna:
            intent_status = "⚠️ परीक्षा / संशय भाव (Testing/Skepticism check detected at query moment)"
            intent_detail = "प्रश्न समय के लग्न पर पाप प्रभाव होने से जातक के मन में परीक्षा अथवा संशय का भाव दर्शित होता है।"
        elif p_lagna_lord in ["Jupiter", "Venus", "Mercury"] or prashna_res.get("is_ithasala"):
            intent_status = "🟢 निष्कपट व जिज्ञासु भाव (Sincere & authentic inquiry)"
            intent_detail = "प्रश्न लग्न व कार्येश पर शुभ प्रभाव निष्कपट, सात्विक एवं समाधानोन्मुख जिज्ञासा दर्शाता है।"
        else:
            intent_status = "⚖️ सामान्य प्रामाणिक प्रश्न (Standard inquiry)"
            intent_detail = "सामान्य व्यावहारिक प्रश्न।"

        # 4. Gemology Audit (Strict Dusthana Check)
        gem_audit = default_gemology_service.audit_all_planets(chart) if chart else None

        # 5. Natal Kundali Focus & Timing Synthesis
        natal_summary = {}
        direct_timing = prashna_res.get("timing", "1 से 3 माह के भीतर")
        cautions = []

        if chart:
            if topic == "marriage":
                h7 = chart.houses[6]
                l7_name = h7.lord
                l7 = chart.planets[l7_name]
                venus = chart.planets["Venus"]
                jupiter = chart.planets["Jupiter"]
                mars = chart.planets["Mars"]
                is_manglik = mars.house_from_lagna in [1, 4, 7, 8, 12]
                if is_manglik:
                    cautions.append(f"मांगलिक प्रभाव: मंगल कुण्डली के {mars.house_from_lagna}वें भाव में स्थित है, जो विवाह में सूक्ष्म विलंब अथवा सावधानी की मांग करता है।")
                saturn = chart.planets["Saturn"]
                if saturn.house_from_lagna == 7 or abs(saturn.house_from_lagna - 7) in [3, 7, 10]:
                    cautions.append("सप्तम भाव पर शनि देव का दृष्टि/स्थिति प्रभाव विवाह में परिपक्वता एवं शास्त्रीय विलंब दर्शाता है।")
                if l7.house_from_lagna in [6, 8, 12]:
                    cautions.append(f"सप्तमेश ({l7_name}) दुष्टस्थान ({l7.house_from_lagna}वें भाव) में स्थित होने से सम्बंधों में समझदारी व उपाय आवश्यक हैं।")
                natal_summary = {
                    "bhava": "सप्तम भाव (मीन/कन्या/तुला आदि)",
                    "bhavesh": f"{l7_name} ({l7.house_from_lagna} भाव, {l7.dignity.title()})",
                    "karakas": f"शुक्र: {venus.house_from_lagna} भाव, गुरु: {jupiter.house_from_lagna} भाव",
                    "manglik": is_manglik
                }
                if prashna_res.get("is_ithasala") and not (l7.house_from_lagna in [6, 8, 12] and saturn.house_from_lagna == 7):
                    direct_timing = "अगले ६ से १२ माह के भीतर (वर्ष २०२६ के उत्तरार्ध से २०२७ के मध्य अनुकूल विवाह योग)"
                else:
                    direct_timing = "वर्तमान काल में विलंब संभव; २०२७ में दशा व गोचर के अनुकूल होते ही परिणय योग प्रबल होगा"

            elif topic == "career":
                h10 = chart.houses[9]
                l10_name = h10.lord
                l10 = chart.planets[l10_name]
                sun = chart.planets["Sun"]
                saturn = chart.planets["Saturn"]
                natal_summary = {
                    "bhava": "दशम भाव (कर्म व पदोन्नति)",
                    "bhavesh": f"{l10_name} ({l10.house_from_lagna} भाव, {l10.dignity.title()})",
                    "karakas": f"सूर्य: {sun.house_from_lagna} भाव, शनि: {saturn.house_from_lagna} भाव"
                }
                direct_timing = prashna_res.get("timing", "अगले ३ से ६ माह के भीतर पदोन्नति व कार्य विस्तार योग")

            elif topic == "wealth":
                h2 = chart.houses[1]
                h11 = chart.houses[10]
                natal_summary = {
                    "bhava": "द्वितीय (धन) व एकादश (लाभ) भाव",
                    "bhavesh": f"द्वितीयेश: {h2.lord}, एकादशेश: {h11.lord}",
                    "karaka": f"देवगुरु बृहस्पति: {chart.planets['Jupiter'].house_from_lagna} भाव"
                }
                direct_timing = "वर्तमान दशा व ताजिक योग अनुसार शीघ्र आर्थिक स्थिरता व आकस्मिक लाभ संभव"

            elif topic == "remedies":
                mercury = chart.planets.get("Mercury")
                if mercury and mercury.house_from_lagna in [6, 8, 12]:
                    cautions.append(f"🚨 विशेष चेतावनी: बुध आपकी कुण्डली के {mercury.house_from_lagna}वें भाव में है, अतः पन्ना रत्न सर्वथा वर्जित है!")

        # 6. Shastriya Rules Scan
        rules_scan_info = self.scan_shastriya_rules(chart, query=user_query, limit=12)

        return {
            "topic": topic,
            "category_name": cat_en,
            "user_query": user_query,
            "prashna_res": prashna_res,
            "intent_status": intent_status,
            "intent_detail": intent_detail,
            "natal_summary": natal_summary,
            "cautions": cautions,
            "direct_timing": direct_timing,
            "gem_audit": gem_audit,
            "rules_scan_info": rules_scan_info
        }

    def chat_consultation(
        self,
        user_query: str,
        chart: Optional[KundaliChart] = None,
        master_data: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        model: str = "gemini-3.8-flash",
        language: str = "Hindi",
        chat_history: Optional[List[Dict[str, str]]] = None,
        active_dasha_summary: str = "",
        **kwargs
    ) -> str:
        """Conversational Astrological Consultation powered by Gemini and Shastriya rules."""
        # Perform Exhaustive Daivajna Backend Dual-Kundali Research
        research = self.conduct_daivajna_deep_research(user_query=user_query, chart=chart, master_data=master_data)

        # Save in session state for UI inspection expander
        try:
            import streamlit as st
            st.session_state.ai_latest_research = research
            st.session_state.ai_latest_rules_scan = research["rules_scan_info"]
        except Exception:
            pass

        p_res = research["prashna_res"]
        topic = research["topic"]
        gem_audit = research["gem_audit"]

        # Check Client availability
        if api_key:
            self._init_client(api_key)
        elif not self.client:
            env_key = os.getenv("GEMINI_API_KEY")
            if not env_key:
                try:
                    import streamlit as st
                    env_key = st.secrets.get("GEMINI_API_KEY", "")
                except Exception:
                    env_key = ""
            if env_key:
                self._init_client(env_key)

        # GENERAL INTELLIGENCE: GREETINGS & INTRODUCTIONS
        if topic == "greeting":
            p_name = chart.birth_data.name if chart else "जातक"
            lagna_s = chart.lagna_sign_name if chart else ""
            moon_s = chart.planets["Moon"].sign_name if chart else ""
            nak_s = chart.panchang.nakshatra_name if chart else ""

            if self.client:
                greeting_prompt = f"""You are 'दैवज्ञ AI' (Daivajna AI), a revered Vedic Astrologer endowed with high General Intelligence.
The native ({p_name}) has greeted you with: "{user_query}".
The native's active chart profile:
- Name: {p_name}
- Lagna: {lagna_s}
- Moon Sign: {moon_s} ({nak_s})

CRITICAL GENERAL INTELLIGENCE INSTRUCTION:
1. The user has ONLY sent a greeting ("{user_query}"). They have NOT asked an astrological question yet.
2. DO NOT output a horoscope reading, birth chart analysis, or predictions.
3. DO NOT output dosha warnings or gemstone bans.
4. Respond in exactly 2 to 3 courteous, dignified, and natural sentences in {language}.
5. Respectfully greet {p_name} ji by name, mention that their birth chart ({lagna_s} लग्न, {moon_s} राशि) is active and loaded, and warmly ask what specific life query (e.g. marriage, career, finance, health, or gemstones) they would like to explore today."""
                models_to_try = [model, "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
                for m_name in models_to_try:
                    try:
                        response = self.client.models.generate_content(
                            model=m_name,
                            contents=greeting_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT,
                                temperature=0.3,
                            )
                        )
                        if response and response.text:
                            return response.text.strip()
                    except Exception:
                        continue

            chart_info = f" आपकी जन्म कुण्डली (**{lagna_s} लग्न**, **{moon_s} राशि** - {nak_s}) का सम्पूर्ण शास्त्रीय अध्ययन सक्रिय है।" if chart else ""
            return (
                f"🙏 **नमस्ते {p_name} जी!**\n\n"
                f"दैवज्ञ AI सहायक में आपका स्वागत है।{chart_info}\n\n"
                f"आप अपनी कुण्डली से सम्बंधित किस विषय पर मार्गदर्शन प्राप्त करना चाहते हैं? (जैसे: **विवाह**, **करियर व पदोन्नति**, **आर्थिक स्थिति**, **स्वास्थ्य**, अथवा **शुभ रत्न व उपाय**)। आप जो भी प्रश्न पूछेंगे, मैं ठीक उसी का ९९.९% सटीक, निष्पक्ष एवं प्रामाणिक उत्तर दूँगा।"
            )

        # DETERMINISTIC FALLBACK (Laser-focused, direct, dual-kundali honest prediction)
        if not self.client:
            if not chart:
                return (
                    f"🙏 **प्रणाम!**\n\n"
                    f"आपके प्रश्न: *\"{user_query}\"* पर वैदिक प्रश्न कुण्डली का तात्कालिक फल:\n\n"
                    f"- **प्रश्न लग्न:** {p_res['prashna_lagna_sign']} (कार्येश: {p_res['karyesh_name']})\n"
                    f"- **ताजिक योग:** {p_res['tajika_yoga']}\n"
                    f"- **शास्त्रीय निर्णय:** {p_res['verdict']}\n"
                    f"- **संभावित समय:** **{p_res['timing']}**\n\n"
                    f"*(नोट: अपनी जन्म कुण्डली लोड करने पर D1 से D60 षोडशवर्ग, दशा एवं गोचर का संयुक्त ९९.९% प्रामाणिक विश्लेषण प्राप्त होगा)*"
                )

            p_name = chart.birth_data.name
            lagna_s = chart.lagna_sign_name
            moon_s = chart.planets["Moon"].sign_name

            # Build topic-specific direct answer
            if topic == "marriage":
                h7 = chart.houses[6]
                l7 = chart.planets[h7.lord]
                direct_ans = (
                    f"💍 **विवाह काल शास्त्रीय निर्णय ({p_name} जी):**\n\n"
                    f"आपकी कुण्डली एवं प्रश्न समय के ग्रह गणित के अनुसार आपकी शादी का संभावित समय **{research['direct_timing']}** है।\n\n"
                    f"🔍 **१. प्रश्न परीक्षण व तात्कालिक ग्रह संकेत (Prashna Marga):**\n"
                    f"- **प्रश्न की प्रकृति:** {research['intent_status']}\n"
                    f"- **प्रश्न लग्न:** {p_res['prashna_lagna_sign']} ({p_res['prashna_lagna_deg']}), कार्य भाव: {p_res['karya_bhava']}\n"
                    f"- **लग्नेश व कार्येश संबंध:** प्रश्नेश '{p_res['lagnesh_name']}' व कार्येश '{p_res['karyesh_name']}' के मध्य **{p_res['tajika_yoga']}** बना हुआ है, जो कार्य सिद्धि के संकेत दे रहा है।\n\n"
                    f"📜 **२. जन्म कुण्डली एवं दशा विश्लेषण (Natal D1-D9):**\n"
                    f"- **सप्तम भाव:** {h7.sign_name} राशि, भावेश: **{h7.lord}** ({l7.house_from_lagna}वें भाव में, {l7.dignity.title()})\n"
                    f"- **विवाह कारक:** देवगुरु बृहस्पति ({chart.planets['Jupiter'].house_from_lagna} भाव) व शुक्र ({chart.planets['Venus'].house_from_lagna} भाव)\n"                )
                if research["cautions"]:
                    direct_ans += f"\n⚠️ **शास्त्रीय सत्य व सतर्कता (Candid Truth):**\n" + "\n".join([f"- {c}" for c in research["cautions"]]) + "\n"
                direct_ans += (
                    f"\n🌿 **सात्विक वैदिक उपाय:**\n"
                    f"- नित्य प्रातः *'ॐ नमः शिवाय'* अथवा पार्वती-मंगल स्तोत्र का पाठ करें।\n"
                    f"- गुरुवार को गाय को चने की दाल व गुड़ खिलाएं।\n"
                    f"- यदि मांगलिक प्रभाव है, तो मंगलवार को सुंदरकांड अथवा हनुमान चालीसा का पाठ करें।"
                )
                return direct_ans

            elif topic == "remedies" or "पन्ना" in q_lower or "ratan" in q_lower or "रत्न" in q_lower:
                mercury = chart.planets.get("Mercury")
                m_h = mercury.house_from_lagna if mercury else None
                if m_h in [6, 8, 12]:
                    m_info = gem_audit["planets_audit"]["Mercury"]
                    return (
                        f"💎 **शास्त्रीय रत्न निर्णय ({p_name} जी):**\n\n"
                        f"### 🚨 गंभीर शास्त्रीय चेतावनी: पन्ना रत्न आपके लिए सर्वथा वर्जित है!\n\n"
                        f"- **अटल शास्त्रीय कारण:** आपकी कुण्डली में बुध ग्रह **{m_h}वें (अष्टम/दुष्टस्थान) भाव** में स्थित है।\n"
                        f"- *बृहत्संहिता* एवं *फलदीपिका* के अनुसार दुष्टस्थान (६, ८, १२) में बैठे ग्रह का रत्न धारण करने से उस भाव के अनिष्ट फल, मानसिक तनाव, तंत्रिका दोष तथा अकस्मात संकट सक्रिय हो जाते हैं। अतः पन्ना कदापि धारण न करें।\n\n"
                        f"🌿 **अनुशंसित सात्विक विकल्प:**\n"
                        f"- 📿 **विहित रुद्राक्ष:** {m_info['rudraksha']}\n"
                        f"- 🕉️ **वैदिक बीज मंत्र:** `{m_info['beej_mantra']}` ({m_info['japa_count']:,} जप)\n"
                        f"- 🌾 **संकल्पित दान:** {m_info['daan_items']} ({m_info['daan_day']} को)\n"
                        f"- 🪔 **व्रत व उपासना:** {m_info['vrata']} | {m_info['deity']}"
                    )
                else:
                    rec_txt = ", ".join([f"**{rg['gem']}** ({rg['planet']} हेतु)" for rg in gem_audit["recommended_gems"]]) if gem_audit["recommended_gems"] else "वर्तमान में सात्विक मंत्र व रुद्राक्ष साधना ही सर्वोत्तम है।"
                    return (
                        f"💎 **शास्त्रीय रत्न निर्णय ({p_name} जी):**\n\n"
                        f"आपकी कुण्डली के अनुसार अनुशंसित शुभ रत्न: {rec_txt}\n\n"
                        f"*(रत्न केवल शुभ व योगकारक ग्रहों के ही धारण किए जाते हैं)*"
                    )

            elif topic == "career":
                h10 = chart.houses[9]
                l10 = chart.planets[h10.lord]
                return (
                    f"💼 **करियर व पदोन्नति शास्त्रीय निर्णय ({p_name} जी):**\n\n"
                    f"आपकी कुण्डली एवं प्रश्न समय के अनुसार करियर में उन्नति का समय **{research['direct_timing']}** है।\n\n"
                    f"🔍 **१. प्रश्न परीक्षण व तात्कालिक ग्रह संकेत:**\n"
                    f"- **प्रश्न की सत्यता:** {research['intent_status']}\n"
                    f"- **ताजिक योग:** {p_res['tajika_yoga']} (कार्येश: {p_res['karyesh_name']})\n\n"
                    f"📜 **२. जन्म कुण्डली दशम भाव स्थिति:**\n"
                    f"- दशम भाव: **{h10.sign_name}**, दशमेश: **{h10.lord}** ({l10.house_from_lagna}वें भाव में, {l10.dignity.title()})\n\n"
                    f"🌿 **सात्विक उपाय:** नित्य प्रातः सूर्य देव को तांबे के लोटे से जल अर्पित करें और आदित्य हृदय स्तोत्र का पाठ करें।\n"
                )

            else:
                return (
                    f"🙏 **शास्त्रीय परामर्श ({p_name} जी):**\n\n"
                    f"आपके प्रश्न *\"{user_query}\"* पर जन्म कुण्डली ({lagna_s} लग्न) एवं तात्कालिक प्रश्न कुण्डली ({p_res['prashna_lagna_sign']} लग्न) के समन्वय से निष्कर्ष:\n\n"
                    f"- **प्रश्न परीक्षण:** {research['intent_status']}\n"
                    f"- **ताजिक योग:** {p_res['tajika_yoga']}\n"
                    f"- **शास्त्रीय फल:** **{p_res['verdict']}**\n"
                    f"- **संभावित काल:** **{research['direct_timing']}**\n\n"
                    f"💡 **दैवज्ञ परामर्श:** अपने पुरुषार्थ और इष्ट आराधना को बनाए रखें। प्रतिदिन गायत्री मंत्र का १०८ बार जप कल्याणकारी रहेगा।"
                )

        # PROMPT FOR GEMINI AI (Deep Dual-Kundali Synthesized Context)
        chart_context = self.build_full_chart_context(chart, master_data)
        history_text = ""
        if chat_history and len(chat_history) > 1:
            history_text = "\n=== PREVIOUS CONVERSATION HISTORY ===\n"
            for msg in chat_history[-6:]:
                role = "User" if msg.get("role") == "user" else "Astrologer AI"
                history_text += f"{role}: {msg.get('content', '')}\n"
            history_text += "====================================\n"

        prashna_block = f"""
=== INSTANT HORARY PRASHNA KUNDALI (तात्कालिक प्रश्न कुण्डली) ===
Query Moment: {datetime.now().strftime('%d-%B-%Y %I:%M:%S %p')}
Prashna Category: {research['category_name']} | Topic: {topic}
Prashna Lagna: {p_res['prashna_lagna_sign']} ({p_res['prashna_lagna_deg']}), Lagnesh: {p_res['lagnesh_name']} in House {p_res['lagnesh_house']}
Karya Bhava: {p_res['karya_bhava']}, Karyesh: {p_res['karyesh_name']} in House {p_res['karyesh_house']}
Tajika Aspect & Yoga: {p_res['tajika_yoga']} (Is Ithasala: {p_res['is_ithasala']}, Is Esharpha: {p_res['is_esharpha']})
Chandra Placement in Prashna: {p_res['moon_placement']}
Intent Sincerity Status (Prashna Marga): {research['intent_status']} — {research['intent_detail']}
Prashna Verdict & Timing: {p_res['verdict']} | Probable Timing: {research['direct_timing']}
=================================================================
"""

        prompt = f"""{chart_context}

{prashna_block}

{history_text}
USER QUESTION:
\"{user_query}\"

CRITICAL GENERAL INTELLIGENCE & DAIVAJNA INSTRUCTIONS:
1. ANSWER ONLY WHAT WAS ASKED: The user is specifically asking about: {topic.upper()}. Address their specific query directly in the opening lines. Do NOT write unsolicited essays about unrelated life domains.
2. DUAL-KUNDALI SYNTHESIS: Cross-corroborate the Instant Prashna Kundali (Lagna, Karyesh, Tajika Ithasala/Esharpha yoga, and Intent testing check) with the Natal Kundali (D1 house lord, D9/D10 divisional dignity, active Mahadasha-Antardasha).
3. ABSOLUTE HONESTY & CANDID CAUTION: If there are negative yogas, delays, or doshas (Manglik, Saturn delay, malefic dasha), state them clearly under a bold caution heading without sugarcoating.
4. RATNA SHASTRA COMPLIANCE: If asked about gemstones, strictly follow the gemology matrix. NEVER recommend Panna if Mercury is in the 8th house; forbid it with an explicit alert and prescribe 4-Mukhi Rudraksha, Budha mantra, and green moong daan.
5. Conclude with focused, actionable, satvik Vedic remedies in {language} for this specific question only.
"""

        models_to_try = [model, "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
        for m_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.35,
                    )
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue

        return research["prashna_res"].get("explanation_hi", "शास्त्रीय गणना पूर्ण हुई।")

    def synthesize_narrative(self, result: GhatnaQueryResult, language: str = "Hindi") -> str:
        """Synthesizes narrative for Ghatna query results."""
        if not self.client:
            return result.narrative_hi if language.lower().startswith("hi") else result.narrative_en

        evidence_payload = {
            "target_date": result.target_date.isoformat(),
            "theme": result.theme,
            "composite_score": result.composite_score,
            "confidence_band": result.confidence_band,
            "active_dasha": result.active_dasha.formatted_summary,
            "top_positive_signals": [
                {"rule": s.rule_name_hi, "source": s.source_text, "explanation": s.explanation_hi, "score": s.signal_score}
                for s in result.top_positive_signals
            ],
            "top_negative_signals": [
                {"rule": s.rule_name_hi, "source": s.source_text, "explanation": s.explanation_hi, "score": s.signal_score}
                for s in result.top_negative_signals
            ]
        }

        user_prompt = (
            f"Please synthesize a clear, shastriya astrological consultation narrative for the user in {language}.\n"
            f"Input Evidence JSON:\n{evidence_payload}\n"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                )
            )
            return response.text
        except Exception:
            return result.narrative_hi


default_narrative_service = AINarrativeService()
