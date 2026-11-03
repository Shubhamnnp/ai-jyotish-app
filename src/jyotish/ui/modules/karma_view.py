import streamlit as st
import importlib

def render_karma_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            '💼 आजीविका: व्यापार बनाम नौकरी',
            '🎓 विद्या, बुद्धि एवं मेधा',
            '⚖️ आचरण, सत्यनिष्ठा एवं चरित्र',
            '⚠️ व्यसन एवं चरित्र-पतन जोखिम',
            '🏰 पैतृक संपत्ति एवं आंतरिक सुख',
            '🕉️ पूर्वजन्म प्रारब्ध एवं आत्मकारक'
        ]
    st.subheader("🧘 व्यक्तित्व एवं कर्मफल विश्लेषण (Personality, Vices, Destiny & Karmic Ledger)")
    st.write("शास्त्रीय वैदिक ज्योतिष (पाराशर, जैमिनी, फलदीपिका एवं सारावली) के नियमों के आधार पर व्यापार बनाम नौकरी, शिक्षा-मेधा, नैतिक आचरण, व्यसन/लत जोखिम, पैतृक संपत्ति, आंतरिक सुख एवं पूर्वजन्म प्रारब्ध का निष्पक्ष व प्रामाणिक विश्लेषण।")

    import importlib
    import src.jyotish.core.karmaphala as karma_mod
    importlib.reload(karma_mod)

    kp_res = karma_mod.KarmaphalaEngine.analyze(chart)
    car = kp_res["career"]
    edu = kp_res["education"]
    mor = kp_res["morals"]
    vic = kp_res["vices"]
    inh = kp_res["inheritance"]
    pea = kp_res["peace"]
    krm = kp_res["karma"]

    # Top Status Banner
    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    c_k1.metric("आजीविका रुझान", car["rec_tag"].split(" (")[0], f"व्यापार: {car['business_score']}% | नौकरी: {car['job_score']}%")
    c_k2.metric("नैतिक सत्यनिष्ठा", f"{mor['morality_score']}%", mor["integrity_level"].split(" (")[0])
    c_k3.metric("व्यसन संवेदनशीलता", f"{vic['addiction_score']}%", vic["risk_level"].split(" / ")[0])
    c_k4.metric("पूर्वजन्म संचित पुण्य", f"{krm['purva_punya_score']}%", f"आत्मकारक: {krm['atmakaraka']}")

    tab_k1, tab_k2, tab_k3, tab_k4, tab_k5, tab_k6 = st.tabs(tabs)

    # ---------------------------------------------------------
    # TAB 1: आजीविका: व्यापार बनाम नौकरी (Career & Enterprise)
    # ---------------------------------------------------------
    with tab_k1:
        st.markdown("### 💼 व्यापार बनाम नौकरी (Business vs Service Aptitude)")
        st.caption("६ठे भाव (सेवा/नौकरी), ७वें भाव (व्यापार/साझेदारी), १०वें भाव (कर्म/सत्ता) एवं बुध/शनि की शास्त्रीय गणना:")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#1E40AF; font-weight:600;">व्यापार एवं स्वतंत्र उद्यम अनुकूलता</span>
                <div style="font-size:32px; font-weight:800; color:#1D4ED8; margin:8px 0;">{car['business_score']}%</div>
                <small style="color:#3B82F6;">७वां भाव (वाणिज्य), ११वां (लाभ) व बुध का प्रभाव</small>
            </div>
            """, unsafe_allow_html=True)
            st.progress(car['business_score'] / 100.0)

        with col_b2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#166534; font-weight:600;">नौकरी एवं संगठित सेवा अनुकूलता</span>
                <div style="font-size:32px; font-weight:800; color:#15803D; margin:8px 0;">{car['job_score']}%</div>
                <small style="color:#22C55E;">६ठा भाव (सेवा/प्रतियोगिता), १०वां (प्रतिष्ठा) व शनि का प्रभाव</small>
            </div>
            """, unsafe_allow_html=True)
            st.progress(car['job_score'] / 100.0)

        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:5px solid #2563EB; border-radius:8px; padding:16px; margin:16px 0;">
            <b style="color:#1E3A8A; font-size:16px;">🎯 अंतिम शास्त्रीय निर्णय: {car['recommendation_hi']}</b>
            <p style="margin:8px 0 0 0; color:#334155; font-size:14px; line-height:1.6;">{car['verdict_desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### ⚡ जोखिम सहिष्णुता (Risk Appetite):")
            st.info(car['risk_appetite'])

            st.markdown("#### ⚠️ शास्त्रीय सावधानियां व चेतावनियां:")
            for w in car['warnings']:
                st.markdown(f"• {w}")

        with col_c2:
            st.markdown("#### 🏭 सर्वाधिक अनुकूल कार्यक्षेत्र व उद्योग (Top Sectors):")
            for idx, sec in enumerate(car['sectors'], 1):
                st.markdown(f"**{idx}.** {sec}")

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {car['shastriya_basis']}</small>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 2: शिक्षा, मेधा एवं बौद्धिक क्षमता (Education & Intellect)
    # ---------------------------------------------------------
    with tab_k2:
        st.markdown("### 🎓 शिक्षा, मेधा एवं बौद्धिक क्षमता (Education & Academic Intellect)")
        st.caption("४थे भाव (विद्या आधार), ५वें भाव (धी-शक्ति/बुद्धि), ९वें भाव (उच्च गुरु ज्ञान) एवं बुध-बृहस्पति का शास्त्रीय विश्लेषण:")

        col_e1, col_e2 = st.columns([1.2, 2.8])
        with col_e1:
            st.markdown(f"""
            <div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#5B21B6; font-weight:600;">समग्र शैक्षिक सामर्थ्य</span>
                <div style="font-size:36px; font-weight:800; color:#6D28D9; margin:8px 0;">{edu['education_score']}%</div>
                <span style="background:#EDE9FE; color:#5B21B6; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:600;">
                    {edu['memory_power'].split(' (')[0]}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col_e2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #7C3AED; border-radius:8px; padding:14px;">
                <b style="color:#4C1D95; font-size:15px;">🧠 बौद्धिक प्रकृति: {edu['intellect_type']}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{edu['intellect_desc']}</p>
                <div style="margin-top:8px; font-size:13px; color:#6D28D9;"><b>स्मरण एवं ग्रहण शक्ति:</b> {edu['memory_power']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.markdown("#### 🚧 शिक्षा में संभावित अवरोध व एकाग्रता दोष (Academic Hurdles):")
            for h in edu['hurdles']:
                st.markdown(f"• {h}")

        with col_ed2:
            st.markdown("#### 🎯 सर्वाधिक फलदायी अध्ययन क्षेत्र एवं करियर शाखाएं:")
            for idx, s in enumerate(edu['recommended_streams'], 1):
                st.markdown(f"**{idx}.** {s}")

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {edu['shastriya_basis']}</small>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: नैतिक आचरण एवं गुण-प्रवृत्तियां (Ethics & Morals)
    # ---------------------------------------------------------
    with tab_k3:
        st.markdown("### ⚖️ नैतिक व्यवहार, सत्यनिष्ठा एवं गुण प्रवृत्तियां (Ethics & Guna Balance)")
        st.caption("लग्न भाव (आत्म-स्वरूप), नवम भाव (धर्म व विवेक) तथा त्रिगुण (सत्व, रज, तम) का शास्त्रीय मापन:")

        col_m1, col_m2 = st.columns([1.2, 2.8])
        with col_m1:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#92400E; font-weight:600;">सत्यनिष्ठा व धर्म बल</span>
                <div style="font-size:36px; font-weight:800; color:#B45309; margin:8px 0;">{mor['morality_score']}%</div>
                <small style="color:#D97706;">सूर्य, गुरु व नवमेश का संयुक्त सामर्थ्य</small>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #D97706; border-radius:8px; padding:14px;">
                <b style="color:#78350F; font-size:15px;">📜 चारित्रिक स्तर: {mor['integrity_level']}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{mor['integrity_desc']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ☸️ त्रिगुण संतुलन अनुपात (Prakriti Guna Distribution):")
        cg1, cg2, cg3 = st.columns(3)
        with cg1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:12px; text-align:center;">
                <b style="color:#15803D;">सत्व गुण (Satva): {mor['guna_distribution']['satva']}%</b>
                <p style="font-size:12px; color:#166534; margin:4px 0 0 0;">धर्म, सत्य, करुणा, आत्म-संयम, ईश्वर-भक्ति</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(mor['guna_distribution']['satva'] / 100.0)

        with cg2:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:12px; text-align:center;">
                <b style="color:#1D4ED8;">रज गुण (Rajas): {mor['guna_distribution']['rajas']}%</b>
                <p style="font-size:12px; color:#1E40AF; margin:4px 0 0 0;">महत्वाकांक्षा, कर्मठता, भौतिक सुख, मान-प्रतिष्ठा</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(mor['guna_distribution']['rajas'] / 100.0)

        with cg3:
            st.markdown(f"""
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:12px; text-align:center;">
                <b style="color:#B91C1C;">तम गुण (Tamas): {mor['guna_distribution']['tamas']}%</b>
                <p style="font-size:12px; color:#991B1B; margin:4px 0 0 0;">क्रोध, प्रमाद, हठधर्मिता, अति-आवेश, आलस्य</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(mor['guna_distribution']['tamas'] / 100.0)

        st.markdown("---")
        col_vr1, col_vr2 = st.columns(2)
        with col_vr1:
            st.markdown("#### 🌟 अंतर्निहित सद्गुण (Core Inherent Virtues):")
            for v in mor['virtues']:
                st.markdown(f"• **{v}**")

        with col_vr2:
            st.markdown("#### 🌑 छाया प्रवृत्तियां व आंतरिक कमजोरियां (Shadow Traits to Watch):")
            for s in mor['shadows']:
                st.markdown(f"• <span style='color:#B91C1C;'>{s}</span>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {mor['shastriya_basis']}</small>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 4: गलत लत, व्यसन एवं प्रलोभन (Vices & Addictions)
    # ---------------------------------------------------------
    with tab_k4:
        st.markdown("### 🚫 गलत लत, व्यसन एवं प्रलोभन संवेदनशीलता (Vices & Addiction Vulnerability)")
        st.caption("द्वितीय भाव (मुख/आहार/खानपान), अष्टम भाव (गुप्त व्यसन), द्वादश भाव (पलायन/अनिद्रा) एवं राहु-शुक्र-मंगल का निष्पक्ष शास्त्रीय परीक्षण:")

        col_vc1, col_vc2 = st.columns([1.2, 2.8])
        with col_vc1:
            alert_bg = "#FEF2F2" if vic['addiction_score'] >= 60 else ("#FFFBEB" if vic['addiction_score'] >= 35 else "#F0FDF4")
            alert_border = "#FECACA" if vic['addiction_score'] >= 60 else ("#FDE68A" if vic['addiction_score'] >= 35 else "#BBF7D0")
            alert_text = "#991B1B" if vic['addiction_score'] >= 60 else ("#92400E" if vic['addiction_score'] >= 35 else "#166534")

            st.markdown(f"""
            <div style="background:{alert_bg}; border:1px solid {alert_border}; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:{alert_text}; font-weight:600;">व्यसन संवेदनशीलता सूचकांक</span>
                <div style="font-size:36px; font-weight:800; color:{alert_text}; margin:8px 0;">{vic['addiction_score']}%</div>
                <small style="color:{alert_text}; font-weight:600;">{vic['risk_level']}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_vc2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #DC2626; border-radius:8px; padding:14px;">
                <b style="color:#991B1B; font-size:15px;">🛡️ शास्त्रीय चेतावनी एवं परामर्श:</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{vic['warning_advice']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🔍 ६-सूत्रीय व्यसन एवं दुर्गुण संवेदनशीलता परीक्षण:")
        for vuln in vic['vulnerabilities']:
            is_danger = "उच्च" in vuln['level'] or "गंभीर" in vuln['level']
            card_border = "#FCA5A5" if is_danger else "#E2E8F0"
            card_bg = "#FFF5F5" if is_danger else "#F8FAFC"
            tag_color = "#DC2626" if is_danger else "#475569"

            st.markdown(f"""
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#0F172A; font-size:14px;">• {vuln['vice']}</b>
                    <span style="background:#FFFFFF; border:1px solid {card_border}; color:{tag_color}; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:700;">{vuln['level']}</span>
                </div>
                <p style="margin:6px 0 0 0; color:#475569; font-size:13px;"><b>ज्योतिषीय कारण:</b> {vuln['reason']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ⚡ कुण्डली के प्रमुख ट्रिगर्स एवं सुरक्षा कवच:")
        for tr in vic['triggers']:
            st.markdown(f"• {tr}")

        st.markdown("#### 🌿 शास्त्रीय निवारण एवं संकल्प (Remedial Countermeasures):")
        for rem in vic['remedies']:
            st.markdown(f"• {rem}")

    # ---------------------------------------------------------
    # TAB 5: पैतृक संपत्ति, सुख एवं शांति (Inheritance & Peace)
    # ---------------------------------------------------------
    with tab_k5:
        st.markdown("### 🏛️ पैतृक संपत्ति एवं मानसिक सुख (Inheritance, Lands & Inner Peace)")

        # Section 1: Inheritance
        st.markdown("#### 📜 १. पैतृक संपत्ति, वसीयत एवं भूमि-भवन लाभ (Inheritance & Ancestral Wealth):")
        col_in1, col_in2 = st.columns([1.2, 2.8])
        with col_in1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#166534; font-weight:600;">पैतृक लाभ अनुकूलता</span>
                <div style="font-size:34px; font-weight:800; color:#15803D; margin:8px 0;">{inh['inheritance_score']}%</div>
                <small style="color:#166534;">८वां (विरासत), ९वां (पिता) व मंगल</small>
            </div>
            """, unsafe_allow_html=True)

        with col_in2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:8px; padding:14px;">
                <b style="color:#14532D; font-size:15px;">🏛️ पैतृक स्थिति: {inh['status']}</b>
                <p style="margin:6px 0; color:#334155; font-size:13.5px;">{inh['status_desc']}</p>
                <div style="margin-top:6px; font-size:13px; color:#0F172A;">
                    • <b>विवाद/मुकदमेबाजी की संभावना:</b> {inh['dispute_risk']}<br/>
                    • <b>भूमि-भवन व अचल संपत्ति योग:</b> {inh['land_status']}<br/>
                    • <b>पिता का सहयोग व संबंध:</b> {inh['father_support']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Section 2: Inner Peace & Mental Sukha
        st.markdown("#### 🕊️ २. आंतरिक सुख, मानसिक शांति एवं चित्त-संतोष (Inner Peace & Sukha Bhava):")
        col_pc1, col_pc2 = st.columns([1.2, 2.8])
        with col_pc1:
            pc_bg = "#EFF6FF" if pea['inner_peace_score'] >= 50 else "#FEF2F2"
            pc_border = "#BFDBFE" if pea['inner_peace_score'] >= 50 else "#FECACA"
            pc_text = "#1E40AF" if pea['inner_peace_score'] >= 50 else "#991B1B"

            st.markdown(f"""
            <div style="background:{pc_bg}; border:1px solid {pc_border}; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:{pc_text}; font-weight:600;">मानसिक शांति सूचकांक</span>
                <div style="font-size:34px; font-weight:800; color:{pc_text}; margin:8px 0;">{pea['inner_peace_score']}%</div>
                <small style="color:{pc_text}; font-weight:600;">{pea['peace_status'].split(' (')[0]}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_pc2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #2563EB; border-radius:8px; padding:14px;">
                <b style="color:#1E3A8A; font-size:15px;">🌊 चित्त स्थिति: {pea['peace_status']}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{pea['peace_desc']}</p>
            </div>
            """, unsafe_allow_html=True)

        col_md1, col_md2 = st.columns(2)
        with col_md1:
            st.markdown("##### 🌙 चन्द्रमा व चतुर्थ भाव के प्रमुख दोष:")
            for d in pea['moon_doshas']:
                st.markdown(f"• {d}")

            st.markdown("##### ⚡ दैनिक तनाव के मुख्य कारक:")
            for st_cause in pea['stressors']:
                st.markdown(f"• {st_cause}")

        with col_md2:
            st.markdown("##### 🌿 मानसिक शांति हेतु अचूक वैदिक उपाय:")
            for up in pea['remedies']:
                st.markdown(f"• {up}")

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {pea['shastriya_basis']}</small>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 6: पूर्वजन्म कर्म, ऋणानुबंध एवं प्रारब्ध (Karma Ledger)
    # ---------------------------------------------------------
    with tab_k6:
        st.markdown("### 🕉️ पूर्वजन्म के कर्म, ऋणानुबंध एवं प्रारब्ध (Past Life Karma & Karmic Debts)")
        st.caption("पंचम भाव (संचित पूर्व-पुण्य), नवम भाव (दैवीय कृपा), राहु-केतु अक्ष एवं आत्मकारक के आधार पर आत्मा का प्रारब्ध:")

        col_km1, col_km2 = st.columns([1.2, 2.8])
        with col_km1:
            st.markdown(f"""
            <div style="background:#FAF5FF; border:1px solid #DDD6FE; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#5B21B6; font-weight:600;">पूर्वजन्म संचित पुण्य</span>
                <div style="font-size:36px; font-weight:800; color:#6D28D9; margin:8px 0;">{krm['purva_punya_score']}%</div>
                <small style="color:#5B21B6; font-weight:600;">{krm['karmic_burden'].split(' (')[0]}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_km2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #7C3AED; border-radius:8px; padding:14px;">
                <b style="color:#4C1D95; font-size:15px;">⚖️ प्रारब्ध भार: {krm['karmic_burden']}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{krm['burden_desc']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### ⚖️ कर्म त्रय संतुलन चक्र (Sanchita, Prarabdha & Kriyamana Balance):")
        c_tr1, c_tr2, c_tr3 = st.columns(3)
        with c_tr1:
            st.markdown(f"""
            <div style="background:#FDF4FF; border:1.5px solid #F0ABFC; border-radius:10px; padding:12px; height:100%;">
                <b style="color:#A21CAF; font-size:14px;">🏺 संचित कर्म (Sanchita): {krm.get('sanchita_pct', 33)}%</b>
                <p style="margin:6px 0; font-size:13px; color:#1E293B;">पूर्वजन्मों के अव्यक्त कर्म-बीज का विशाल भंडार (१२वां व ८वां भाव)। यह आत्मा के अवचेतन में सुरक्षित रहता है।</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(krm.get('sanchita_pct', 33) / 100.0)

        with c_tr2:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:10px; padding:12px; height:100%;">
                <b style="color:#B45309; font-size:14px;">🏹 प्रारब्ध कर्म (Prarabdha): {krm.get('prarabdha_pct', 34)}%</b>
                <p style="margin:6px 0; font-size:13px; color:#1E293B;">इस जन्म में देह धारण कर अनिवार्य रूप से भोगने हेतु आवंटित कर्म (१ला व ६ठा भाव)। यह पूर्व-निर्धारित प्रारब्ध है।</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(krm.get('prarabdha_pct', 34) / 100.0)

        with c_tr3:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:12px; height:100%;">
                <b style="color:#15803D; font-size:14px;">⚡ क्रियमाण कर्म (Kriyamana): {krm.get('kriyamana_pct', 33)}%</b>
                <p style="margin:6px 0; font-size:13px; color:#1E293B;">वर्तमान जीवन में स्वतंत्र इच्छाशक्ति, पुरुषार्थ व विवेक (३रा व ९वां भाव)। इसके द्वारा जातक नए भाग्य का निर्माण करता है।</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(krm.get('kriyamana_pct', 33) / 100.0)

        st.caption(f"📜 **शास्त्रीय सिद्धांत:** 'प्रारब्धं भुज्यमानं तु क्रियमाणेण शाम्यति' — अर्थात वर्तमान के सद्विचार, गुरु-कृपा व तीव्र पुरुषार्थ ({krm.get('kriyamana_pct', 33)}% क्रियमाण) से कठिन से कठिन प्रारब्ध के ताप को भी शांत किया जा सकता है।")
        st.markdown("---")

        # Rahu & Ketu Karmic Axis
        col_rk1, col_rk2 = st.columns(2)
        with col_rk1:
            st.markdown("""
            <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#9A3412; font-size:15px;">🔥 राहु का कर्म-पाश: पूर्वजन्म की अतृप्त वासनाएं</b>
                <p style="margin:6px 0 0 0; color:#7C2D12; font-size:13px; line-height:1.5;">जिस भाव में राहु स्थित होता है, आत्मा वहाँ पिछले जन्मों की अधूरी इच्छाओं को पूरा करने हेतु व्याकुल रहती है:</p>
            </div>
            """, unsafe_allow_html=True)
            st.info(krm['rahu_desire'])

        with col_rk2:
            st.markdown("""
            <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#0F766E; font-size:15px;">🌀 केतु की सिद्धि: पूर्वजन्म की साधना व वैराग्य</b>
                <p style="margin:6px 0 0 0; color:#115E59; font-size:13px; line-height:1.5;">जिस भाव में केतु स्थित होता है, वहाँ आत्मा पूर्वजन्म में सिद्धि प्राप्त कर चुकी है और अंततः सहज अनासक्ति प्राप्त होती है:</p>
            </div>
            """, unsafe_allow_html=True)
            st.success(krm['ketu_mastery'])

        # Atmakaraka Soul Lesson
        st.markdown("#### 🌟 आत्मकारक ग्रह (Atmakaraka) का केंद्रीय आध्यात्मिक पाठ:")
        st.markdown(f"""
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:14px;">
            <b style="color:#1E40AF; font-size:15px;">आत्मा का प्रमुख गृहकार्य (Soul Curriculum) — आत्मकारक: {krm['atmakaraka']}</b>
            <p style="margin:6px 0; color:#1E3A8A; font-size:14px; font-weight:600;">{krm['atmakaraka_lesson']}</p>
            <p style="margin:0; color:#334155; font-size:13px;">{krm['atmakaraka_detail']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Active Karmic Debts
        st.markdown("#### ⛓️ सक्रिय ऋणानुबंध एवं ऋण-मुक्ति के वैदिक उपाय (Active Karmic Debts & Redemption):")
        for debt in krm['active_debts']:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#0F172A; font-size:14px;">• {debt['debt_name']}</b>
                <p style="margin:4px 0; color:#475569; font-size:13px;"><b>लक्षण:</b> {debt['symptom']}</p>
                <p style="margin:0; color:#15803D; font-size:13px;"><b>ऋण-मुक्ति कर्म (Redemption):</b> {debt['redemption']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
            <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {krm['shastriya_basis']}</small>
        </div>
        """, unsafe_allow_html=True)

