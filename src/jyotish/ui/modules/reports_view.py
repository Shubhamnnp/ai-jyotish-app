import streamlit as st
import urllib.parse as urllib
from src.jyotish.services.master_calculator import default_master_calculator
from src.jyotish.services.report_generator import default_report_generator
from src.jyotish.services.pdf_generator import default_pdf_service
try:
    from src.jyotish.services.prescription import default_prescription_service, ConsultationSlipService
except ImportError:
    default_prescription_service = None
    ConsultationSlipService = None

def render_reports_view(chart, birth_profile, tabs=None):
    if tabs is None or len(tabs) < 2:
        tabs = [
            '📚 सम्पूर्ण ५०-पेज पत्रिका',
            '📋 १-पेज परामर्श पर्ची'
        ]
    st.subheader("📄 सम्पूर्ण जीवन कुण्डली पत्रिका एवं १-पेज परामर्श पर्ची (Printable Dossier & Prescription)")

    # Classical Shastriya Shloka Card
    bphs_report_shloka = {
        "title": "बृहत्पाराशर होराशास्त्र एवं फलदीपिका — सम्पूर्ण जीवन पत्रिका निर्माण",
        "source": "महर्षि पराशर विरचित 'बृहत्पाराशर होराशास्त्र' (अध्याय १, श्लोक ३-४) एवं 'फलदीपिका'",
        "shloka": "होराशास्त्रं प्रवक्ष्यामि लोकानां हितकाम्यया।\nब्रह्मणा यत्पुरातन्यं पाराशर्यं महन्मतम्॥\nयस्य विज्ञानमात्रेण सर्वज्ञत्वं प्रपद्यते।\nआयुर्दायं दशा ज्ञेया शुभाशुभफलं स्फुटम्॥",
        "meaning": "समस्त मानव जाति के कल्याणार्थ महर्षि पराशर ने होराशास्त्र का विशद ज्ञान प्रकट किया। षोडशवर्ग, अष्टकवर्ग, द्वादश भाव, विंशोत्तरी दशा एवं गोचर का प्रामाणिक समन्वय कर जब सम्पूर्ण जीवन पत्रिका निर्मित की जाती है, तो जातक के भूत, भविष्य और वर्तमान का स्फुट व प्रामाणिक मार्गदर्शन प्राप्त होता है।"
    }
    with st.expander(f"📜 शास्त्रीय प्रमाण — {bphs_report_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {bphs_report_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{bphs_report_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {bphs_report_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Active Native Micro Reports HUD Console
    l_deg = getattr(chart, "lagna_degree", 0.0)
    l_ansh = int(l_deg)
    l_kala = int(round((l_deg - l_ansh) * 60.0))
    if l_kala >= 60:
        l_kala = 0
        l_ansh += 1
    l_dms = f"{l_ansh}° {l_kala:02d}'"

    moon = chart.planets.get("Moon")
    if moon:
        m_deg = getattr(moon, "sign_degree", 0.0)
        m_ansh = int(m_deg)
        m_kala = int(round((m_deg - m_ansh) * 60.0))
        if m_kala >= 60:
            m_kala = 0
            m_ansh += 1
        m_dms = f"{m_ansh}° {m_kala:02d}'"
        m_nak = getattr(moon, "nakshatra_name", getattr(moon, "nakshatra", "—"))
        m_pada = getattr(moon, "nakshatra_pada", getattr(moon, "pada", 1))
    else:
        m_dms = "—"
        m_nak = "—"
        m_pada = 1

    p_serv = default_prescription_service
    if p_serv is None:
        from src.jyotish.services.prescription import ConsultationSlipService
        p_serv = ConsultationSlipService()
    try:
        quick_p = p_serv.generate_prescription(chart)
        pri_gem = quick_p.get("primary_gem", "माणिक्य")
        pro_gems = ", ".join(quick_p.get("prohibited_gems", [])[:2]) or "कोई नहीं"
    except Exception:
        pri_gem = "माणिक्य"
        pro_gems = "—"

    col_rep1, col_rep2, col_rep3, col_rep4 = st.columns(4)
    col_rep1.metric("सक्रिय जातक व लग्न", f"{birth_profile.name}", f"{chart.lagna_sign_name} ({l_dms})")
    col_rep2.metric("चन्द्र राशि व नक्षत्र", f"{moon.sign_name if moon else '—'} ({m_dms})", f"🌙 {m_nak}-चरण {m_pada}")
    col_rep3.metric("अनुकूल प्राथमिक रत्न", f"🟢 {pri_gem}", f"वर्जित: 🚫 {pro_gems}")
    col_rep4.metric("रिपोर्ट स्वरूप (Formats)", "२२ अध्याय पत्रिका", "A4 PDF / HTML / पर्ची")

    with st.expander("👑 ज्योतिषी कस्टम ब्रांडिंग एवं रिपोर्ट विन्यास (White-Label Branding Settings)", expanded=False):
        c_br1, c_br2, c_br3 = st.columns(3)
        astro_name = c_br1.text_input("ज्योतिषी का नाम (Astrologer Name)", value="ज्योतिषाचार्य पं. शुभम तिवारी", key="rep_astro_name")
        astro_org = c_br2.text_input("संस्थान / केंद्र (Center Name)", value="वैदिक ज्योतिष अनुसंधान केंद्र", key="rep_astro_org")
        astro_phone = c_br3.text_input("संपर्क सूत्र / WhatsApp (Contact)", value="+91-9452155742", key="rep_astro_phone")

    tab_rep_master, tab_rep_slip = st.tabs(tabs)

    with tab_rep_master:
        st.write("पूरी जन्म कुण्डली, षोडशवर्ग, द्वादश भाव, षड्बल, जैमिनी, ५ दशा प्रणालियाँ, अष्टकवर्ग, साढ़ेसाती, गोचर एवं पाया, लाल किताब ९ ऋण व १०८ टोटके, ३-स्तरीय ट्रिगर, वैदिक मुहूर्त एवं पञ्चक, कुण्डली मिलान १६ परिहार, के.पी. कस्पल सब-लॉर्ड्स, सुदर्शन चक्र, वास्तु एवं सात्विक उपायों सहित २२ अध्यायों की पूर्ण रंगीन मुद्रण-योग्य पत्रिका।")

        r_gen = default_report_generator

        with st.spinner("🔮 समस्त शास्त्रीय गणनाओं को संकलित कर सम्पूर्ण पत्रिका तैयार की जा रही है..."):
            master_bundle = default_master_calculator.calculate_all(chart)
            html_rep = r_gen.generate_html_report(
                chart,
                master_data=master_bundle,
                astro_name=astro_name,
                astro_phone=astro_phone,
                astro_org=astro_org
            )

        pdf_service = default_pdf_service

        chart_cache_key = f"pdf_{birth_profile.name}_{birth_profile.birth_date}_{birth_profile.birth_time}"
        pdf_bytes = st.session_state.get(chart_cache_key, None)

        col_rep_btn1, col_rep_btn2, col_rep_btn3 = st.columns([1.8, 1.4, 1.2])
        with col_rep_btn1:
            if pdf_bytes:
                st.download_button(
                    label=f"⚡ असली PDF डाउनलोड करें ({len(pdf_bytes)/1024:.0f} KB)",
                    data=pdf_bytes,
                    file_name=f"{birth_profile.name}_Sampurna_Kundali_Report.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="rep_btn_download_pdf"
                )
            else:
                if st.button("⚡ 1-क्लिक असली PDF तैयार करें (Direct Native PDF)", type="primary", use_container_width=True, key="rep_btn_gen_pdf"):
                    with st.spinner("🔮 क्रोमियम इंजन द्वारा सम्पूर्ण 50+ पेज सचित्र पत्रिका PDF तैयार की जा रही है (लगभग 10-15 सेकंड)..."):
                        pdf_data = pdf_service.html_to_pdf_bytes(html_rep, timeout_sec=90)
                        if pdf_data:
                            st.session_state[chart_cache_key] = pdf_data
                            st.toast("✅ सम्पूर्ण 50+ पेज PDF सफलतापूर्वक तैयार हो गई है! डाउनलोड बटन पर क्लिक करें।")
                            st.rerun()
                        else:
                            st.error("⚠️ PDF इंजन निष्पादित नहीं हो सका। कृपया बगल में दिए गए HTML डाउनलोड का उपयोग करें।")

        with col_rep_btn2:
            st.download_button(
                label="📥 रंगीन HTML पत्रिका (.html)",
                data=html_rep,
                file_name=f"{birth_profile.name}_Sampurna_Kundali_Report.html",
                mime="text/html",
                use_container_width=True,
                key="rep_btn_download"
            )
        with col_rep_btn3:
            st.button("🖨️ सीधे प्रिंट करें (Ctrl+P)", on_click=lambda: st.toast("प्रिंट करने हेतु डाउनलोड फाइल को ब्राउज़र में खोलकर Ctrl+P दबाएं।"), use_container_width=True, key="rep_btn_print")

        with st.expander("👁️ पत्रिका सम्पूर्ण लाइव पूर्वावलोकन (Live 20+ Chapter Preview)", expanded=True):
            st.components.v1.html(html_rep, height=850, scrolling=True)

    with tab_rep_slip:
        st.markdown("#### 📋 १-पेज डॉक्टरी-शैली ज्योतिषी परामर्श पर्ची (Consultation Prescription Slip)")
        st.caption("क्लाइंट को परामर्श के बाद सीधे देने हेतु त्वरित १-पेज पर्ची — अनुकूल रत्न, पूर्ण वर्जित रत्न, वैदिक मंत्र, अनिष्ट शांति दान, जीवनशैली एवं ९० दिनों की गोचर सावधानी।")

        p_service = default_prescription_service
        if p_service is None:
            from src.jyotish.services.prescription import ConsultationSlipService
            p_service = ConsultationSlipService()

        p_data = p_service.generate_prescription(chart)
        p_html = p_service.render_prescription_html(
            p_data,
            astro_name=astro_name,
            astro_center=astro_org,
            astro_contact=astro_phone
        )
        p_wa_text = p_service.generate_whatsapp_text(p_data)
        import urllib.parse
        wa_url = f"https://wa.me/?text={urllib.parse.quote(p_wa_text)}"

        slip_cache_key = f"slip_pdf_{birth_profile.name}_{birth_profile.birth_date}"
        slip_pdf = st.session_state.get(slip_cache_key, None)

        col_slip1, col_slip2, col_slip3, col_slip4 = st.columns([1.6, 1.2, 1.4, 1.0])
        with col_slip1:
            if slip_pdf:
                st.download_button(
                    "⚡ असली पर्ची PDF डाउनलोड (.pdf)",
                    data=slip_pdf,
                    file_name=f"{birth_profile.name}_Consultation_Prescription.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="btn_dl_slip_pdf"
                )
            else:
                if st.button("⚡ 1-क्लिक पर्ची PDF बनाएं", type="primary", use_container_width=True, key="btn_gen_slip_pdf"):
                    with st.spinner("📄 1-पेज पर्ची PDF तैयार हो रही है..."):
                        s_data = pdf_service.html_to_pdf_bytes(p_html, timeout_sec=30)
                        if s_data:
                            st.session_state[slip_cache_key] = s_data
                            st.rerun()
        with col_slip2:
            st.download_button(
                "📥 पर्ची HTML",
                data=p_html,
                file_name=f"{birth_profile.name}_Consultation_Prescription.html",
                mime="text/html",
                use_container_width=True,
                key="btn_dl_slip"
            )
        with col_slip3:
            st.link_button(
                "💬 WhatsApp पर भेजें",
                url=wa_url,
                use_container_width=True
            )
        with col_slip4:
            st.button("🖨️ A4 प्रिंट (Ctrl+P)", on_click=lambda: st.toast("डाउनलोड की गई पर्ची ब्राउज़र में खोलकर Ctrl+P से A4 आकार में तुरंत प्रिंट करें।"), use_container_width=True, key="btn_print_slip")

        st.components.v1.html(p_html, height=720, scrolling=True)



    # =============================================================
    # TAB 17: 100 SHASTRIYA RULES LIBRARY

