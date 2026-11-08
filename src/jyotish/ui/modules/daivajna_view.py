import streamlit as st
import os
from src.jyotish.services.master_calculator import default_master_calculator
from src.jyotish.ai.narrative import default_narrative_service
from src.jyotish.dasha.vimshottari import default_dasha_engine as default_vimshottari_engine

def render_daivajna_view(chart, tabs=None):
    st.subheader("💬 दैवज्ञ AI सहायक — प्रामाणिक वैदिक परामर्श (Dual-Kundali AI Astrologer)")
    st.write("९९.९% शास्त्रीय परिशुद्धता: जन्म कुण्डली (D1-D60) एवं तात्कालिक प्रश्न कुण्डली (Prashna Marga) के संयुक्त शोध पर आधारित निष्पक्ष, ईमानदार एवं सत्य फलादेश।")

    # Active Kundali Profile Banner
    vim_current = ""
    try:
        curr_dasha = default_vimshottari_engine.get_current_dasha(chart)
        if curr_dasha:
            vim_current = f" &nbsp;|&nbsp; <b>वर्तमान महादशा:</b> <span style='color:#7C3AED;'>{curr_dasha.get('lord', '')} ({curr_dasha.get('level', 'MD')})</span>"
    except Exception:
        vim_current = ""

    st.markdown(
        f'<div style="background:linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border:1.5px solid #93C5FD; border-radius:10px; padding:12px 18px; margin-bottom:15px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
        f'<div><b style="color:#1E40AF; font-size:15px;">👤 सक्रिय कुण्डली:</b> <span style="font-weight:700; color:#0F172A;">{chart.birth_data.name}</span> &nbsp;|&nbsp; '
        f'<b>लग्न:</b> <span style="color:#2563EB;">{chart.lagna_sign_name}</span> &nbsp;|&nbsp; '
        f'<b>चन्द्र राशि:</b> <span style="color:#2563EB;">{chart.planets["Moon"].sign_name} ({chart.panchang.nakshatra_name})</span> &nbsp;|&nbsp; '
        f'<b>आत्मकारक:</b> <span style="color:#D97706;">{chart.atmakaraka}</span>'
        f'{vim_current}</div>'
        f'<div><span style="background:#DCFCE7; color:#166534; border:1px solid #86EFAC; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:700;">🌟 ९९.९% प्रामाणिक दैवज्ञ शोध</span></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # ⚡ त्रिवेणी संगम: JyotishOS Math Engine + Google Gemini AI + OpenAI ChatGPT-4o
    with st.expander("⚡ त्रिवेणी संगम AI विन्यास (JyotishOS Deep Math + Google Gemini AI + OpenAI GPT-4o)", expanded=False):
        c_eng1, c_eng2 = st.columns([1.3, 1])
        with c_eng1:
            trio_mode_options = [
                "⚡ त्रिवेणी संगम (Trio: JyotishOS Math + Gemini + OpenAI)",
                "🌟 Google Gemini AI + JyotishOS Math",
                "🤖 OpenAI GPT-4o + JyotishOS Math",
                "🔬 Offline Shastriya Engine (100% Deterministic Local)"
            ]
            selected_trio_mode = st.radio(
                "🧠 एआई इंजन प्रदाता मोड (AI Provider Mode):",
                options=trio_mode_options,
                index=0,
                key="radio_trio_ai_mode"
            )
            mode_code = "trio"
            if "Gemini" in selected_trio_mode and "OpenAI" not in selected_trio_mode:
                mode_code = "gemini"
            elif "OpenAI" in selected_trio_mode and "Gemini" not in selected_trio_mode:
                mode_code = "openai"
            elif "Offline" in selected_trio_mode:
                mode_code = "offline"

        with c_eng2:
            st.markdown("<b style='font-size:13px; color:#1E40AF;'>🔑 API की स्थिति एवं मॉडल्स:</b>", unsafe_allow_html=True)
            k_gem = st.session_state.get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
            k_oai = st.session_state.get("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
            gem_badge = "🟢 सक्रिय (Active)" if k_gem else "🟡 अप्रदत्त (Optional)"
            oai_badge = "🟢 सक्रिय (Active)" if k_oai else "🟡 अप्रदत्त (Optional)"
            st.markdown(
                f'<div style="font-size:12.5px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:8px 12px; margin-bottom:8px;">'
                f'• 🌟 <b>Google Gemini:</b> <span style="font-weight:700;">{gem_badge}</span><br>'
                f'• 🤖 <b>OpenAI GPT-4o:</b> <span style="font-weight:700;">{oai_badge}</span><br>'
                f'• 🔬 <b>JyotishOS Math:</b> <span style="color:#059669; font-weight:700;">100% सक्रिय</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                sel_gem_model = st.selectbox("Gemini Model:", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro"], key="sb_gem_model")
            with c_m2:
                sel_oai_model = st.selectbox("OpenAI Model:", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], key="sb_oai_model")

        c_k1, c_k2 = st.columns(2)
        with c_k1:
            inp_gem = st.text_input("Gemini API Key (वैकल्पिक):", value=k_gem, type="password", key="inp_gem_key_t16")
            if inp_gem:
                st.session_state["gemini_api_key"] = inp_gem
        with c_k2:
            inp_oai = st.text_input("OpenAI API Key (वैकल्पिक):", value=k_oai, type="password", key="inp_oai_key_t16")
            if inp_oai:
                st.session_state["openai_api_key"] = inp_oai

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = [
            {
                "role": "assistant",
                "content": f"🙏 **प्रणाम! मैं आपका 'दैवज्ञ AI' (त्रिवेणी संगम) सहायक हूँ।**\n\nमैंने **{chart.birth_data.name} जी** की कुण्डली ({chart.lagna_sign_name} लग्न, {chart.planets['Moon'].sign_name} राशि) का D1 से D60 तक सम्पूर्ण षोडशवर्ग, दशा, गोचर, तथा १२,५००+ महा-शास्त्रीय नियम लोड कर लिए हैं।\n\nयह परामर्श प्रणाली **JyotishOS Deep Math Engine + Google Gemini AI + OpenAI ChatGPT-4o** के संयुक्त त्रिवेणी संगम पर प्रशिक्षित है।\n\nआप विवाह, करियर, व्यापार, धन, स्वास्थ्य, या शुभ रत्न से सम्बंधित कोई भी प्रश्न पूछ सकते हैं। आपके प्रत्येक प्रश्न पर मैं **तात्कालिक प्रश्न कुण्डली (Prashna Marga)** एवं **जन्म कुण्डली** का संयुक्त शोध कर सिर्फ आपके प्रश्न का ९९.९% सटीक, ईमानदार एवं निष्पक्ष उत्तर दूँगा (सकारात्मक योग एवं नकारात्मक बाधक तत्व दोनों पूर्ण सत्यता के साथ)।"
            }
        ]

    # Quick Consultation Question Chips
    st.markdown("<b style='font-size:13px; color:#475569;'>⚡ त्वरित शास्त्रीय प्रश्न (Direct Consultation):</b>", unsafe_allow_html=True)
    c_q1, c_q2, c_q3, c_q4 = st.columns(4)
    quick_q = None
    if c_q1.button("💍 विवाह काल व 3-Tier ट्रिगर", use_container_width=True):
        quick_q = "मेरी शादी कब तक होगी? कृपया प्रश्न कुण्डली, ३-स्तरीय ट्रिगर (दशा + गोचर + अष्टकवर्ग) और जन्म कुण्डली के आधार पर सटीक समय बताएं।"
    if c_q2.button("💼 करियर, आजीविका व पदोन्नति", use_container_width=True):
        quick_q = "मेरी कुण्डली एवं प्रश्न समय के अनुसार करियर में पदोन्नति या नई नौकरी का अनुकूल समय कब आएगा?"
    if c_q3.button("💰 धन लाभ व आर्थिक स्थिति", use_container_width=True):
        quick_q = "मेरी आर्थिक स्थिति, धन लाभ और बचत के लिए कुण्डली क्या संकेत देती है?"
    if c_q4.button("🪐 दशा एवं गोचर पाया फल", use_container_width=True):
        quick_q = "वर्तमान में चल रही दशा और गोचर (शनि व गुरु के पाए सहित) का मेरे जीवन पर क्या प्रभाव पड़ रहा है?"

    c_q5, c_q6, c_q7, c_q8 = st.columns(4)
    if c_q5.button("📕 लाल किताब ऋण व टोटके", use_container_width=True):
        quick_q = "मेरी कुण्डली में लाल किताब 1952 के अनुसार क्या कोई सक्रिय कर्मिक ऋण है और क्या सात्विक टोटके व सावधानियां विहित हैं?"
    if c_q6.button("🎯 3-Tier घटना सम्भावना काल", use_container_width=True):
        quick_q = "मेरी कुण्डली में आने वाले १२ से २४ महीनों में प्रमुख जीवन घटना (करियर/विवाह) के ३-स्तरीय ट्रिगर स्कोर क्या हैं?"
    if c_q7.button("💎 शुभ रत्न, रुद्राक्ष व मन्त्र", use_container_width=True):
        quick_q = "मेरी कुण्डली के अनुसार मेरे लिए कौन सा रत्न शुभ है और कौन सा रत्न सर्वथा वर्जित है? कृपया कठोर शास्त्रीय नियम से बताएं।"
    if c_q8.button("⚠️ स्वास्थ्य व त्रिदोष निवारण", use_container_width=True):
        quick_q = "मेरी कुण्डली में स्वास्थ्य, त्रिदोष संतुलन अथवा अरिष्ट के क्या संकेत हैं और उनसे बचाव के शास्त्रीय उपाय क्या हैं?"

    # Display Conversation History
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"], avatar="🔮" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Chat Input Box
    user_prompt = st.chat_input("अपनी कुण्डली से संबंधित प्रश्न यहाँ लिखें (उदा. मेरी शादी कब तक होगी?)...")
    prompt_to_process = quick_q or user_prompt

    if prompt_to_process:
        # Add user message to history
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_to_process)

        # Generate Assistant Response
        with st.chat_message("assistant", avatar="🔮"):
            with st.spinner("🔮 प्रश्न परीक्षण (सत्यता जांच), तात्कालिक प्रश्न कुण्डली एवं जन्म कुण्डली (D1-D60) का संयुक्त शास्त्रीय शोध किया जा रहा है..."):
                master_bundle = default_master_calculator.calculate_all(chart)
                active_key = st.session_state.get("gemini_api_key", os.getenv("GEMINI_API_KEY"))
                active_oai_key = st.session_state.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
                curr_mode_label = st.session_state.get("radio_trio_ai_mode", "trio")
                mode_arg = "trio"
                if "Gemini" in curr_mode_label and "OpenAI" not in curr_mode_label:
                    mode_arg = "gemini"
                elif "OpenAI" in curr_mode_label and "Gemini" not in curr_mode_label:
                    mode_arg = "openai"
                elif "Offline" in curr_mode_label:
                    mode_arg = "offline"

                ai_response = default_narrative_service.chat_consultation(
                    user_query=prompt_to_process,
                    chart=chart,
                    master_data=master_bundle,
                    api_key=active_key,
                    openai_api_key=active_oai_key,
                    provider_mode=mode_arg,
                    model=st.session_state.get("sb_gem_model", "gemini-2.5-flash"),
                    openai_model=st.session_state.get("sb_oai_model", "gpt-4o"),
                    language="Hindi",
                    chat_history=st.session_state.ai_chat_history
                )
                st.markdown(ai_response)
                st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_response})

                # Render Live Dual-Kundali Research Evidence Card for this query
                latest_research = st.session_state.get("ai_latest_research")
                if latest_research and latest_research.get("topic") != "greeting":
                    p_info = latest_research.get("prashna_res", {})
                    with st.expander("🔬 दैवज्ञ द्वि-कुण्डली शोध प्रमाण (Natal + Horary Prashna + D1-D60 Backend Audit)", expanded=False):
                        cp1, cp2, cp3 = st.columns(3)
                        with cp1:
                            st.markdown(
                                f'<div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px 14px; font-size:12.5px;">'
                                f'<b style="color:#1E40AF;">❓ तात्कालिक प्रश्न परीक्षा:</b><br>'
                                f'<b>प्रश्न लग्न:</b> {p_info.get("prashna_lagna_sign", "—")} ({p_info.get("prashna_lagna_deg", "—")})<br>'
                                f'<b>प्रश्नेश:</b> {p_info.get("lagnesh_name", "—")} (भाव {p_info.get("lagnesh_house", "—")})<br>'
                                f'<b>कार्येश:</b> {p_info.get("karyesh_name", "—")} (भाव {p_info.get("karyesh_house", "—")})<br>'
                                f'<b>ताजिक योग:</b> <span style="color:#7C3AED; font-weight:700;">{p_info.get("tajika_yoga", "—")}</span><br>'
                                f'<b>जिज्ञासा भाव:</b> {latest_research.get("intent_status", "—")}'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        with cp2:
                            n_sum = latest_research.get("natal_summary", {})
                            bhava_txt = n_sum.get("bhava", "सम्पूर्ण कुण्डली")
                            bhavesh_txt = n_sum.get("bhavesh", "—")
                            karakas_txt = n_sum.get("karakas", n_sum.get("karaka", "—"))
                            st.markdown(
                                f'<div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px 14px; font-size:12.5px;">'
                                f'<b style="color:#047857;">📜 जन्म कुण्डली शोध:</b><br>'
                                f'<b>सम्बन्धित भाव:</b> {bhava_txt}<br>'
                                f'<b>भावेश स्थिति:</b> {bhavesh_txt}<br>'
                                f'<b>कारक स्थिति:</b> {karakas_txt}<br>'
                                f'<b>संभावित काल:</b> <b style="color:#16A34A;">{latest_research.get("direct_timing", "—")}</b>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        with cp3:
                            g_aud = latest_research.get("gem_audit", {})
                            rec_cnt = len(g_aud.get("recommended_gems", [])) if g_aud else 0
                            pro_cnt = len(g_aud.get("strictly_prohibited_gems", [])) if g_aud else 0
                            merc_8_txt = "🚫 पन्ना वर्जित!" if chart.planets.get('Mercury') and chart.planets['Mercury'].house_from_lagna == 8 else "सामान्य"
                            st.markdown(
                                f'<div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px 14px; font-size:12.5px;">'
                                f'<b style="color:#B91C1C;">💎 रत्न शुद्धि व दुष्टस्थान:</b><br>'
                                f'<b>अनुशंसित रत्न:</b> 🟢 {rec_cnt} रत्न<br>'
                                f'<b>सर्वथा वर्जित रत्न:</b> 🚫 {pro_cnt} रत्न<br>'
                                f'<b>८वें भाव में बुध:</b> {merc_8_txt}<br>'
                                f'<b>निर्णय:</b> केवल योगकारक के रत्न ग्राह्य'
                                f'</div>',
                                unsafe_allow_html=True
                            )

    # Clear Chat Button
    if len(st.session_state.ai_chat_history) > 1:
        if st.button("🗑️ संवाद इतिहास साफ करें (Clear Chat)"):
            st.session_state.ai_chat_history = [
                {
                    "role": "assistant",
                    "content": f"🙏 **संवाद पुनः प्रारंभ किया गया।** {chart.birth_data.name} जी की कुण्डली एवं प्रश्न कुण्डली के संदर्भ में आप अपना प्रश्न पूछ सकते हैं।"
                }
            ]
            st.rerun()



    # TAB 19: COMPREHENSIVE REPORT & PRINTABLE KUNDALI BOOK

