import streamlit as st
import pandas as pd
import importlib
from src.jyotish.core.constants import SIGN_NAMES

def render_rules_library_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            '📚 १२,५०० नियम बैंक',
            '🔍 ग्रन्थ एक्सप्लोरर',
            '🔬 कुण्डली अनुसंधान इंजन'
        ]
    st.subheader("📚 १२,५००+ महा-शास्त्रीय नियम बैंक, ग्रन्थ एक्सप्लोरर एवं अनुसंधान इंजन (Vedic Rules & Research Engine)")
    tab_rules_bank, tab_grantha_explorer, tab_research_engine = st.tabs(tabs)
    with tab_rules_bank:

            import importlib
            import src.jyotish.rules.engine as rules_mod
            importlib.reload(rules_mod)
            rules_engine = rules_mod.RulesEngine()
            all_rules = rules_engine.rules

            # Evaluate all rules on current chart dynamically
            with st.spinner("१२,५००+ शास्त्रीय नियमों का स्वचालित मूल्यांकन जारी..."):
                evidences = rules_engine.evaluate_all(chart, None, {}, None)
                ev_by_id = {ev.rule_id: ev for ev in evidences}

            fired_evs = [ev for ev in evidences if ev.fired]
            fired_yogas = [ev for ev in fired_evs if ev.polarity == "+"]
            fired_doshas = [ev for ev in fired_evs if ev.polarity == "-"]

            # Top Status Metrics
            col_rm1, col_rm2, col_rm3, col_rm4 = st.columns(4)
            col_rm1.metric("कुल शास्त्रीय नियम", f"{len(all_rules):,}", "१० महा-ग्रंथ")
            col_rm2.metric("कुण्डली में सक्रिय नियम", f"{len(fired_evs)}", f"सत्यापित ({round((len(fired_evs)/max(1, len(all_rules)))*100)}%)")
            col_rm3.metric("सक्रिय शुभ योग", f"{len(fired_yogas)}", "शुभ फलित")
            col_rm4.metric("सक्रिय दोष / चेतावनियां", f"{len(fired_doshas)}", "सावधानी अपेक्षित")

            st.markdown("---")

            # Filter Controls
            c_f1, c_f2, c_f3 = st.columns([2.5, 2, 1.8])
            search_kw = c_f1.text_input("🔍 नियम खोजें (Search Rule)", placeholder="e.g. गजकेसरी, बुधादित्य, धनेश, षष्ठम, शनि, राहु...")

            grantha_list = ["सभी १० महा-ग्रंथ (All Granthas)"] + sorted(list({r.get('source', {}).get('text', 'Unknown') for r in all_rules}))
            sel_grantha = c_f2.selectbox("📖 ग्रन्थ अनुसार फ़िल्टर (By Grantha)", grantha_list)

            cat_list = ["सभी श्रेणियां (All Categories)"] + sorted(list({r.get('category', 'general') for r in all_rules}))
            sel_cat = c_f3.selectbox("🏷️ श्रेणी अनुसार फ़िल्टर (By Category)", cat_list)

            col_chk1, col_chk2 = st.columns([2, 1])
            show_only_fired = col_chk1.checkbox("⭐ केवल आपकी कुण्डली में सक्रिय नियम देखें (Show Only Fired Rules)", value=False)
            sort_order = col_chk2.selectbox("क्रम (Sort)", ["सक्रिय नियम पहले (Fired First)", "ग्रन्थ क्रमानुसार (By Grantha)"])

            # Filtering
            filtered_rules = []
            for r in all_rules:
                r_id = r.get("rule_id", "")
                ev = ev_by_id.get(r_id)
                is_fired = ev.fired if ev else False

                if show_only_fired and not is_fired:
                    continue
                if sel_grantha != "सभी १० महा-ग्रंथ (All Granthas)" and r.get('source', {}).get('text') != sel_grantha:
                    continue
                if sel_cat != "सभी श्रेणियां (All Categories)" and r.get('category') != sel_cat:
                    continue
                if search_kw:
                    kw_l = search_kw.lower()
                    match_txt = f"{r.get('rule_name_hi', '')} {r.get('rule_name_en', '')} {r_id} {r.get('effect', {}).get('description_hi', '')}".lower()
                    if kw_l not in match_txt:
                        continue
                filtered_rules.append(r)

            if sort_order == "सक्रिय नियम पहले (Fired First)":
                filtered_rules.sort(key=lambda r: (0 if ev_by_id.get(r['rule_id'], None) and ev_by_id[r['rule_id']].fired else 1, r.get('source', {}).get('text', '')))

            st.caption(f"प्रदर्शित शास्त्रीय नियम: **{len(filtered_rules)}** / {len(all_rules)} (सक्रिय: {sum(1 for r in filtered_rules if ev_by_id.get(r['rule_id']) and ev_by_id[r['rule_id']].fired)})")

            # Render Rules (Paginate to top 150 for ultra-fast rendering)
            limit = 150
            rules_slice = filtered_rules[:limit]

            for r in rules_slice:
                r_id = r.get("rule_id", "")
                ev = ev_by_id.get(r_id)
                is_fired = ev.fired if ev else False
                pol = r.get("effect", {}).get("polarity", "+")
                pol_badge = "🟢 शुभ योग (+)" if pol == "+" else "🔴 अनिष्ट / दोष (-)"
                status_badge = "✅ आपकी कुण्डली में सक्रिय (Fired)" if is_fired else "⚪ निष्क्रिय (Inactive)"
                status_color = "#15803D" if is_fired else "#64748B"
                border_color = "#86EFAC" if is_fired else "#CBD5E1"
                bg_color = "#F0FDF4" if is_fired else "#FFFFFF"

                with st.expander(f"{'⭐ ' if is_fired else ''}{r.get('rule_name_hi', '')} — {r.get('rule_name_en', '')} [{status_badge}]", expanded=is_fired):
                    st.markdown(f"""
                    <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:8px; padding:12px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:6px;">
                            <b style="color:{status_color}; font-size:14px;">स्थिति: {status_badge}</b>
                            <span style="font-size:12px; color:#475569;"><b>नियम ID:</b> {r_id} | <b>प्रभाव:</b> {pol_badge}</span>
                        </div>
                        <div style="font-size:13px; color:#1E293B; margin-bottom:6px;">
                            <b>📖 ग्रन्थ:</b> {r.get('source', {}).get('text', 'Unknown')} <i>({r.get('source', {}).get('chapter', 'General')})</i> | 
                            <b>ऋषि/लेखक:</b> {r.get('source', {}).get('author', 'Vedic')} | 
                            <b>पद्धति:</b> {r.get('school', 'Classical')} | 
                            <b>श्रेणी:</b> {r.get('category', 'yoga')}
                        </div>
                        <p style="margin:6px 0; color:#0F172A; font-size:13.5px; line-height:1.5;">
                            <b>शास्त्रीय फलित:</b> {ev.explanation_hi if (ev and is_fired) else r.get('effect', {}).get('description_hi', '')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if r.get('modifiers'):
                        mods_txt = " • ".join([f"{m.get('condition', '')} ({m.get('delta', '')})" for m in r['modifiers']])
                        st.caption(f"🔧 संशोधक (Modifiers): {mods_txt}")

            if len(filtered_rules) > limit:
                st.info(f"💡 कुल {len(filtered_rules)} में से प्रथम {limit} नियम प्रदर्शित हैं। विशिष्ट नियम खोजने हेतु ऊपर 'खोजें' बॉक्स या 'ग्रन्थ' फ़िल्टर का प्रयोग करें।")


        # =============================================================
    with tab_grantha_explorer:
        st.markdown("### 🔍 शास्त्रीय ग्रन्थ नियम एक्सप्लोरर एवं १-क्लिक कुण्डली वेध (Grantha Rules Explorer)")
        st.caption("बृहत्पाराशर होराशास्त्र, बृहज्जातक, सारावली, फलदीपिका, जैमिनी सूत्र, लाल किताब, के.पी. ज्योतिष, नाड़ी एवं प्रश्न मार्ग के १२,५००+ नियमों का लाइव सर्च व कुण्डली परीक्षण:")

        try:
            import importlib
            import src.jyotish.services.rules_explorer as re_mod
            importlib.reload(re_mod)
            re_svc = re_mod.default_rules_explorer_service

            stats = re_svc.get_stats()
            total_rules_indexed = stats["total_rules"]

            # Top KPI metrics
            c_rk1, c_rk2, c_rk3 = st.columns(3)
            with c_rk1:
                st.metric("इंडेक्स किए गए कुल नियम", f"{total_rules_indexed:,}", "१५ शास्त्रीय ग्रन्थ")
            with c_rk2:
                st.metric("ग्रन्थ पुस्तकालय (Granthas)", f"{stats['granthas_count']} ग्रन्थ", "पारंपरिक व आधुनिक")
            with c_rk3:
                st.metric("खोज क्षमता (Engine)", "अति-तीव्र (Sub-millisecond)", "In-memory AST Index")

            # Search & Filter Bar
            c_qs1, c_qs2, c_qs3 = st.columns([2.5, 2, 1])
            with c_qs1:
                search_q = st.text_input("🔍 नियम या योग खोजें (Search by Keyword)", placeholder="उदा: गजकेसरी, उच्च, नीच, अष्टम, केमद्रुम, विवाह, धन...", key="re_search_q")
            with c_qs2:
                g_options = ["सभी ग्रन्थ (All Granthas)"] + list(stats["breakdown"].keys())
                sel_g = st.selectbox("📖 ग्रन्थ चुनें (Filter Grantha)", g_options, key="re_sel_grantha")
            with c_qs3:
                max_re = st.selectbox("अधिकतम परिणाम", [20, 50, 100, 200], index=1, key="re_max_re")

            grantha_arg = None if sel_g == "सभी ग्रन्थ (All Granthas)" else sel_g
            search_results = re_svc.search_rules(query=search_q, grantha_filter=grantha_arg, max_results=max_re)

            st.caption(f"प्राप्त परिणाम: **{len(search_results)}** नियम")

            # Display Search Results
            for idx, r in enumerate(search_results):
                r_id = r.get("rule_id", f"R_{idx}")
                r_name_hi = r.get("rule_name_hi", r_id)
                r_name_en = r.get("rule_name_en", "")
                src_meta = r.get("source", {})
                grantha_title = r.get("_grantha", src_meta.get("text", "Classical"))
                eff = r.get("effect", {})
                desc_hi = eff.get("description_hi", "")
                pol = eff.get("polarity", "+")
                themes = eff.get("themes", [])

                # Live Test on Current Chart
                is_active, active_reason = re_svc.test_rule_on_chart(r, chart)

                status_badge = "✅ इस कुण्डली में सक्रिय" if is_active else "⚪ इस कुण्डली में निष्क्रिय"
                badge_bg = "#DCFCE7" if is_active else "#F1F5F9"
                badge_fg = "#166534" if is_active else "#64748B"
                border_color = "#86EFAC" if is_active else "#CBD5E1"
                left_border = "#16A34A" if is_active else "#94A3B8"

                with st.expander(f"{'⭐ ' if is_active else ''}{r_name_hi} — {r_name_en} [{status_badge}]", expanded=is_active):
                    st.markdown(
                        f'<div style="background:#FFFFFF; border:1px solid {border_color}; border-left:5px solid {left_border}; padding:12px; border-radius:8px; margin-bottom:8px;">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:6px;">'
                        f'<div><b>📖 ग्रन्थ:</b> <span style="color:#2563EB; font-weight:700;">{grantha_title}</span> ({src_meta.get("chapter", "अध्याय")}, {src_meta.get("shloka", "")})</div>'
                        f'<span style="background:{badge_bg}; color:{badge_fg}; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800;">{status_badge}</span>'
                        f'</div>'
                        f'<div style="font-size:13.5px; color:#0F172A; margin:6px 0; line-height:1.5;"><b>📜 शास्त्रीय फल:</b> {desc_hi}</div>'
                        f'<div style="font-size:12px; color:#475569;">🎯 <b>विषय:</b> {", ".join(themes) if themes else "सामान्य"} | <b>नियम ID:</b> <code>{r_id}</code></div>'
                        f'<div style="margin-top:8px; padding:6px 10px; background:#F8FAFC; border-radius:6px; font-size:12px; color:#1E293B;">'
                        f'<b>🔎 कुण्डली वेध परिणाम:</b> {active_reason}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        except Exception as _e_re:
            st.error(f"नियम एक्सप्लोरर में त्रुटि: {_e_re}")

    with tab_research_engine:
        st.markdown("### 🔍 शास्त्रीय योग एवं कुण्डली अनुसंधान इंजन (Astrological Research & Query Engine)")
        st.write("शास्त्रीय शोध इंजन के समान अपने सहेजे गए जातकों एवं ऐतिहासिक बेंचमार्क कुण्डलियों में विशिष्ट शास्त्रीय योगों, ग्रह स्थितियों व उच्च-नीच अवस्थाओं की खोज।")

        from src.jyotish.services.research_engine import default_research_engine, AVAILABLE_RESEARCH_YOGAS

        c_rq1, c_rq2 = st.columns([2, 1])
        with c_rq1:
            sel_yogas = st.multiselect(
                "🎯 शास्त्रीय योग फ़िल्टर (Select Classical Yogas)",
                options=[y["key"] for y in AVAILABLE_RESEARCH_YOGAS],
                format_func=lambda x: next((y["name_hi"] for y in AVAILABLE_RESEARCH_YOGAS if y["key"] == x), x),
                placeholder="उदा. गजकेसरी, बुधादित्य, रुचक, विपरीत राजयोग, नीचभंग, मांगलिक..."
            )
        with c_rq2:
            sel_lagna = st.multiselect(
                "🏛️ लग्न राशि फ़िल्टर (Lagna Sign)",
                options=list(range(1, 13)),
                format_func=lambda x: f"{x}. {SIGN_NAMES[x-1]}",
                placeholder="सभी लग्न (All)"
            )

        c_rq3, c_rq4, c_rq5 = st.columns(3)
        with c_rq3:
            p_house_p = st.selectbox("🪐 ग्रह (Planet in House)", ["कोई नहीं (None)", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])
            p_house_h = st.selectbox("📍 भाव (House 1-12)", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) if p_house_p != "कोई नहीं (None)" else None
        with c_rq4:
            p_sign_p = st.selectbox("🪐 ग्रह (Planet in Sign)", ["कोई नहीं (None)", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])
            p_sign_s = st.selectbox("♈ राशि (Sign 1-12)", list(range(1, 13)), format_func=lambda x: f"{x}. {SIGN_NAMES[x-1]}") if p_sign_p != "कोई नहीं (None)" else None
        with c_rq5:
            p_dig_p = st.selectbox("🪐 ग्रह (Planet Dignity)", ["कोई नहीं (None)", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
            p_dig_d = st.selectbox("👑 अवस्था (Dignity)", ["exalted", "debilitated", "own", "retrograde"], format_func=lambda x: {"exalted": "🌟 उच्च (Exalted)", "debilitated": "⚠️ नीच (Debilitated)", "own": "👑 स्वराशि (Own Sign)", "retrograde": "🔄 वक्री (Retrograde)"}[x]) if p_dig_p != "कोई नहीं (None)" else None

        btn_search = st.button("🔍 अनुसंधान एवं खोज प्रारंभ करें (Execute Search)", type="primary", key="btn_run_research_query")

        p_in_h = {"planet": p_house_p, "house": p_house_h} if p_house_p != "कोई नहीं (None)" else None
        p_in_s = {"planet": p_sign_p, "sign": p_sign_s} if p_sign_p != "कोई नहीं (None)" else None
        p_in_d = {"planet": p_dig_p, "dignity": p_dig_d} if p_dig_p != "कोई नहीं (None)" else None

        search_results = default_research_engine.search(
            yoga_keys=sel_yogas if sel_yogas else None,
            lagna_signs=sel_lagna if sel_lagna else None,
            planet_in_house=p_in_h,
            planet_in_sign=p_in_s,
            planet_dignity=p_in_d
        )

        st.markdown(f"#### 📋 अनुसंधान परिणाम: **{len(search_results)}** कुण्डलियां मेल खाती हैं")

        if search_results:
            for idx, r in enumerate(search_results):
                with st.container():
                    c_card1, c_card2, c_card3 = st.columns([2.5, 3.5, 1.2])
                    with c_card1:
                        st.markdown(f"**👤 {r['name']}**")
                        st.caption(f"📁 {r['folder']} | लग्न: **{r['lagna']}** | चंद्र: **{r['moon_sign']} ({r['nakshatra']})**")
                    with c_card2:
                        tags_html = " ".join([f"<span style='background:#EFF6FF; color:#1D4ED8; padding:3px 8px; border-radius:6px; font-size:12px; margin-right:4px; font-weight:700;'>{m}</span>" for m in r["matched_criteria"]])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    with c_card3:
                        if st.button("📂 कुण्डली खोलें", key=f"load_res_c_{idx}_{r['id']}"):
                            bd = r["birth_data"]
                            st.session_state["birth_name"] = bd.get("name", r["name"])
                            st.session_state["birth_date"] = datetime.strptime(bd["birth_date"], "%Y-%m-%d").date() if isinstance(bd.get("birth_date"), str) else bd.get("birth_date")
                            st.session_state["birth_time"] = datetime.strptime(bd["birth_time"], "%H:%M:%S").time() if isinstance(bd.get("birth_time"), str) and ":" in bd.get("birth_time") else bd.get("birth_time")
                            st.session_state["birth_city"] = bd.get("city", "नई दिल्ली")
                            st.success(f"कुण्डली '{r['name']}' सक्रिय हो गई!")
                            st.rerun()
                    st.divider()
        else:
            st.warning("दिए गए मापदंडों से मेल खाती कोई कुण्डली नहीं मिली। कृपया फ़िल्टर शिथिल करके पुनः प्रयास करें।")


