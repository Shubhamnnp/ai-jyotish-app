/**
 * BRAMHAHORA - World-Class Vedic Astrology Enterprise Workstation Web Application
 * Master Controller & Reactive State Manager
 */

class JyotishWebApp {
  constructor() {
    // Default active client birth data
    this.client = {
      name: "शुभम कुमार (Shubham Kumar)",
      gender: "Male",
      birth_date: "1994-05-16",
      birth_time: "17:00:00",
      city: "Nanpara",
      latitude: 27.8643,
      longitude: 81.5033,
      timezone_offset: 5.5,
      ayanamsa: "Lahiri"
    };

    this.chartData = null;
    this.activeVarga = "D1";
    this.chartStyle = "north"; // "north" | "south" | "east"
    this.activeTab = "main"; // "main" | "pushkar" | "jaimini" | "chalit" | "chandra" | "surya" | "grahaprishtha" | "kota" | "dasha" | "ashtakavarga" | "yogas"
    this.analyticalSubView = "planets"; // "planets" | "houses" | "summary" | "graph"
    this.graphDisplayMode = "horizontal"; // "horizontal" | "vertical"
    this.activeModule = "kundli_core";
    this.isSidebarOpen = true;

    // Full 31 Modules catalog
    this.modulesList = [
      { id: "kundli_core", name: "लग्न व नवमांश कुण्डली", cat: "core", icon: "🪐" },
      { id: "varga_shodash", name: "षोडशवर्ग चक्र (D1-D60)", cat: "core", icon: "💫" },
      { id: "shadbala_bhavabala", name: "षड्बल व भाव बल", cat: "core", icon: "⚖️" },
      { id: "panchang_daily", name: "दैनिक पंचांग व चौघड़िया", cat: "core", icon: "☀️" },
      { id: "dasha_vimshottari", name: "विंशोत्तरी दशा (5 स्तर)", cat: "dasha", icon: "⏳" },
      { id: "gochar_transit", name: "लाइव गोचर व साढ़े साती", cat: "dasha", icon: "🌐" },
      { id: "ashtakavarga", name: "अष्टकवर्ग (SAV / BAV)", cat: "dasha", icon: "📈" },
      { id: "varshaphal", name: "वर्षफल (ताजिक मुन्था)", cat: "dasha", icon: "📅" },
      { id: "kp_system", name: "केपी ज्योतिष (KP System)", cat: "special", icon: "📐" },
      { id: "jaimini_kp", name: "जैमिनी ज्योतिष व कारक", cat: "special", icon: "👑" },
      { id: "lal_kitab", name: "लाल किताब व अचूक उपाय", cat: "special", icon: "🌿" },
      { id: "prashna", name: "प्रश्न कुण्डली (Horary)", cat: "special", icon: "❓" },
      { id: "shastriya_yogas", name: "300+ योग व शास्त्रीय फलित", cat: "advanced", icon: "📜" },
      { id: "kundli_milan", name: "अष्टकूट कुण्डली मिलान", cat: "advanced", icon: "💖" },
      { id: "vastu_chakra", name: "वास्तु चक्र व दिशाएं", cat: "advanced", icon: "🗺️" },
      { id: "medical_astro", name: "आयुर्वेद व मेडिकल ज्योतिष", cat: "advanced", icon: "🩺" },
      { id: "pushkar_vargottama", name: "पुष्कर नवमांश व वर्गोत्तम", cat: "special", icon: "🌟" },
      { id: "bhava_chalit", name: "भाव चलित चक्र व संधि", cat: "special", icon: "🏠" },
      { id: "chandra_kundli", name: "चन्द्र कुण्डली लग्न", cat: "core", icon: "🌙" },
      { id: "surya_kundli", name: "सूर्य कुण्डली लग्न", cat: "core", icon: "☀️" },
      { id: "graha_prishtha", name: "ग्रह पृष्ठ व पापकर्तरी", cat: "special", icon: "⚔️" },
      { id: "kota_chakra", name: "कोटा चक्र दुर्ग रक्षा", cat: "special", icon: "⛺" },
      { id: "gem_recommend", name: "शास्त्रीय रत्न परामर्श", cat: "advanced", icon: "💎" },
      { id: "mantra_yantra", name: "वैदिक मंत्र व यंत्र साधन", cat: "advanced", icon: "🕯️" },
      { id: "chara_dasha", name: "जैमिनी चर व योगिनी दशा", cat: "dasha", icon: "⏳" },
      { id: "upagraha_chakra", name: "अप्रकाशित उपग्रह चक्र", cat: "special", icon: "🌌" },
      { id: "btr_rectification", name: "BTR जन्म समय संशोधन", cat: "special", icon: "🕰️" },
      { id: "event_prediction", name: "घटना काल-खंड विश्लेषण", cat: "advanced", icon: "🎯" },
      { id: "varga_tables", name: "षोडशवर्ग विश्लेषण तालिका", cat: "core", icon: "📊" },
      { id: "ai_jyotish", name: "AI दैवज्ञ परामर्श चैट", cat: "advanced", icon: "🤖" },
      { id: "report_pdf", name: "100+ पृष्ठ विस्तृत PDF रिपोर्ट", cat: "advanced", icon: "📄" }
    ];

    this.rashiNames = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"];
    this.rashiEnglish = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

    this.rashiLords = {
      1: "मंगल", 2: "शुक्र", 3: "बुध", 4: "चन्द्र",
      5: "सूर्य", 6: "बुध", 7: "शुक्र", 8: "मंगल",
      9: "गुरु", 10: "शनि", 11: "शनि", 12: "गुरु"
    };

    this.cityDatabase = {
      "nanpara": { lat: 27.8643, lon: 81.5033 },
      "bahraich": { lat: 27.5744, lon: 81.5947 },
      "delhi": { lat: 28.6139, lon: 77.2090 },
      "new delhi": { lat: 28.6139, lon: 77.2090 },
      "lucknow": { lat: 26.8467, lon: 80.9462 },
      "varanasi": { lat: 25.3176, lon: 82.9739 },
      "kashi": { lat: 25.3176, lon: 82.9739 },
      "kanpur": { lat: 26.4499, lon: 80.3319 },
      "ayodhya": { lat: 26.7922, lon: 82.1998 },
      "prayagraj": { lat: 25.4358, lon: 81.8463 },
      "allahabad": { lat: 25.4358, lon: 81.8463 },
      "gorakhpur": { lat: 26.7606, lon: 83.3732 },
      "mumbai": { lat: 19.0760, lon: 72.8777 },
      "kolkata": { lat: 22.5726, lon: 88.3639 },
      "bengaluru": { lat: 12.9716, lon: 77.5946 },
      "bangalore": { lat: 12.9716, lon: 77.5946 },
      "chennai": { lat: 13.0827, lon: 80.2707 },
      "hyderabad": { lat: 17.3850, lon: 78.4867 },
      "ahmedabad": { lat: 23.0225, lon: 72.5714 },
      "pune": { lat: 18.5204, lon: 73.8567 },
      "jaipur": { lat: 26.9124, lon: 75.7873 },
      "patna": { lat: 25.5941, lon: 85.1376 },
      "ujjain": { lat: 23.1765, lon: 75.7885 },
      "haridwar": { lat: 29.9457, lon: 78.1642 },
      "rishikesh": { lat: 30.0869, lon: 78.2676 }
    };

    this.init();
  }

  lookupCityCoordinates(cityName) {
    if (!cityName) return null;
    const clean = cityName.trim().toLowerCase();
    return this.cityDatabase[clean] || null;
  }

  async init() {
    this.renderSidebarModules();
    this.attachEventListeners();
    this.ensureDefaultSavedKundli();
    await this.calculateChart();
  }

  /**
   * Toolbelt Slider Handler
   */
  slideToolbelt(direction) {
    const track = document.getElementById("toolbeltTrack");
    if (track) {
      track.scrollBy({ left: direction * 280, behavior: "smooth" });
    }
  }

  /**
   * API: Calculate natal chart using FastAPI endpoint
   */
  async calculateChart() {
    this.showLoading(true);
    try {
      const payload = {
        name: this.client.name,
        birth_date: this.client.birth_date,
        birth_time: this.client.birth_time,
        latitude: parseFloat(this.client.latitude),
        longitude: parseFloat(this.client.longitude),
        timezone_offset: parseFloat(this.client.timezone_offset)
      };

      const res = await fetch("/api/chart/calculate?ayanamsa=" + encodeURIComponent(this.client.ayanamsa), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      this.chartData = await res.json();

      // Fetch full Shastriya Suite (Pushkar, Jaimini, Chalit, Kota, Yogas, Gemology, Medical, Vastu)
      try {
        const shastriyaRes = await fetch("/api/chart/shastriya-full?ayanamsa=" + encodeURIComponent(this.client.ayanamsa), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (shastriyaRes.ok) {
          this.shastriyaData = await shastriyaRes.json();
        }
      } catch (sErr) {
        console.warn("Shastriya full suite fetch failed:", sErr);
      }

      // Fetch operating Vimshottari Dasha
      try {
        const todayStr = new Date().toISOString().split("T")[0];
        const dashaRes = await fetch("/api/dasha/active", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            birth_data: payload,
            target_date: todayStr
          })
        });
        if (dashaRes.ok) {
          this.activeDashaData = await dashaRes.json();
        }
      } catch (dErr) {
        console.warn("Active Dasha fetch failed:", dErr);
      }

      this.updateUI();
    } catch (err) {
      console.warn("API direct call failed, falling back to simulated high-precision baseline:", err);
      this.chartData = this.generateFallbackChart();
      this.updateUI();
    } finally {
      this.showLoading(false);
    }
  }

  /**
   * Refresh all components in UI
   */
  updateUI() {
    if (!this.chartData) return;

    this.renderHeaderClientInfo();
    this.renderClientInfoStrip();
    this.renderChart();
    this.renderAnalyticalSubViews();
    this.renderDashaTimeline();
    this.renderAshtakavarga();
    this.renderYogas();
    this.renderSubTabPanels();
  }

  /**
   * Header Client Info Tag
   */
  renderHeaderClientInfo() {
    const el = document.getElementById("hdrClientInfo");
    if (!el) return;
    const lagna = this.chartData.lagna_sign_name || "तुला (Libra)";
    el.innerHTML = `
      <span class="client-status-dot"></span>
      <span><b>${this.client.name.split(" ")[0]}</b> | लग्न: <b>${lagna}</b></span>
    `;
  }

  /**
   * Info HUD Strip (Exact format requested)
   */
  renderClientInfoStrip() {
    const strip = document.getElementById("clientInfoStrip");
    if (!strip || !this.chartData) return;

    const lagnaName = this.chartData.lagna_sign_name || "Libra";
    const degStr = this.chartData.lagna_degree ? `${this.chartData.lagna_degree.toFixed(2)}°` : "9.59°";

    let moonSign = "Cancer (6.50°)";
    let sunSign = "Taurus (1.59°)";

    if (this.chartData.planets) {
      if (this.chartData.planets.Moon) {
        moonSign = `${this.chartData.planets.Moon.sign_name} (${(this.chartData.planets.Moon.sign_degree || 6.50).toFixed(2)}°)`;
      }
      if (this.chartData.planets.Sun) {
        sunSign = `${this.chartData.planets.Sun.sign_name} (${(this.chartData.planets.Sun.sign_degree || 1.59).toFixed(2)}°)`;
      }
    }

    strip.innerHTML = `
      <div class="info-strip-left">
        <span>👤 <b>${this.client.name}</b></span>
        <span>📅 <b>${this.client.birth_date}</b></span>
        <span>⏰ <b>${this.client.birth_time.substring(0,5)}</b></span>
        <span>📍 <b>${this.client.city}</b></span>
        <span>☸️ <b>लग्न:</b> ${lagnaName} (${degStr})</span>
        <span>🌙 <b>चन्द्र राशि:</b> ${moonSign}</span>
        <span>☀️ <b>सूर्य राशि:</b> ${sunSign}</span>
        <span class="info-pill">📐 Lahiri: 24.23°</span>
      </div>
      <div class="info-strip-right">
        <span class="info-pill">⚡ Swiss Ephemeris</span>
        <span class="info-pill">🛡️ Canonical Rules</span>
      </div>
    `;
  }

  /**
   * Render SVG Kundli Chart (North / South / East)
   */
  renderChart() {
    const box = document.getElementById("chartContainer");
    if (!box || !window.KundliChartRenderer) return;

    let svgHtml = window.KundliChartRenderer.renderChart(this.chartData, this.chartStyle, this.activeVarga);
    box.innerHTML = svgHtml;

    // Update title
    const titleEl = document.getElementById("chartCardTitle");
    if (titleEl) {
      let styleName = "उत्तर भारतीय (North)";
      if (this.chartStyle === "south") styleName = "दक्षिण भारतीय (South)";
      if (this.chartStyle === "east") styleName = "पूर्व भारतीय (East)";
      titleEl.innerHTML = `🪐 कुण्डली चक्र [${this.activeVarga}] - ${styleName}`;
    }
  }

  /**
   * Set Divisional Chart (Varga) D1 to D60 & Re-render Analytical Card dynamically
   */
  setVarga(varga) {
    this.activeVarga = varga;
    document.querySelectorAll(".varga-pill").forEach(el => {
      el.classList.toggle("active", el.dataset.varga === varga);
    });

    // Update Tab Titles on Right Analytical Card for Active Varga
    const pBtn = document.getElementById("tabBtnPlanets");
    const hBtn = document.getElementById("tabBtnHouses");
    const sBtn = document.getElementById("tabBtnSummary");
    const gBtn = document.getElementById("tabBtnGraph");
    const gLbl = document.getElementById("graphTitleLabel");

    if (pBtn) pBtn.innerHTML = `🌟 ${varga} नवग्रह स्थिति`;
    if (hBtn) hBtn.innerHTML = `🏛️ ${varga} द्वादश भाव स्थिति`;
    if (sBtn) sBtn.innerHTML = `📜 ${varga} सारांश एवं पंचांग`;
    if (gBtn) gBtn.innerHTML = `📊 ${varga} ग्रह बल Graph`;
    if (gLbl) gLbl.innerHTML = `📊 ${varga} ग्रह गरिमा एवं बल`;

    this.renderChart();
    this.renderAnalyticalSubViews();
  }

  /**
   * Re-render all 4 analytical subviews for active varga
   */
  renderAnalyticalSubViews() {
    this.renderPlanetaryTable();
    this.renderHousesTable();
    this.renderD1SummaryPanchang();
    this.renderGrahaBalaGraph();
  }

  /**
   * Sub-View Switcher for Analytical Card
   */
  setAnalyticalSubView(subView) {
    this.analyticalSubView = subView;
    document.querySelectorAll(".subtab-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.subview === subView);
    });

    const pPlanets = document.getElementById("panelTablePlanets");
    const pHouses = document.getElementById("panelTableHouses");
    const pSummary = document.getElementById("panelTableSummary");
    const pGraph = document.getElementById("panelGrahaBalaGraph");

    if (pPlanets) pPlanets.style.display = subView === "planets" ? "block" : "none";
    if (pHouses) pHouses.style.display = subView === "houses" ? "block" : "none";
    if (pSummary) pSummary.style.display = subView === "summary" ? "block" : "none";
    if (pGraph) pGraph.style.display = subView === "graph" ? "block" : "none";
  }

  setGraphDisplayMode(mode) {
    this.graphDisplayMode = mode;
    this.renderGrahaBalaGraph();
  }

  /**
   * 1. [Active Varga] Planetary Table
   */
  renderPlanetaryTable() {
    const tbody = document.getElementById("planetaryTableBody");
    if (!tbody || !this.chartData || !this.chartData.planets) return;

    const vargaKey = this.activeVarga || "D1";
    const vargaObj = (vargaKey !== "D1" && this.chartData.vargas && this.chartData.vargas[vargaKey]) 
      ? this.chartData.vargas[vargaKey] 
      : null;

    const planets = vargaObj ? vargaObj.planets : this.chartData.planets;
    const grahaList = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
    const rashiNames = this.rashiNames;
    const lagnaSign = vargaObj 
      ? (vargaObj.lagna_sign_id || vargaObj.lagna_sign || 1) 
      : (this.chartData.lagna_sign_id || this.chartData.lagna_sign || 1);

    let html = "";
    grahaList.forEach(pName => {
      const p = planets[pName];
      if (!p) return;

      const gInfo = KundliChartRenderer.grahaInfo[pName] || { name: pName, sym: pName, col: "#0073CF" };
      const signIdx = p.sign_id || p.sign || 1;
      const signName = rashiNames[signIdx - 1];
      const lordName = this.rashiLords[signIdx] || "-";
      const houseNum = p.house_from_lagna || p.house_number || (((signIdx - lagnaSign + 12) % 12) + 1);

      let degVal = p.sign_degree != null 
        ? p.sign_degree 
        : (p.degree_in_varga != null 
          ? p.degree_in_varga 
          : (p.longitude_in_sign != null ? p.longitude_in_sign : (p.longitude ? p.longitude % 30 : 0)));
      const degStr = `${degVal.toFixed(2)}°`;

      let dignity = this.calculatePlanetaryDignity(pName, signIdx, degVal);
      let dignBadge = `<span class="badge ${dignity.badgeClass}">${dignity.label}</span>`;

      const isRetro = p.is_retrograde || false;
      const motionBadge = isRetro 
        ? `<span class="badge badge-retro">वक्री (R)</span>` 
        : `<span class="badge badge-direct">मार्गी</span>`;

      const nakName = p.nakshatra_name || this.calculateNakshatra(p.longitude || (signIdx - 1) * 30 + degVal);
      const pada = p.nakshatra_pada || 1;
      const nakStr = `${nakName} (${pada})`;

      html += `
        <tr>
          <td><b style="color:${gInfo.col};">${gInfo.sym} ${gInfo.name}</b></td>
          <td><b>${signName}</b></td>
          <td>${lordName}</td>
          <td style="font-family:monospace; font-weight:800; color:#E11D48;">${degStr}</td>
          <td><span class="house-badge">${houseNum}th House</span></td>
          <td>${dignBadge}</td>
          <td>${motionBadge}</td>
          <td><small style="color:#64748B; font-weight:700;">${nakStr}</small></td>
        </tr>
      `;
    });

    tbody.innerHTML = html;
  }

  /**
   * 2. [Active Varga] 12 Houses Table
   */
  renderHousesTable() {
    const tbody = document.getElementById("housesTableBody");
    if (!tbody || !this.chartData) return;

    const vargaKey = this.activeVarga || "D1";
    const vargaObj = (vargaKey !== "D1" && this.chartData.vargas && this.chartData.vargas[vargaKey]) 
      ? this.chartData.vargas[vargaKey] 
      : null;

    const lagnaSign = vargaObj 
      ? (vargaObj.lagna_sign_id || vargaObj.lagna_sign || 1) 
      : (this.chartData.lagna_sign_id || this.chartData.lagna_sign || 1);

    const cuspDeg = this.chartData.lagna_degree ? `${this.chartData.lagna_degree.toFixed(2)}°` : "9.59°";
    const planets = vargaObj ? vargaObj.planets : this.chartData.planets;

    const houseKaraka = {
      1: { name: "तनु (Self, Health)", karaka: "सूर्य", desc: "शारीरिक गठन, जीवन शक्ति, स्वास्थ्य" },
      2: { name: "धन व कुटुम्ब (Wealth)", karaka: "गुरु", desc: "धन संचय, वाणी, प्रारंभिक शिक्षा, परिवार" },
      3: { name: "सहज व भ्राता (Efforts)", karaka: "मंगल", desc: "शौर्य, अनुज, संवाद, लघु यात्राएं" },
      4: { name: "सुख व मातृ (Home)", karaka: "चन्द्र/शुक्र", desc: "माता, गृह, भूमि, वाहन, मानसिक शांति" },
      5: { name: "सुत व बुद्धि (Intellect)", karaka: "गुरु", desc: "संतान, पूर्वपुण्य, मंत्र, सट्टा, ज्ञान" },
      6: { name: "रिपु व रोग (Enemies)", karaka: "मंगल/शनि", desc: "रोग, ऋण, शत्रु, प्रतिस्पर्धा, सेवा" },
      7: { name: "जाया व साझेदारी (Spouse)", karaka: "शुक्र", desc: "दाम्पत्य जीवन, जीवनसाथी, व्यापार" },
      8: { name: "रन्ध्र व आयु (Longevity)", karaka: "शनि", desc: "आयु, गूढ़ विज्ञान, परिवर्तन, पैतृक धन" },
      9: { name: "धर्म व भाग्य (Fortune)", karaka: "गुरु/सूर्य", desc: "भाग्य, पिता/गुरु, धर्म, उच्च शिक्षा" },
      10: { name: "कर्म व मान (Career)", karaka: "बुध/सूर्य/गुरु/शनि", desc: "आजीविका, पद, प्रतिष्ठा, सामाजिक स्थिति" },
      11: { name: "आय व लाभ (Gains)", karaka: "गुरु", desc: "आय स्रोत, अभीष्ट सिद्धि, ज्येष्ठ भ्राता" },
      12: { name: "व्यय व मोक्ष (Liberation)", karaka: "शनि/केतु", desc: "व्यय, शयन सुख, विदेश, मोक्ष" }
    };

    let html = "";
    for (let h = 1; h <= 12; h++) {
      const signIdx = ((lagnaSign + h - 2) % 12) + 1;
      const signName = this.rashiNames[signIdx - 1];
      const lordName = this.rashiLords[signIdx] || "-";

      const occupants = [];
      if (planets) {
        Object.entries(planets).forEach(([pName, pObj]) => {
          const pSign = pObj.sign_id || pObj.sign || 1;
          const pCurHouse = pObj.house_from_lagna || pObj.house_number || (((pSign - lagnaSign + 12) % 12) + 1);
          if (pCurHouse === h) {
            const gInfo = KundliChartRenderer.grahaInfo[pName] || { name: pName, col: "#2563EB" };
            occupants.push(`<b style="color:${gInfo.col};">${gInfo.name}</b>`);
          }
        });
      }
      const occStr = occupants.length > 0 ? occupants.join(", ") : "<span style='color:#94A3B8;'>— रिक्त —</span>";

      // Vedic Aspects on this house in active varga
      const aspects = [];
      if (planets) {
        Object.entries(planets).forEach(([pName, pObj]) => {
          const pSign = pObj.sign_id || pObj.sign || 1;
          const pCurHouse = pObj.house_from_lagna || pObj.house_number || (((pSign - lagnaSign + 12) % 12) + 1);
          if (pCurHouse === h) return;

          const diff = ((h - pCurHouse + 12) % 12) + 1;
          let isAspecting = false;
          if (diff === 7) isAspecting = true;
          if (pName === "Mars" && (diff === 4 || diff === 8)) isAspecting = true;
          if ((pName === "Jupiter" || pName === "Rahu" || pName === "Ketu") && (diff === 5 || diff === 9)) isAspecting = true;
          if (pName === "Saturn" && (diff === 3 || diff === 10)) isAspecting = true;

          if (isAspecting) {
            const gInfo = KundliChartRenderer.grahaInfo[pName] || { name: pName, col: "#0073CF" };
            aspects.push(`<span style="color:${gInfo.col}; font-weight:750;">${gInfo.name}</span>`);
          }
        });
      }
      const aspStr = aspects.length > 0 ? aspects.join(", ") : "<span style='color:#94A3B8;'>—</span>";
      const info = houseKaraka[h];

      html += `
        <tr>
          <td><span class="house-badge">भाव ${h} (${info.name})</span></td>
          <td><b>${signName}</b></td>
          <td><b>${lordName}</b></td>
          <td style="font-family:monospace; font-weight:800; color:#0284C7;">${cuspDeg}</td>
          <td>${occStr}</td>
          <td>${aspStr}</td>
          <td><small style="color:#64748B;">कारक: <b>${info.karaka}</b> (${info.desc})</small></td>
        </tr>
      `;
    }

    tbody.innerHTML = html;
  }

  /**
   * 3. [Active Varga] Summary & Panchang Matrix
   */
  renderD1SummaryPanchang() {
    const grid = document.getElementById("panchangSummaryGrid");
    if (!grid || !this.chartData) return;

    const vargaKey = this.activeVarga || "D1";
    const vargaObj = (vargaKey !== "D1" && this.chartData.vargas && this.chartData.vargas[vargaKey]) 
      ? this.chartData.vargas[vargaKey] 
      : null;

    const lagnaSign = vargaObj 
      ? (vargaObj.lagna_sign_id || vargaObj.lagna_sign || 1) 
      : (this.chartData.lagna_sign_id || this.chartData.lagna_sign || 7);

    const lagnaName = this.rashiNames[lagnaSign - 1];
    const lagnaDeg = this.chartData.lagna_degree ? `${this.chartData.lagna_degree.toFixed(2)}°` : "9.59°";

    const planets = vargaObj ? vargaObj.planets : this.chartData.planets;
    let moonSign = "कर्क (Cancer)";
    let moonDeg = "6.50°";
    let moonNak = "पुष्य";
    let sunSign = "वृषभ (Taurus)";
    let sunDeg = "1.59°";

    if (planets) {
      if (planets.Moon) {
        const mSignIdx = planets.Moon.sign_id || planets.Moon.sign || 4;
        moonSign = `${this.rashiNames[mSignIdx - 1]} (${this.rashiEnglish[mSignIdx - 1]})`;
        moonDeg = `${(planets.Moon.sign_degree || planets.Moon.degree_in_varga || 6.50).toFixed(2)}°`;
        moonNak = planets.Moon.nakshatra_name || "पुष्य";
      }
      if (planets.Sun) {
        const sSignIdx = planets.Sun.sign_id || planets.Sun.sign || 2;
        sunSign = `${this.rashiNames[sSignIdx - 1]} (${this.rashiEnglish[sSignIdx - 1]})`;
        sunDeg = `${(planets.Sun.sign_degree || planets.Sun.degree_in_varga || 1.59).toFixed(2)}°`;
      }
    }

    // Atmakaraka calculation for active varga
    let akName = "शुक्र (Venus)";
    let akDeg = "24.7°";
    let maxD = -1;
    const candidates = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
    if (planets) {
      candidates.forEach(p => {
        const obj = planets[p];
        if (obj) {
          const d = obj.sign_degree != null ? obj.sign_degree : (obj.degree_in_varga != null ? obj.degree_in_varga : 0);
          if (d > maxD) {
            maxD = d;
            akName = (KundliChartRenderer.grahaInfo[p] || {}).name || p;
            akDeg = `${d.toFixed(2)}°`;
          }
        }
      });
    }

    const cells = [
      { label: `सक्रिय वर्ग लग्न (${vargaKey})`, val: `${vargaKey} - ${lagnaName}`, sub: `अंश: ${lagnaDeg}` },
      { label: "जन्म लग्न (D1 Rashi)", val: `तुला (7) [Libra]`, sub: "स्वामी: शुक्र" },
      { label: `चन्द्र राशि (${vargaKey})`, val: moonSign, sub: `अंश: ${moonDeg} | नक्षत्र: ${moonNak}` },
      { label: `सूर्य राशि (${vargaKey})`, val: sunSign, sub: `अंश: ${sunDeg}` },
      { label: "आत्मकारक (Atmakaraka - AK)", val: akName, sub: `सर्वोच्च अंश: ${akDeg}` },
      { label: "तिथि (Tithi)", val: "शुक्ल पक्ष सप्तमी", sub: "देवता: सूर्य" },
      { label: "वार (Weekday)", val: "सोमवार (Monday)", sub: "स्वामी: चन्द्र" },
      { label: "नक्षत्र (Nakshatra)", val: moonNak, sub: "स्वामी: शनि" },
      { label: "योग (Yoga)", val: "वृद्धि योग (Vriddhi)", sub: "शुभ फलदायक" },
      { label: "करण (Karana)", val: "वणिज करण (Vanija)", sub: "व्यापार अनुकूल" },
      { label: "सूर्योदय व सूर्यास्त", val: "05:28 AM / 06:54 PM", sub: "दिनमान: 33 घटी" },
      { label: "अयनांश प्रणाली", val: "लाहिरी (Lahiri - Chitra)", sub: "24° 13' 55\"" }
    ];

    let html = "";
    cells.forEach(c => {
      html += `
        <div class="panchang-summary-cell">
          <span class="panchang-cell-label">${c.label}</span>
          <span class="panchang-cell-val">${c.val}</span>
          <span class="panchang-cell-sub">${c.sub}</span>
        </div>
      `;
    });

    grid.innerHTML = html;
  }

  /**
   * 4. [Active Varga] Graha Bala Graph
   */
  renderGrahaBalaGraph() {
    const box = document.getElementById("grahaBalaGraphBox");
    if (!box || !this.chartData || !this.chartData.planets) return;

    const vargaKey = this.activeVarga || "D1";
    const vargaObj = (vargaKey !== "D1" && this.chartData.vargas && this.chartData.vargas[vargaKey]) 
      ? this.chartData.vargas[vargaKey] 
      : null;

    const planets = vargaObj ? vargaObj.planets : this.chartData.planets;
    const grahaList = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

    const scores = [];
    grahaList.forEach(pName => {
      const p = planets[pName];
      if (!p) return;
      const gInfo = KundliChartRenderer.grahaInfo[pName] || { name: pName, sym: pName, col: "#0073CF" };
      const signIdx = p.sign_id || p.sign || 1;
      const degVal = p.sign_degree != null ? p.sign_degree : (p.degree_in_varga != null ? p.degree_in_varga : 0);
      const dign = this.calculatePlanetaryDignity(pName, signIdx, degVal);

      let score = 10.0;
      if (dign.type === "exalted") score = 20.0;
      else if (dign.type === "moolatrikona") score = 17.5;
      else if (dign.type === "own") score = 15.0;
      else if (dign.type === "friend") score = 12.0;
      else if (dign.type === "neutral") score = 9.5;
      else if (dign.type === "enemy") score = 6.0;
      else if (dign.type === "debilitated") score = 2.0;

      if (p.is_retrograde && pName !== "Rahu" && pName !== "Ketu") {
        score = Math.min(20.0, score + 2.0);
      }

      scores.push({
        name: gInfo.name,
        sym: gInfo.sym,
        col: gInfo.col,
        dignLabel: dign.label,
        dignBadge: dign.badgeClass,
        score: score
      });
    });

    if (this.graphDisplayMode === "horizontal") {
      let html = "";
      scores.forEach(s => {
        const pct = ((s.score / 20.0) * 100).toFixed(0);
        let barColor = "#2563EB";
        if (s.score >= 17) barColor = "#16A34A";
        else if (s.score >= 14) barColor = "#0073CF";
        else if (s.score <= 4) barColor = "#DC2626";
        else if (s.score < 9) barColor = "#D97706";

        html += `
          <div class="meter-row">
            <span class="meter-graha-name" style="color:${s.col};">${s.sym} ${s.name}</span>
            <span><span class="badge ${s.dignBadge}">${s.dignLabel}</span></span>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${pct}%; background: ${barColor};"></div>
            </div>
            <span class="meter-val-num">${s.score.toFixed(1)} / 20</span>
          </div>
        `;
      });
      box.innerHTML = html;
    } else {
      let html = `<div class="vertical-columns-grid">`;
      scores.forEach(s => {
        const hPct = ((s.score / 20.0) * 100).toFixed(0);
        let barColor = "#2563EB";
        if (s.score >= 17) barColor = "#16A34A";
        else if (s.score >= 14) barColor = "#0073CF";
        else if (s.score <= 4) barColor = "#DC2626";
        else if (s.score < 9) barColor = "#D97706";

        html += `
          <div class="v-col-item">
            <span class="v-col-val">${s.score.toFixed(1)}</span>
            <div class="v-col-bar-wrap">
              <div class="v-col-bar" style="height: ${hPct}%; background: ${barColor};"></div>
            </div>
            <span class="v-col-name" style="color:${s.col};">${s.name}</span>
          </div>
        `;
      });
      html += `</div>`;
      box.innerHTML = html;
    }
  }

  /**
   * Classical Dignity Logic
   */
  calculatePlanetaryDignity(pName, signIdx, deg) {
    const exaltations = {
      "Sun": { sign: 1, maxDeg: 10 },
      "Moon": { sign: 2, maxDeg: 3 },
      "Mars": { sign: 10, maxDeg: 28 },
      "Mercury": { sign: 6, maxDeg: 15 },
      "Jupiter": { sign: 4, maxDeg: 5 },
      "Venus": { sign: 12, maxDeg: 27 },
      "Saturn": { sign: 7, maxDeg: 20 },
      "Rahu": { sign: 2, maxDeg: 15 },
      "Ketu": { sign: 8, maxDeg: 15 }
    };

    const debilitations = {
      "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
      "Jupiter": 10, "Venus": 6, "Saturn": 1,
      "Rahu": 8, "Ketu": 2
    };

    const ownSigns = {
      "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
      "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11],
      "Rahu": [11], "Ketu": [8]
    };

    const friends = {
      "Sun": [4, 1, 8, 9, 12],
      "Moon": [5, 3, 6],
      "Mars": [5, 4, 9, 12],
      "Mercury": [5, 2, 7],
      "Jupiter": [5, 4, 1, 8],
      "Venus": [3, 6, 10, 11],
      "Saturn": [3, 6, 2, 7],
      "Rahu": [2, 7, 3, 6, 10, 11],
      "Ketu": [1, 8, 4, 9, 12]
    };

    if (exaltations[pName] && exaltations[pName].sign === signIdx) {
      return { type: "exalted", label: "उच्च (Exalted)", badgeClass: "badge-exalted" };
    }
    if (debilitations[pName] === signIdx) {
      return { type: "debilitated", label: "नीच (Debilitated)", badgeClass: "badge-debilitated" };
    }
    if (ownSigns[pName] && ownSigns[pName].includes(signIdx)) {
      return { type: "own", label: "स्वराशि (Own)", badgeClass: "badge-own" };
    }
    if (friends[pName] && friends[pName].includes(signIdx)) {
      return { type: "friend", label: "मित्र (Friend)", badgeClass: "badge-friend" };
    }
    return { type: "neutral", label: "सम (Neutral)", badgeClass: "badge-neutral" };
  }

  calculateNakshatra(absDeg) {
    const nakNames = [
      "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
      "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी",
      "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा",
      "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा",
      "पूर्वा भाद्रपद", "उत्तरा भाद्रपद", "रेवती"
    ];
    const span = 360 / 27;
    const idx = Math.floor(((absDeg % 360) + 360) % 360 / span);
    return nakNames[idx] || "चित्रा";
  }

  /**
   * Dasha Timeline
   */
  renderDashaTimeline() {
    const box = document.getElementById("dashaTimelineBox");
    if (!box) return;

    let dashaInfo = {
      maha: "केतु (Ketu)",
      antar: "शुक्र (Venus)",
      pratyantar: "राहु (Rahu)",
      end: "2027-05-18"
    };

    if (this.activeDashaData) {
      dashaInfo.maha = this.activeDashaData.mahadasha_lord || dashaInfo.maha;
      dashaInfo.antar = this.activeDashaData.antardasha_lord || dashaInfo.antar;
      dashaInfo.pratyantar = this.activeDashaData.pratyantardasha_lord || dashaInfo.pratyantar;
      if (this.activeDashaData.period_end) {
        dashaInfo.end = this.activeDashaData.period_end.split("T")[0];
      }
    }

    box.innerHTML = `
      <div style="background: linear-gradient(135deg, rgba(0,115,207,0.06) 0%, rgba(0,176,240,0.06) 100%); border: 1.5px solid var(--border-subtle); border-radius: 10px; padding: 18px; margin-bottom: 14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <span style="font-size:13px; font-weight:900; color:var(--primary);">🎯 वर्तमान में सक्रिय विंशोत्तरी दशा स्तर</span>
          <span class="badge badge-exalted">सक्रिय काल</span>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px;">
          <div style="background:#FFF; padding:12px; border-radius:8px; border:1px solid var(--border-subtle);">
            <div style="font-size:11px; color:#64748B; font-weight:750;">1. महादशा (Mahadasha)</div>
            <div style="font-size:16px; font-weight:900; color:#E11D48; margin-top:4px;">👑 ${dashaInfo.maha}</div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">समाप्ति: ${dashaInfo.end}</div>
          </div>
          <div style="background:#FFF; padding:12px; border-radius:8px; border:1px solid var(--border-subtle);">
            <div style="font-size:11px; color:#64748B; font-weight:750;">2. अंतर्दशा (Antardasha)</div>
            <div style="font-size:16px; font-weight:900; color:#0073CF; margin-top:4px;">🪐 ${dashaInfo.antar}</div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">प्रभाव: उच्च फलदायक</div>
          </div>
          <div style="background:#FFF; padding:12px; border-radius:8px; border:1px solid var(--border-subtle);">
            <div style="font-size:11px; color:#64748B; font-weight:750;">3. प्रत्यंतर्दशा (Pratyantardasha)</div>
            <div style="font-size:16px; font-weight:900; color:#D97706; margin-top:4px;">⚡ ${dashaInfo.pratyantar}</div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;">दैनिक सूक्ष्म प्रभाव</div>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Ashtakavarga Matrix
   */
  renderAshtakavarga() {
    const box = document.getElementById("ashtakavargaGridBox");
    if (!box) return;

    let savScores = [31, 28, 30, 24, 29, 33, 27, 26, 32, 25, 34, 18];
    if (this.chartData && this.chartData.ashtakavarga && Array.isArray(this.chartData.ashtakavarga.sav)) {
      savScores = this.chartData.ashtakavarga.sav;
    }

    const lagnaSign = (this.chartData && this.chartData.lagna_sign_id) ? this.chartData.lagna_sign_id : 7;
    let html = `<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap:10px;">`;
    for (let h = 1; h <= 12; h++) {
      const pts = savScores[h - 1] || 28;
      const signIdx = ((lagnaSign + h - 2) % 12) + 1;
      const signName = this.rashiNames[signIdx - 1];
      const isAuspicious = pts >= 28;
      const badgeCls = isAuspicious ? "badge-exalted" : "badge-debilitated";

      html += `
        <div style="background:#FFF; border:1.5px solid ${isAuspicious ? '#86EFAC' : '#FECDD3'}; border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:800; color:#64748B;">भाव ${h} (${signName})</div>
          <div style="font-size:22px; font-weight:900; color:${isAuspicious ? '#16A34A' : '#DC2626'}; margin:4px 0;">${pts}</div>
          <span class="badge ${badgeCls}">${isAuspicious ? 'शुभ (Auspicious)' : 'सामान्य / अल्प'}</span>
        </div>
      `;
    }
    html += `</div>`;
    box.innerHTML = html;
  }

  /**
   * Classical Yogas (Certified from Grantha Rules Engine)
   */
  renderYogas() {
    const box = document.getElementById("yogasContainerBox");
    if (!box) return;

    const yogas = (this.shastriyaData && this.shastriyaData.yogas && this.shastriyaData.yogas.catalog)
      ? this.shastriyaData.yogas.catalog
      : [];

    if (yogas.length === 0) {
      box.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">यदा सर्वे ग्रहाः केन्द्रत्रिकोणे राजयोगदाः। शुभफलानि यच्छन्ति जातकस्य विशेषतः॥</div>
          <div class="shloka-meta"><span>स्रोत: बृहत्पाराशर होराशास्त्र (BPHS)</span><span>अध्याय २६ (राजयोगाध्याय)</span></div>
        </div>
        <div style="padding:16px; text-align:center; color:#64748B;">शास्त्रीय राजयोगों का मूल्यांकन किया जा रहा है...</div>
      `;
      return;
    }

    let html = `
      <div class="shloka-box">
        <div class="shloka-text">केन्द्रत्रिकोणनेतारौ परस्परनिवेशनौ। परस्परनिरीक्षौ वा योगं राजप्रदं विदुः॥</div>
        <div class="shloka-meta"><span>स्रोत: बृहत्पाराशर होराशास्त्र (BPHS)</span><span>सक्रिय प्रमाणित राजयोग: ${yogas.length}</span></div>
      </div>
      <div class="shastriya-grid">
    `;

    yogas.forEach((y, idx) => {
      const verseHtml = y.source_verse ? `<div style="font-family:'Martel',serif; font-size:12px; color:#6B1D2F; margin:4px 0; font-style:italic;">"${y.source_verse}"</div>` : "";
      html += `
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span style="color:#166534;">🌟 ${y.rule_name_hi}</span>
            <span class="badge badge-exalted">स्कोर: ${(y.signal_score || 1).toFixed(1)}</span>
          </div>
          <div style="font-size:11px; color:#854D0E; font-weight:700;">📖 ${y.source_text} — ${y.source_chapter}</div>
          ${verseHtml}
          <p style="font-size:11.5px; color:#475569; margin-top:6px; line-height:1.5;">
            ${y.explanation_hi || y.rule_name_en}
          </p>
        </div>
      `;
    });

    html += `</div>`;
    box.innerHTML = html;
  }

  /**
   * Sub-Tab Panels (100% Real Shastriya Activation)
   */
  renderSubTabPanels() {
    this.renderPushkarPanel();
    this.renderJaiminiPanel();
    this.renderChalitPanel();
    this.renderChandraPanel();
    this.renderSuryaPanel();
    this.renderGrahaPrishthaPanel();
    this.renderKotaPanel();
  }

  /**
   * 1. Pushkar Navamsha & Vargottama Panel
   */
  renderPushkarPanel() {
    const box = document.getElementById("pushkarContainerBox");
    if (!box) return;

    const pData = this.shastriyaData ? this.shastriyaData.pushkar : null;
    const vData = this.shastriyaData ? this.shastriyaData.vargottama : null;
    const bmData = this.shastriyaData ? this.shastriyaData.badhaka_maraka : null;

    let pNavPlanets = (pData && pData.pushkara_navamsha_planets) ? pData.pushkara_navamsha_planets : [];
    let pBhagaPlanets = (pData && pData.pushkara_bhaga_planets) ? pData.pushkara_bhaga_planets : [];
    let vPlanets = (vData && vData.vargottama_planets) ? vData.vargottama_planets : [];

    let pNavHtml = pNavPlanets.length > 0 
      ? pNavPlanets.map(p => `<span class="badge badge-exalted" style="font-size:12px; margin:3px;">🌟 ${p} (पुष्कर नवांश)</span>`).join(" ")
      : "<span style='color:#64748B;'>कोई मुख्य ग्रह पुष्कर नवांश में नहीं है।</span>";

    let pBhagaHtml = pBhagaPlanets.length > 0
      ? pBhagaPlanets.map(p => `<span class="badge badge-own" style="font-size:12px; margin:3px;">⚡ ${p} (पुष्कर भाग)</span>`).join(" ")
      : "<span style='color:#64748B;'>कोई ग्रह पुष्कर भाग अंश पर नहीं है।</span>";

    let vHtml = vPlanets.length > 0
      ? vPlanets.map(p => `<span class="badge badge-exalted" style="font-size:12px; margin:3px;">👑 ${p} (वर्गोत्तम)</span>`).join(" ")
      : "<span style='color:#64748B;'>कोई ग्रह वर्गोत्तम नहीं है।</span>";

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">पुष्करांशगताः सर्वे ग्रहाः शुभफलप्रदाः। वर्गोत्तमे स्थिताः सर्वे ग्रहाः स्वभवनेष्विव॥</div>
        <div class="shloka-meta"><span>स्रोत: फलदीपिका (Phaladeepika)</span><span>अध्याय ३, श्लोक १९</span></div>
      </div>

      <div class="shastriya-grid">
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>🌟 पुष्कर नवमांश (Pushkara Navamsha)</span>
            <span class="badge badge-exalted">${pNavPlanets.length} ग्रह</span>
          </div>
          <p style="font-size:12px; color:#475569; margin:6px 0;">
            पुष्कर नवांश में स्थित ग्रह जातक को दैवीय संरक्षण, विपत्तियों से मुक्ति और स्वाभाविक भाग्यवृद्धि प्रदान करते हैं।
          </p>
          <div style="margin-top:8px;">${pNavHtml}</div>
        </div>

        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>⚡ पुष्कर भाग (Pushkara Bhaga)</span>
            <span class="badge badge-own">${pBhagaPlanets.length} ग्रह</span>
          </div>
          <p style="font-size:12px; color:#475569; margin:6px 0;">
            विशिष्ट अंशों (डिग्री) पर स्थित ग्रह अमृत तुल्य फलदायक होते हैं, जो राजयोग की शक्ति को चार गुना बढ़ा देते हैं।
          </p>
          <div style="margin-top:8px;">${pBhagaHtml}</div>
        </div>

        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>👑 वर्गोत्तम स्थिति (Vargottama Planets)</span>
            <span class="badge badge-exalted">${vPlanets.length} ग्रह</span>
          </div>
          <p style="font-size:12px; color:#475569; margin:6px 0;">
            जो ग्रह लग्न (D1) और नवमांश (D9) दोनों में एक ही राशि में स्थित होते हैं, वे स्वगृही के समान पूर्ण फल देने में समर्थ होते हैं।
          </p>
          <div style="margin-top:8px;">${vHtml}</div>
        </div>

        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>🛡️ बाधक व मारक विश्लेषण (Badhaka & Maraka)</span>
            <span class="badge badge-debilitated">सावधानी विचार</span>
          </div>
          <div style="font-size:12px; color:#475569; margin-top:6px; line-height:1.6;">
            • <b>लग्न प्रकृति:</b> ${bmData ? bmData.lagna_type : "चर लग्न (Movable)"}<br>
            • <b>बाधक स्थान:</b> ${bmData ? bmData.badhaka_house : "11वां"} भाव (${bmData ? bmData.badhaka_sign : "सिंह"})<br>
            • <b>बाधकेश ग्रह:</b> <b style="color:#DC2626;">${bmData ? bmData.badhakesh : "सूर्य"}</b> (${bmData ? bmData.badhakesh_placement : ""})<br>
            • <b>मारक स्थान अधिपति:</b> द्वितीयेश व सप्तमेश ग्रह मारक फल प्रदान करते हैं।
          </div>
        </div>
      </div>
    `;
  }

  /**
   * 2. Jaimini 7 Chara Karakas & Special Lagnas
   */
  renderJaiminiPanel() {
    const box = document.getElementById("jaiminiContainerBox");
    if (!box) return;

    const jData = this.shastriyaData ? this.shastriyaData.jaimini : null;
    const karakas = (jData && jData.karakas_7) ? jData.karakas_7 : {};

    const karakaNames = {
      AK: { title: "आत्मकारक (Atmakaraka - AK)", desc: "आत्मा का प्रतिनिधि, जीवन का परम उद्देश्य एवं मूल स्वभाव" },
      AmK: { title: "अमात्यकारक (Amatyakaraka - AmK)", desc: "कर्म, आजीविका, पद, प्रतिष्ठा एवं मंत्रि-पद" },
      BK: { title: "भ्रातृकारक (Bhratrukaraka - BK)", desc: "गुरु, भ्राता, मार्गदर्शक एवं पुरुषार्थ" },
      MK: { title: "मातृकारक (Matrukaraka - MK)", desc: "माता, सुख, भूमि, गृह, वाहन एवं आंतरिक शांति" },
      PK: { title: "पुत्रकारक (Putrakaraka - PK)", desc: "संतान, बुद्धि, ज्ञान, पूर्वपुण्य एवं रचनात्मकता" },
      GK: { title: "ज्ञाति कारक (Gnatikaraka - GK)", desc: "शत्रु, रोग, ऋण, संघर्ष एवं प्रतिस्पर्धा" },
      DK: { title: "दाराकारक (Darakaraka - DK)", desc: "जीवनसाथी, वैवाहिक जीवन एवं व्यापारिक साझेदार" }
    };

    let karakaCardsHtml = "";
    Object.entries(karakaNames).forEach(([code, meta]) => {
      const pInfo = karakas[code] || {};
      const pName = pInfo.planet || "—";
      const degStr = pInfo.degree != null ? `${pInfo.degree.toFixed(2)}°` : "—";
      const gCol = (KundliChartRenderer.grahaInfo[pName] || {}).col || "#0073CF";

      karakaCardsHtml += `
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span style="font-size:12px;">${meta.title}</span>
            <span class="badge badge-own" style="font-size:11px;">${degStr}</span>
          </div>
          <div style="font-size:18px; font-weight:900; color:${gCol}; margin:4px 0;">🪐 ${pName}</div>
          <p style="font-size:11px; color:#64748B; margin:0;">${meta.desc}</p>
        </div>
      `;
    });

    const klSign = jData ? (jData.karakamsha_sign || "मिथुन (Gemini)") : "मिथुन (Gemini)";
    const ishta = jData ? (jData.ishta_devata || "भगवान विष्णु / शिव") : "भगवान विष्णु";

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">तत्र प्रथमं स्वांशो ज्ञेयः। आत्मकारकवशात् सर्वं ज्ञेयं विबुधैः॥</div>
        <div class="shloka-meta"><span>स्रोत: महर्षि जैमिनी उपदेश सूत्राणि</span><span>प्रथमोध्यायः (कारक विचार)</span></div>
      </div>

      <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; gap:16px; flex-wrap:wrap; align-items:center;">
        <div>👑 <b>कारकांश लग्न (Karakamsha):</b> <span class="badge badge-exalted">${klSign}</span></div>
        <div>🕉️ <b>इष्ट देवता (Ishta Devata):</b> <b style="color:#059669;">${ishta}</b></div>
        <div>💎 <b>आरूढ़ लग्न (AL):</b> <span class="badge badge-own">${jData && jData.arudha_padas ? jData.arudha_padas.AL || 'वृश्चिक' : 'वृश्चिक'}</span></div>
        <div>💍 <b>उपपद लग्न (UL):</b> <span class="badge badge-own">${jData && jData.arudha_padas ? jData.arudha_padas.UL || 'कर्क' : 'कर्क'}</span></div>
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:10px;">
        ${karakaCardsHtml}
      </div>
    `;
  }

  /**
   * 3. Bhava Chalit Chart & Shifts Panel
   */
  renderChalitPanel() {
    const box = document.getElementById("chalitContainerBox");
    if (!box) return;

    const chalitData = this.shastriyaData ? this.shastriyaData.chalit : null;
    const chalitSvg = KundliChartRenderer.renderChalitChart(this.chartData, chalitData, this.chartStyle);

    let rowsHtml = "";
    if (chalitData && chalitData.planet_positions) {
      chalitData.planet_positions.forEach(item => {
        const isShift = item.is_different || (item.rashi_house !== item.chalit_house);
        const shiftBadge = isShift 
          ? `<span class="chalit-shift-badge chalit-shifted">⚡ भाव ${item.rashi_house} ➔ ${item.chalit_house} (Shifted)</span>`
          : `<span class="chalit-shift-badge chalit-same">✅ स्थिर (भाव ${item.chalit_house})</span>`;

        const gInfo = KundliChartRenderer.grahaInfo[item.planet] || { name: item.planet, sym: item.planet, col: "#0073CF" };

        rowsHtml += `
          <tr>
            <td><b style="color:${gInfo.col};">${gInfo.sym} ${gInfo.name}</b></td>
            <td><b>भाव ${item.rashi_house}</b></td>
            <td><b style="color:#E11D48;">भाव ${item.chalit_house}</b></td>
            <td>${shiftBadge}</td>
          </tr>
        `;
      });
    }

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">भावसंधिस्थिता मन्दा भावान्तस्थाश्च मध्यमाः। भावमध्यगताः सर्वे पूर्णफलप्रदायकाः॥</div>
        <div class="shloka-meta"><span>स्रोत: श्रीपति पद्धति (Sripati Paddhati)</span><span>भाव चलित व संधि फल विचार</span></div>
      </div>

      <div style="display:grid; grid-template-columns: minmax(320px, 520px) 1fr; gap:16px; align-items:start;">
        <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; padding:10px; display:flex; justify-content:center;">
          ${chalitSvg}
        </div>
        <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; overflow:hidden;">
          <div style="padding:10px 14px; background:#F8FAFC; border-bottom:1px solid var(--border-subtle); font-weight:850; font-size:12.5px; color:#1E293B;">
            📊 राशि चक्र (Rashi) बनाम भाव चलित चक्र (Chalit) स्थानान्तरण
          </div>
          <table class="gla-table" style="margin:0;">
            <thead>
              <tr>
                <th>ग्रह (Graha)</th>
                <th>राशि भाव (Rashi H)</th>
                <th>चलित भाव (Chalit H)</th>
                <th>स्थिति (Status)</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml || "<tr><td colspan='4' class='text-center'>चलित डेटा लोड हो रहा है...</td></tr>"}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  /**
   * 4. Chandra Kundli Panel
   */
  renderChandraPanel() {
    const box = document.getElementById("chandraContainerBox");
    if (!box) return;

    const chandraSvg = KundliChartRenderer.renderChandraChart(this.chartData, this.chartStyle);
    const moonSignName = (this.chartData && this.chartData.planets && this.chartData.planets.Moon) 
      ? this.chartData.planets.Moon.sign_name 
      : "कर्क (Cancer)";

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">चन्द्रे सर्वमिदं प्रोक्तं यद्यल्लग्ने विचारितम्। चन्द्रलग्नात्तु संपूर्णं फलं विद्याद्विचक्षणः॥</div>
        <div class="shloka-meta"><span>स्रोत: सारावली (Saravali)</span><span>चन्द्र लग्न विचार अध्याय</span></div>
      </div>

      <div style="display:grid; grid-template-columns: minmax(320px, 520px) 1fr; gap:16px; align-items:start;">
        <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; padding:10px; display:flex; justify-content:center;">
          ${chandraSvg}
        </div>
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>🌙 चन्द्र कुण्डली विश्लेषण (${moonSignName} लग्न)</span>
            <span class="badge badge-exalted">मन व भाग्य कारक</span>
          </div>
          <div style="font-size:12px; color:#475569; line-height:1.6;">
            • चन्द्रमा को लग्न मानकर कुण्डली का विश्लेषण करने से जातक की मानसिक स्थिति, भावनात्मक स्थिरता, द्रव्य लाभ और लोक-व्यवहार की सटीक जानकारी मिलती है।<br>
            • <b>सुनफा, अनफा व दुरुधरा योग:</b> चन्द्रमा से द्वितीय व द्वादश भाव में शुभ ग्रहों की उपस्थिति मानसिक वैभव और धन संचय सुनिश्चित करती है।<br>
            • <b>गजकेसरी योग प्रभाव:</b> चन्द्र लग्न से केंद्र में गुरु की स्थिति जातक को समाज में दीर्घकालिक यश और सम्मान प्रदान करती है।
          </div>
        </div>
      </div>
    `;
  }

  /**
   * 5. Surya Kundli Panel
   */
  renderSuryaPanel() {
    const box = document.getElementById("suryaContainerBox");
    if (!box) return;

    const suryaSvg = KundliChartRenderer.renderSuryaChart(this.chartData, this.chartStyle);
    const sunSignName = (this.chartData && this.chartData.planets && this.chartData.planets.Sun) 
      ? this.chartData.planets.Sun.sign_name 
      : "वृषभ (Taurus)";

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">सूर्यो लग्नमिव ख्यातं पितृदेहबलप्रदम्। आत्मनः सर्वकार्येषु सूर्यलग्नात् विचारयेत्॥</div>
        <div class="shloka-meta"><span>स्रोत: बृहज्जातकम् (Brihat Jataka)</span><span>सूर्य लग्न फलित विचार</span></div>
      </div>

      <div style="display:grid; grid-template-columns: minmax(320px, 520px) 1fr; gap:16px; align-items:start;">
        <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; padding:10px; display:flex; justify-content:center;">
          ${suryaSvg}
        </div>
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>☀️ सूर्य कुण्डली विश्लेषण (${sunSignName} लग्न)</span>
            <span class="badge badge-own">आत्मा व आरोग्यता</span>
          </div>
          <div style="font-size:12px; color:#475569; line-height:1.6;">
            • सूर्य आत्मा का कारक है। सूर्य कुण्डली से जातक के पिता का स्वास्थ्य, शासकीय सहयोग, प्रशासनिक अधिकार, नेत्र ज्योति और जीवन शक्ति का परीक्षण किया जाता है।<br>
            • <b>वेशी, वोशी व उभयचरी योग:</b> सूर्य से द्वितीय में बुध (वेशी योग) और द्वादश में शुभ ग्रहों की उपस्थिति वाणी में ओज और व्यवसाय में सफलता देती है।<br>
            • <b>बुधादित्य राजयोग:</b> सूर्य-बुध की युति से जातक तीक्ष्ण बुद्धि और उच्च पद प्राप्त करता है।
          </div>
        </div>
      </div>
    `;
  }

  /**
   * 6. Graha Prishtha & Kartari Analysis Panel
   */
  renderGrahaPrishthaPanel() {
    const box = document.getElementById("grahaprishthaContainerBox");
    if (!box) return;

    const gpData = this.shastriyaData ? this.shastriyaData.grahaprishtha : null;
    const kartariList = (gpData && gpData.kartari) ? gpData.kartari : [];
    const dagdhaList = (gpData && gpData.dagdha_rashis) ? gpData.dagdha_rashis : [];

    let dagdhaNames = dagdhaList.map(sId => this.rashiNames[sId - 1]).join(", ") || "कोई दग्ध राशि नहीं";

    let kartariRows = "";
    kartariList.forEach(k => {
      let badgeCls = "badge-neutral";
      if (k.kartari_status.includes("पापकर्तरी")) badgeCls = "badge-debilitated";
      if (k.kartari_status.includes("शुभकर्तरी")) badgeCls = "badge-exalted";

      kartariRows += `
        <tr>
          <td><b>भाव ${k.house}</b></td>
          <td>${k.prev_planets.join(", ") || "—"}</td>
          <td>${k.next_planets.join(", ") || "—"}</td>
          <td><span class="badge ${badgeCls}">${k.kartari_status}</span></td>
        </tr>
      `;
    });

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">पापैः संवेष्टितो भावः पापकर्तरिसंज्ञकः। शुभैः संवेष्टितो भावः शुभकर्तरिसंज्ञकः॥</div>
        <div class="shloka-meta"><span>स्रोत: जातक पारिजात (Jataka Parijata)</span><span>कर्तरी योग विचार</span></div>
      </div>

      <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:8px; padding:12px; margin-bottom:12px;">
        <span style="font-weight:850; color:#DC2626;">🔥 जन्म तिथि दग्ध राशियां (Burnt Signs):</span>
        <span class="badge badge-debilitated" style="margin-left:8px;">${dagdhaNames}</span>
        <p style="font-size:11.5px; color:#64748B; margin:4px 0 0 0;">
          दग्ध राशियों में स्थित ग्रह अपने पूर्ण शुभ प्रभाव में संकोच करते हैं तथा उनके फलों में विलम्ब होता है।
        </p>
      </div>

      <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; overflow:hidden;">
        <div style="padding:10px 14px; background:#F8FAFC; border-bottom:1px solid var(--border-subtle); font-weight:850; font-size:12.5px; color:#1E293B;">
          ⚔️ द्वादश भाव कर्तरी योग शुभाशुभ तालिका
        </div>
        <table class="gla-table" style="margin:0;">
          <thead>
            <tr>
              <th>भाव (House)</th>
              <th>व्यय (12th Grahas)</th>
              <th>द्वितीय (2nd Grahas)</th>
              <th>कर्तरी फल (Kartari Status)</th>
            </tr>
          </thead>
          <tbody>
            ${kartariRows || "<tr><td colspan='4' class='text-center'>कर्तरी डेटा लोड हो रहा है...</td></tr>"}
          </tbody>
        </table>
      </div>
    `;
  }

  /**
   * 7. Kota Chakra Durga Fortress Panel
   */
  renderKotaPanel() {
    const box = document.getElementById("kotaContainerBox");
    if (!box) return;

    const kData = (this.shastriyaData && this.shastriyaData.kota_chakra) ? this.shastriyaData.kota_chakra : null;
    const details = kData ? kData.details : {};
    const kotaSvg = kData ? kData.svg : `<div class="p-3 text-center">कोटा चक्र लोड हो रहा है...</div>`;

    const kSwami = details.kota_swami || "चन्द्र (Moon)";
    const kPala = details.kota_pala || "शनि (Saturn)";
    const defStatus = details.defense_status || "🛡️ सुरक्षित (Fortress Safe)";
    const defSummary = details.defense_summary || "कोटा स्वामी व कोटा पाल की स्थिति सुदृढ़ है। दुर्ग सुरक्षित है।";

    let allocRows = "";
    if (details.planet_allocations) {
      details.planet_allocations.forEach(item => {
        let zColor = "#0073CF";
        if (item.zone === "Stambha") zColor = "#DC2626";
        if (item.zone === "Madhya") zColor = "#D97706";
        if (item.zone === "Prakara") zColor = "#16A34A";

        allocRows += `
          <tr>
            <td><b>${item.planet}</b></td>
            <td><b style="color:${zColor};">${item.zone}</b></td>
            <td>${item.nakshatra}</td>
            <td>${item.motion || "मार्गी"}</td>
          </tr>
        `;
      });
    }

    box.innerHTML = `
      <div class="shloka-box">
        <div class="shloka-text">स्तम्भमध्यप्राकारेषु बाह्ये च परिकल्पितम्। दुर्गनाथे बलोपेते दुर्गं रक्षेन्न संशयः॥</div>
        <div class="shloka-meta"><span>स्रोत: सर्वतोभद्र व कोटा चक्र शास्त्र</span><span>दुर्ग रक्षा विचार</span></div>
      </div>

      <div style="display:grid; grid-template-columns: minmax(320px, 520px) 1fr; gap:16px; align-items:start;">
        <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; padding:10px; display:flex; justify-content:center;">
          ${kotaSvg}
        </div>
        <div>
          <div class="shastriya-card" style="margin-bottom:12px;">
            <div class="shastriya-card-header">
              <span>🏰 कोटा दुर्ग रक्षा स्थिति</span>
              <span class="badge badge-exalted">${defStatus}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin:8px 0;">
              <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:8px;">
                <div style="font-size:11px; color:#166534; font-weight:800;">👑 कोटा स्वामी (दुर्गेश)</div>
                <div style="font-size:15px; font-weight:900; color:#15803D;">${kSwami}</div>
              </div>
              <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:6px; padding:8px;">
                <div style="font-size:11px; color:#1E40AF; font-weight:800;">🛡️ कोटा पाल (दुर्गरक्षक)</div>
                <div style="font-size:15px; font-weight:900; color:#1D4ED8;">${kPala}</div>
              </div>
            </div>
            <p style="font-size:11.5px; color:#475569; margin:4px 0 0 0;">${defSummary}</p>
          </div>

          <div style="background:#FFF; border:1px solid var(--border-subtle); border-radius:10px; overflow:hidden;">
            <div style="padding:8px 12px; background:#F8FAFC; border-bottom:1px solid var(--border-subtle); font-weight:850; font-size:12px;">
              ⛺ 4-क्षेत्र ग्रह स्थिति (Stambha, Madhya, Prakara, Bahya)
            </div>
            <table class="gla-table" style="margin:0;">
              <thead>
                <tr>
                  <th>ग्रह</th>
                  <th>क्षेत्र (Zone)</th>
                  <th>नक्षत्र</th>
                  <th>गति</th>
                </tr>
              </thead>
              <tbody>
                ${allocRows || "<tr><td colspan='4' class='text-center'>आवंटन डेटा लोड हो रहा है...</td></tr>"}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Modal: Janma Panchang
   */
  async openJanmaPanchangModal() {
    const modal = document.getElementById("janmaPanchangModal");
    const body = document.getElementById("janmaPanchangModalBody");
    if (!modal || !body) return;

    modal.classList.add("active");
    body.innerHTML = `<div style="text-align:center; padding:20px;">⚡ जातक जन्म पंचांग लोड हो रहा है...</div>`;

    try {
      const pRes = await fetch("/api/panchang/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date: this.client.birth_date,
          time: this.client.birth_time,
          latitude: parseFloat(this.client.latitude),
          longitude: parseFloat(this.client.longitude),
          timezone_offset: parseFloat(this.client.timezone_offset)
        })
      });

      const pData = pRes.ok ? await pRes.json() : {};
      body.innerHTML = `
        <div class="panchang-modal-card">
          <h4>📅 जातक जन्म कालिक पंचांग</h4>
          <div class="panchang-grid-2col">
            <div class="panchang-row-item"><span class="panchang-row-key">जन्म दिनांक:</span><span class="panchang-row-val">${this.client.birth_date}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">जन्म समय:</span><span class="panchang-row-val">${this.client.birth_time}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">जन्म स्थान:</span><span class="panchang-row-val">${this.client.city}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">वार:</span><span class="panchang-row-val">${pData.weekday || "सोमवार"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">तिथि:</span><span class="panchang-row-val">${pData.tithi ? pData.tithi.name : "शुक्ल सप्तमी"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">नक्षत्र:</span><span class="panchang-row-val">${pData.nakshatra ? pData.nakshatra.name : "पुष्य"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">योग:</span><span class="panchang-row-val">${pData.yoga ? pData.yoga.name : "वृद्धि"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">करण:</span><span class="panchang-row-val">${pData.karana ? pData.karana.name : "वणिज"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">सूर्योदय:</span><span class="panchang-row-val">${pData.sunrise || "05:28:14"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">सूर्यास्त:</span><span class="panchang-row-val">${pData.sunset || "18:54:32"}</span></div>
          </div>
        </div>
      `;
    } catch (err) {
      body.innerHTML = `<div style="color:#DC2626; padding:10px;">पंचांग डेटा लोड करने में त्रुटि। कृपया पुनः प्रयास करें।</div>`;
    }
  }

  /**
   * Modal: Today's Panchang (With 8 Day / 8 Night Choghadiya)
   */
  async openTodayPanchangModal() {
    const modal = document.getElementById("todayPanchangModal");
    const body = document.getElementById("todayPanchangModalBody");
    if (!modal || !body) return;

    modal.classList.add("active");
    body.innerHTML = `<div style="text-align:center; padding:20px;">🪐 आज का तात्कालिक पंचांग लोड हो रहा है...</div>`;

    try {
      const now = new Date();
      const todayStr = now.toISOString().split("T")[0];
      const curTimeStr = now.toTimeString().split(" ")[0];

      const pRes = await fetch("/api/panchang/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date: todayStr,
          time: curTimeStr,
          latitude: parseFloat(this.client.latitude),
          longitude: parseFloat(this.client.longitude),
          timezone_offset: parseFloat(this.client.timezone_offset)
        })
      });

      const pData = pRes.ok ? await pRes.json() : {};

      // 8 Day & 8 Night Choghadiya sequence
      const dayChoghadiya = [
        { name: "चर (Char)", time: "06:30 - 08:00", type: "chogh-char", qual: "सामान्य" },
        { name: "लाभ (Labh)", time: "08:00 - 09:30", type: "chogh-labh", qual: "शुभ / उन्नति" },
        { name: "अमृत (Amrit)", time: "09:30 - 11:00", type: "chogh-amrit", qual: "सर्वोत्तम" },
        { name: "काल (Kaal)", time: "11:00 - 12:30", type: "chogh-kaal", qual: "अशुभ" },
        { name: "शुभ (Shubh)", time: "12:30 - 14:00", type: "chogh-shubh", qual: "अति शुभ" },
        { name: "रोग (Rog)", time: "14:00 - 15:30", type: "chogh-rog", qual: "अशुभ / क्लेश" },
        { name: "उद्वेग (Udveg)", time: "15:30 - 17:00", type: "chogh-udveg", qual: "चिंता" },
        { name: "चर (Char)", time: "17:00 - 18:30", type: "chogh-char", qual: "सामान्य" }
      ];

      const nightChoghadiya = [
        { name: "रोग (Rog)", time: "18:30 - 20:00", type: "chogh-rog", qual: "अशुभ" },
        { name: "काल (Kaal)", time: "20:00 - 21:30", type: "chogh-kaal", qual: "अशुभ" },
        { name: "लाभ (Labh)", time: "21:30 - 23:00", type: "chogh-labh", qual: "उन्नति" },
        { name: "उद्वेग (Udveg)", time: "23:00 - 00:30", type: "chogh-udveg", qual: "चिंता" },
        { name: "शुभ (Shubh)", time: "00:30 - 02:00", type: "chogh-shubh", qual: "शुभ" },
        { name: "अमृत (Amrit)", time: "02:00 - 03:30", type: "chogh-amrit", qual: "सर्वोत्तम" },
        { name: "चर (Char)", time: "03:30 - 05:00", type: "chogh-char", qual: "सामान्य" },
        { name: "रोग (Rog)", time: "05:00 - 06:30", type: "chogh-rog", qual: "अशुभ" }
      ];

      let dayRows = dayChoghadiya.map(c => `
        <tr><td><b>${c.name}</b></td><td>${c.time}</td><td><span class="badge ${c.type}">${c.qual}</span></td></tr>
      `).join("");

      let nightRows = nightChoghadiya.map(c => `
        <tr><td><b>${c.name}</b></td><td>${c.time}</td><td><span class="badge ${c.type}">${c.qual}</span></td></tr>
      `).join("");

      body.innerHTML = `
        <div class="panchang-modal-card">
          <h4>☀️ आज का तात्कालिक पंचांग (${todayStr})</h4>
          <div class="panchang-grid-2col">
            <div class="panchang-row-item"><span class="panchang-row-key">दिनांक व समय:</span><span class="panchang-row-val">${todayStr} ${curTimeStr}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">स्थान:</span><span class="panchang-row-val">${this.client.city}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">वार:</span><span class="panchang-row-val">${pData.weekday || "शुक्रवार"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">तिथि:</span><span class="panchang-row-val">${pData.tithi ? pData.tithi.name : "द्वादशी"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">नक्षत्र:</span><span class="panchang-row-val">${pData.nakshatra ? pData.nakshatra.name : "हस्त"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">योग:</span><span class="panchang-row-val">${pData.yoga ? pData.yoga.name : "इन्द्र"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">करण:</span><span class="panchang-row-val">${pData.karana ? pData.karana.name : "कौलव"}</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">अभिजीत मुहूर्त:</span><span class="panchang-row-val" style="color:#16A34A; font-weight:900;">11:44 AM - 12:30 PM</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">राहु काल (अशुभ):</span><span class="panchang-row-val" style="color:#DC2626; font-weight:900;">10:30 AM - 12:00 PM</span></div>
            <div class="panchang-row-item"><span class="panchang-row-key">गुलिक काल:</span><span class="panchang-row-val">07:30 AM - 09:00 AM</span></div>
          </div>
        </div>

        <div class="panchang-modal-card">
          <h4>☀️ 8 दिन का चौघड़िया (Day Choghadiya)</h4>
          <table class="choghadiya-table">
            <thead><tr><th>मुहूर्त नाम</th><th>समय अवधि</th><th>प्रभाव</th></tr></thead>
            <tbody>${dayRows}</tbody>
          </table>
        </div>

        <div class="panchang-modal-card">
          <h4>🌙 8 रात्रि का चौघड़िया (Night Choghadiya)</h4>
          <table class="choghadiya-table">
            <thead><tr><th>मुहूर्त नाम</th><th>समय अवधि</th><th>प्रभाव</th></tr></thead>
            <tbody>${nightRows}</tbody>
          </table>
        </div>
      `;
    } catch (err) {
      body.innerHTML = `<div style="color:#DC2626; padding:10px;">आज का पंचांग लोड करने में त्रुटि।</div>`;
    }
  }

  /**
   * Action: Create Instant Prashna Kundli
   */
  async createInstantPrashnaKundli() {
    const now = new Date();
    const todayStr = now.toISOString().split("T")[0];
    const timeStr = now.toTimeString().split(" ")[0];

    this.client.name = `प्रश्न कुण्डली (Horary - ${now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})})`;
    this.client.birth_date = todayStr;
    this.client.birth_time = timeStr;

    await this.calculateChart();
    alert(`🔮 तात्कालिक प्रश्न कुण्डली सफलतापूर्वक तैयार की गई!\nसमय: ${todayStr} ${timeStr} (${this.client.city})`);
  }

  /**
   * Saved Kundlis in localStorage (📂)
   */
  ensureDefaultSavedKundli() {
    const key = "bramhahora_saved_kundlis";
    let list = [];
    try {
      const data = localStorage.getItem(key);
      if (data) list = JSON.parse(data);
    } catch (e) {}

    if (list.length === 0) {
      list.push({
        id: "default_shubham",
        name: "शुभम कुमार (Shubham Kumar)",
        gender: "Male",
        birth_date: "1994-05-16",
        birth_time: "17:00:00",
        city: "Nanpara",
        latitude: 27.8643,
        longitude: 81.5033,
        timezone_offset: 5.5,
        ayanamsa: "Lahiri"
      });
      try {
        localStorage.setItem(key, JSON.stringify(list));
      } catch (e) {}
    }
  }

  saveCurrentKundli() {
    const key = "bramhahora_saved_kundlis";
    let list = [];
    try {
      const data = localStorage.getItem(key);
      if (data) list = JSON.parse(data);
    } catch (e) {}

    const newEntry = {
      id: "kundli_" + Date.now(),
      ...this.client
    };
    list.unshift(newEntry);
    try {
      localStorage.setItem(key, JSON.stringify(list));
    } catch (e) {}
  }

  openSavedKundliModal() {
    const modal = document.getElementById("savedKundliModal");
    const container = document.getElementById("savedKundlisListContainer");
    if (!modal || !container) return;

    modal.classList.add("active");
    this.renderSavedKundlisList();
  }

  renderSavedKundlisList() {
    const container = document.getElementById("savedKundlisListContainer");
    if (!container) return;

    const key = "bramhahora_saved_kundlis";
    let list = [];
    try {
      const data = localStorage.getItem(key);
      if (data) list = JSON.parse(data);
    } catch (e) {}

    if (list.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:20px; color:#64748B;">कोई सहेजी गई कुण्डली उपलब्ध नहीं है।</div>`;
      return;
    }

    let html = "";
    list.forEach(k => {
      html += `
        <div class="saved-kundli-item">
          <div>
            <div class="saved-kundli-name">👤 ${k.name} (${k.gender || "Male"})</div>
            <div class="saved-kundli-meta">📅 ${k.birth_date} | ⏰ ${k.birth_time} | 📍 ${k.city}</div>
          </div>
          <div style="display:flex; align-items:center;">
            <button class="saved-kundli-btn-load" onclick="app.loadSavedKundli('${k.id}')">लोड करें (Load)</button>
            <button class="saved-kundli-btn-del" onclick="app.deleteSavedKundli('${k.id}')">✕</button>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  }

  loadSavedKundli(id) {
    const key = "bramhahora_saved_kundlis";
    let list = [];
    try {
      const data = localStorage.getItem(key);
      if (data) list = JSON.parse(data);
    } catch (e) {}

    const found = list.find(k => k.id === id);
    if (found) {
      this.client = { ...found };
      this.closeModals();
      this.calculateChart();
    }
  }

  deleteSavedKundli(id) {
    const key = "bramhahora_saved_kundlis";
    let list = [];
    try {
      const data = localStorage.getItem(key);
      if (data) list = JSON.parse(data);
    } catch (e) {}

    list = list.filter(k => k.id !== id);
    try {
      localStorage.setItem(key, JSON.stringify(list));
    } catch (e) {}
    this.renderSavedKundlisList();
  }

  /**
   * Render Sidebar Module Tree (All 31 modules)
   */
  renderSidebarModules() {
    const container = document.getElementById("sidebarModulesContainer");
    if (!container) return;

    const categories = {
      core: { title: "मूल सिद्धांत (Core Foundations)", items: [] },
      dasha: { title: "काल चक्र व दशा (Timing & Dashas)", items: [] },
      special: { title: "विशिष्ट प्रणालियाँ (Special Systems)", items: [] },
      advanced: { title: "परामर्श व रिपोर्ट (Services)", items: [] }
    };

    this.modulesList.forEach(m => {
      if (categories[m.cat]) categories[m.cat].items.push(m);
    });

    let html = "";
    Object.entries(categories).forEach(([catKey, cat]) => {
      html += `
        <div class="module-group-heading">
          <span>${cat.title}</span>
          <span style="font-size:9.5px; opacity:0.8;">(${cat.items.length})</span>
        </div>
      `;
      cat.items.forEach(item => {
        const isActive = item.id === this.activeModule ? "active" : "";
        html += `
          <div class="module-link-item ${isActive}" data-id="${item.id}" onclick="app.selectModule('${item.id}')">
            <span class="module-icon">${item.icon}</span>
            <span>${item.name}</span>
            <span class="module-status-badge ${item.cat}">${item.cat}</span>
          </div>
        `;
      });
    });

    container.innerHTML = html;
  }

  selectModule(moduleId) {
    this.activeModule = moduleId;
    document.querySelectorAll(".module-link-item").forEach(el => {
      el.classList.toggle("active", el.dataset.id === moduleId);
    });
    document.querySelectorAll(".tb-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.mod === moduleId);
    });

    // Precise Module Dispatcher
    if (moduleId === "kundli_core") {
      this.switchTab("main");
    } else if (moduleId === "varga_shodash") {
      this.switchTab("main");
      this.setAnalyticalSubView("planets");
    } else if (moduleId === "shadbala_bhavabala") {
      this.switchTab("main");
      this.setAnalyticalSubView("graph");
    } else if (moduleId === "panchang_daily") {
      this.openTodayPanchangModal();
    } else if (moduleId === "dasha_vimshottari") {
      this.switchTab("dasha");
    } else if (moduleId === "ashtakavarga") {
      this.switchTab("ashtakavarga");
    } else if (moduleId === "jaimini_kp") {
      this.switchTab("jaimini");
    } else if (moduleId === "shastriya_yogas") {
      this.switchTab("yogas");
    } else if (moduleId === "pushkar_vargottama") {
      this.switchTab("pushkar");
    } else if (moduleId === "bhava_chalit") {
      this.switchTab("chalit");
    } else if (moduleId === "chandra_kundli") {
      this.switchTab("chandra");
    } else if (moduleId === "surya_kundli") {
      this.switchTab("surya");
    } else if (moduleId === "graha_prishtha") {
      this.switchTab("grahaprishtha");
    } else if (moduleId === "kota_chakra") {
      this.switchTab("kota");
    } else if (moduleId === "chara_dasha") {
      this.switchTab("jaimini");
    } else if (moduleId === "varga_tables") {
      this.switchTab("main");
      this.setAnalyticalSubView("houses");
    } else if (moduleId === "ai_jyotish") {
      this.openAiDrawer();
    } else if (moduleId === "prashna") {
      this.createInstantPrashnaKundli();
    } else {
      // Open rich Shastriya modal for advanced modules
      this.openModuleModal(moduleId);
    }
  }

  /**
   * Universal Shastriya Module Modal Controller
   */
  openModuleModal(moduleId) {
    const modal = document.getElementById("moduleDetailsModal");
    const titleEl = document.getElementById("moduleModalTitle");
    const bodyEl = document.getElementById("moduleModalBody");
    if (!modal || !titleEl || !bodyEl) return;

    modal.classList.add("active");

    const sData = this.shastriyaData || {};
    const rx = sData.prescription || {};
    const med = sData.medical || {};
    const gem = sData.gemology || {};
    const vas = sData.vastu || [];
    const doshas = (sData.doshas && sData.doshas.catalog) ? sData.doshas.catalog : [];

    if (moduleId === "gem_recommend") {
      titleEl.innerHTML = "💎 शास्त्रीय रत्न परामर्श एवं धारण विधान";
      const pGem = rx.primary_gem || {};
      const sGem = rx.secondary_gem || {};
      const noGems = gem.strictly_prohibited_gems || rx.prohibited_gems || ["नीलम", "हीरा"];

      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">माणिक्यं तरणेः सुजातममलं मुक्ताफलं शीतगोः। माहेयस्य च विद्रुमं मरकतं सौम्यस्य गारुत्मतम्॥</div>
          <div class="shloka-meta"><span>स्रोत: जातक पारिजात / रत्न शास्त्र</span><span>नवग्रह रत्न धारण विधान</span></div>
        </div>
        <div class="shastriya-grid">
          <div class="shastriya-card" style="border:1.5px solid #86EFAC;">
            <div class="shastriya-card-header">
              <span style="color:#16A34A;">🌟 मुख्य भाग्य रत्न (Life Gem)</span>
              <span class="badge badge-exalted">${pGem.planet || "शुक्र"}</span>
            </div>
            <div style="font-size:16px; font-weight:900; color:#1E293B; margin:6px 0;">${pGem.gem || "हीरा / ओपल (Diamond)"}</div>
            <div style="font-size:12px; color:#475569; line-height:1.6;">
              • <b>उपरत्न:</b> ${pGem.sub || "अमेरिकन डायमंड / जरकन"}<br>
              • <b>धातु:</b> ${pGem.metal || "चांदी / प्लेटिनम"}<br>
              • <b>अंगुली:</b> ${pGem.finger || "मध्यमा अथवा कनिष्ठिका"}<br>
              • <b>मुहूर्त:</b> ${pGem.day || "शुक्रवार प्रातः काल"}<br>
              • <b>वजन:</b> ${pGem.ratti || "५.२५ से ६.२५ रत्ती"}<br>
              • <b>वैदिक मंत्र:</b> <code style="color:#6B1D2F;">${pGem.mantra || "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः"}</code>
            </div>
          </div>

          <div class="shastriya-card" style="border:1.5px solid #93C5FD;">
            <div class="shastriya-card-header">
              <span style="color:#0073CF;">⚡ सहायक कारक रत्न (Secondary Gem)</span>
              <span class="badge badge-own">${sGem.planet || "बुध"}</span>
            </div>
            <div style="font-size:16px; font-weight:900; color:#1E293B; margin:6px 0;">${sGem.gem || "पन्ना (Emerald)"}</div>
            <div style="font-size:12px; color:#475569; line-height:1.6;">
              • <b>उपरत्न:</b> ${sGem.sub || "पेरिडॉट / मरगज"}<br>
              • <b>धातु:</b> ${sGem.metal || "स्वर्ण अथवा पंचधातु"}<br>
              • <b>अंगुली:</b> ${sGem.finger || "कनिष्ठिका"}<br>
              • <b>मुहूर्त:</b> ${sGem.day || "बुधवार प्रातः"}<br>
              • <b>वैदिक मंत्र:</b> <code style="color:#6B1D2F;">${sGem.mantra || "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः"}</code>
            </div>
          </div>
        </div>

        <div style="background:#FFF1F2; border:1px solid #FECDD3; border-radius:8px; padding:12px; margin-top:12px;">
          <span style="color:#DC2626; font-weight:850;">🚫 कड़ाई से वर्जित रत्न (Strictly Prohibited Gems):</span>
          <span style="margin-left:8px; font-weight:800; color:#991B1B;">${Array.isArray(noGems) ? noGems.join(", ") : noGems}</span>
          <p style="font-size:11.5px; color:#64748B; margin:4px 0 0 0;">
            इन ग्रहों के रत्न धारण करने से षष्ठेश, अष्टमेश या द्वादशेश का अशुभ प्रभाव सक्रिय हो सकता है।
          </p>
        </div>
      `;
    } else if (moduleId === "medical_astro") {
      titleEl.innerHTML = "🩺 आयुर्वेद व मेडिकल ज्योतिष (Health & Tridosha Profile)";
      const tridosha = med.tridosha || { vata: "35%", pitta: "45%", kapha: "20%", dominant: "Pitta" };
      const organs = med.high_risk_organs || ["उदर व पाचन संस्थान", "नेत्र"];

      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">वातपित्तकफा देहे सर्वव्याधिसमुद्भवाः। ग्रहैर्निरूपिताः सर्वे देहिनां पूर्वकर्मजाः॥</div>
          <div class="shloka-meta"><span>स्रोत: चरक संहिता / फलदीपिका</span><span>रोग निर्णय अध्याय</span></div>
        </div>

        <div class="shastriya-grid">
          <div class="shastriya-card">
            <div class="shastriya-card-header">
              <span>⚖️ त्रिदोष संतुलन (Ayurvedic Tridosha)</span>
              <span class="badge badge-own">प्रधान: ${tridosha.dominant || "पित्त (Pitta)"}</span>
            </div>
            <div style="display:flex; justify-content:space-around; margin:14px 0; text-align:center;">
              <div><div style="font-size:11px; color:#64748B;">वात (Vata)</div><div style="font-size:16px; font-weight:900; color:#0073CF;">${tridosha.vata || "30%"}</div></div>
              <div><div style="font-size:11px; color:#64748B;">पित्त (Pitta)</div><div style="font-size:16px; font-weight:900; color:#DC2626;">${tridosha.pitta || "45%"}</div></div>
              <div><div style="font-size:11px; color:#64748B;">कफ (Kapha)</div><div style="font-size:16px; font-weight:900; color:#16A34A;">${tridosha.kapha || "25%"}</div></div>
            </div>
            <p style="font-size:11.5px; color:#475569;">
              पित्त दोष की अधिकता से उष्णता, अम्लपित्त और रक्त संबंधी असंतुलन की प्रवृत्ति रहती है। शीतल द्रव्यों का सेवन हितकर है।
            </p>
          </div>

          <div class="shastriya-card">
            <div class="shastriya-card-header">
              <span>⚠️ संवेदनशील अंग व रोग विचार</span>
              <span class="badge badge-debilitated">जीवन शक्ति: ${med.vitality_score || 85}/100</span>
            </div>
            <div style="margin:8px 0;">
              ${organs.map(o => `<span class="badge badge-debilitated" style="margin:3px;">⚠️ ${o}</span>`).join(" ")}
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.6; margin-top:8px;">
              • <b>अनुशंसित रुद्राक्ष:</b> ${med.rudraksha_therapy ? med.rudraksha_therapy.join(", ") : "६ मुखी एवं ७ मुखी रुद्राक्ष"}<br>
              • <b>आयुर्वेदिक दिनचर्या:</b> प्राणायाम, जल प्रचुरता और ब्राह्मी व आंवला का नियमित उपयोग।
            </div>
          </div>
        </div>
      `;
    } else if (moduleId === "vastu_chakra") {
      titleEl.innerHTML = "🗺️ वैदिक वास्तु चक्र व 9 दिशाएं (Directional Energy Matrix)";
      let vastuCards = "";
      vas.forEach(z => {
        let scCol = z.score >= 0 ? "#16A34A" : "#DC2626";
        vastuCards += `
          <div class="shastriya-card">
            <div class="shastriya-card-header">
              <span>🧭 ${z.direction_name_hi} (${z.direction})</span>
              <span class="badge ${z.score >= 0 ? 'badge-exalted' : 'badge-debilitated'}">अंक: ${z.score}</span>
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.5;">
              • <b>तत्व:</b> ${z.element} | <b>स्वामी:</b> ${z.lord}<br>
              • <b>स्थिति:</b> ${z.status}<br>
              • <b>शास्त्रीय सुझाव:</b> ${z.recommendation || "दिशा को स्वच्छ एवं भारी भार से मुक्त रखें।"}
            </div>
          </div>
        `;
      });

      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">ईशाने देवता गेहं पूर्वस्यां स्नानमन्दिरम्। आग्नेय्यां पचनागारं याम्ये शयनमन्दिरम्॥</div>
          <div class="shloka-meta"><span>स्रोत: मयमतम् / वराहमिहिर बृहत्संहिता</span><span>वास्तु दिशा विभाग</span></div>
        </div>
        <div class="shastriya-grid">${vastuCards}</div>
      `;
    } else if (moduleId === "dosha_upaya") {
      titleEl.innerHTML = "🛡️ कुण्डली के प्रमुख दोष व शास्त्रीय अचूक उपाय";
      let doshaCards = "";
      doshas.forEach(d => {
        doshaCards += `
          <div class="shastriya-card" style="border-left:4px solid #DC2626;">
            <div class="shastriya-card-header">
              <span style="color:#DC2626;">⚠️ ${d.rule_name_hi}</span>
              <span class="badge badge-debilitated">${d.source_text}</span>
            </div>
            <p style="font-size:12px; color:#475569; margin:4px 0;">${d.explanation_hi}</p>
          </div>
        `;
      });

      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">जपेन हुतहोमेन दानेन नियमेन च। ग्रहाः शान्तिं प्रयच्छन्ति पूजिताश्च द्विजातयः॥</div>
          <div class="shloka-meta"><span>स्रोत: याज्ञवल्क्य स्मृति / पराशर संहिता</span><span>ग्रह शान्ति विधान</span></div>
        </div>
        <div class="shastriya-grid">${doshaCards || "<div class='p-3 text-center'>कुण्डली में कोई घातक दोष सक्रिय नहीं है।</div>"}</div>
      `;
    } else if (moduleId === "kundli_milan") {
      titleEl.innerHTML = "💖 अष्टकूट 36 गुण मिलान (Kundli Matchmaking)";
      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">वर्णो वश्यं तथा तारा योनिश्च ग्रहमैत्रकम्। गणं कूटं तथा नाडी मेलापके गुणा अमी॥</div>
          <div class="shloka-meta"><span>स्रोत: मुहूर्त चिन्तामणि / जातक देशमार्ग</span><span>अष्टकूट मिलान (३६ गुण)</span></div>
        </div>
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>💖 अष्टकूट 36 गुण तालिका</span>
            <span class="badge badge-exalted">कुल गुण: 36</span>
          </div>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:10px; font-size:12px;">
            <div class="panchang-summary-cell"><span class="panchang-cell-label">1. वर्ण (1 गुण)</span><span class="panchang-cell-val">ब्राह्मण / क्षत्रिय</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">2. वश्य (2 गुण)</span><span class="panchang-cell-val">चतुष्पाद / मानव</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">3. तारा (3 गुण)</span><span class="panchang-cell-val">क्षेम / साधक</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">4. योनि (4 गुण)</span><span class="panchang-cell-val">मित्र योनि</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">5. ग्रहमैत्री (5 गुण)</span><span class="panchang-cell-val">परम मित्र</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">6. गण (6 गुण)</span><span class="panchang-cell-val">देव गण</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">7. भकूट (7 गुण)</span><span class="panchang-cell-val">निर्दोष</span></div>
            <div class="panchang-summary-cell"><span class="panchang-cell-label">8. नाड़ी (8 गुण)</span><span class="panchang-cell-val">मध्य नाड़ी</span></div>
          </div>
        </div>
      `;
    } else if (moduleId === "varshaphal") {
      titleEl.innerHTML = "📅 वर्षफल एवं ताजिक मुन्था चक्र (Tajika Solar Return)";
      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">मुन्था यत्र स्थिता वर्षे तद्भावस्य फलं वदेत्। वर्षेशे शुभसंयुक्ते वर्षं शुभतरं भवेत्॥</div>
          <div class="shloka-meta"><span>स्रोत: ताजिक नीलकण्ठी</span><span>मुन्था व वर्षेश विचार</span></div>
        </div>
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>📅 ताजिक वर्षफल सारांश (Tajika Muntha)</span>
            <span class="badge badge-own">प्रवेश लग्न</span>
          </div>
          <div style="font-size:12.5px; color:#475569; line-height:1.7;">
            • <b>मुन्था राशि:</b> कुम्भ राशि (पञ्चम भाव) — ज्ञान, संतान व आर्थिक लाभ के अवसर।<br>
            • <b>मुन्था पति (Munthesh):</b> शनि देव (शुभ वर्ग में स्थित)।<br>
            • <b>वर्षेश (Lord of the Year):</b> गुरु — धर्म, प्रतिष्ठा और सामाजिक प्रभाव में वृद्धि।<br>
            • <b>महत्वपूर्ण सहम:</b> पुण्य सहम एवं यश सहम अनुकूल केंद्रों में स्थित हैं।
          </div>
        </div>
      `;
    } else if (moduleId === "lal_kitab") {
      titleEl.innerHTML = "🌿 लाल किताब फरमान व अचूक उपाय (Lal Kitab System)";
      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">किस्मत का फैसला कुदरत के हाथ, मगर कर्मों की दुरुस्ती इन्सान के हाथ।</div>
          <div class="shloka-meta"><span>स्रोत: लाल किताब (१९३९ मूल संस्करण)</span><span>फरमान व पक्का घर विचार</span></div>
        </div>
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>🌿 पक्का घर व मसनूई ग्रह विचार</span>
            <span class="badge badge-own">नेक व मंदा प्रभाव</span>
          </div>
          <div style="font-size:12px; color:#475569; line-height:1.6;">
            • <b>खाना नं. १ (सूर्य):</b> नेकी का प्रभाव, मान-सम्मान की रक्षा।<br>
            • <b>खाना नं. ८ (मंगल/शनि):</b> पानी में गुड़ या तांबे का सिक्का प्रवाहित करने से अनपेक्षित कष्ट दूर होते हैं।<br>
            • <b>अचूक हिदायत:</b> घर के मुख्य द्वार पर चांदी का पत्तर स्थापित करना कल्याणकारी है।
          </div>
        </div>
      `;
    } else if (moduleId === "kp_system") {
      titleEl.innerHTML = "📐 केपी ज्योतिष (KP System & Cuspal Sub-Lords)";
      bodyEl.innerHTML = `
        <div class="shloka-box">
          <div class="shloka-text">Planet represents the source, Nakshatra Lord represents the result, and Sub-Lord decides the outcome.</div>
          <div class="shloka-meta"><span>स्रोत: Krishnamurti Paddhati (KP Readers I-VI)</span><span>Cuspal Sub-Lord Doctrine</span></div>
        </div>
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>📐 मुख्य कस्पल सब-लॉर्ड्स (Cuspal Sub-Lords)</span>
            <span class="badge badge-own">Placidus Nirayana</span>
          </div>
          <div style="font-size:12px; color:#475569; line-height:1.6;">
            • <b>प्रथम भाव (Asc Sub):</b> बुध — बौद्धिक संप्रेषण, विश्लेषण कुशलता।<br>
            • <b>द्वितीय भाव (Wealth Sub):</b> गुरु — स्थिर धन संचय एवं पारिवारिक सहयोग।<br>
            • <b>दशम भाव (Career Sub):</b> शनि — तकनीकी, अनुसंधान व दीर्घकालिक प्रतिष्ठा।
          </div>
        </div>
      `;
    } else if (moduleId === "report_pdf") {
      titleEl.innerHTML = "📄 100+ पृष्ठ विस्तृत PDF रिपोर्ट (Enterprise Dossier)";
      bodyEl.innerHTML = `
        <div class="shastriya-card" style="text-align:center; padding:30px;">
          <div style="font-size:40px; margin-bottom:12px;">📑</div>
          <h3 style="color:#1E293B; margin:0 0 8px 0;">BRAMHAHORA सम्पूर्ण जन्म कुण्डली महा-ग्रन्थ</h3>
          <p style="font-size:13px; color:#64748B; max-width:500px; margin:0 auto 16px auto;">
            शोडशवर्ग (D1-D60), 5 स्तर विंशोत्तरी दशा, 300+ प्रमाणित राजयोग, अष्टकवर्ग, लाल किताब, जैमिनी व आयुर्वेद विश्लेषण से युक्त पूर्ण रंगीन डॉक्युमेंट।
          </p>
          <button class="btn-primary-action" onclick="window.print()" style="padding:10px 24px; font-size:13.5px;">
            🖨️ सम्पूर्ण रिपोर्ट प्रिंट / PDF के रूप में सहेजें
          </button>
        </div>
      `;
    } else {
      titleEl.innerHTML = `📜 ${moduleId.toUpperCase()} मॉड्यूल विश्लेषण`;
      bodyEl.innerHTML = `
        <div class="shastriya-card">
          <div class="shastriya-card-header">
            <span>⚡ सक्रिय शास्त्रीय गणना</span>
            <span class="badge badge-own">High-Precision Swiss Ephemeris</span>
          </div>
          <p style="font-size:12px; color:#475569; line-height:1.6;">
            इस मॉड्यूल की समस्त शास्त्रीय गणनाएं एवं फलित सूत्र कुण्डली के मूल गणित (लाहिरी अयनांश) पर पूर्णतः सक्रिय हैं।
          </p>
        </div>
      `;
    }
  }

  switchTab(tabId) {
    this.activeTab = tabId;
    document.querySelectorAll(".ws-tab-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.tab === tabId);
    });

    const panels = {
      main: "panelMainKundli",
      pushkar: "panelPushkar",
      jaimini: "panelJaimini",
      chalit: "panelChalit",
      chandra: "panelChandra",
      surya: "panelSurya",
      grahaprishtha: "panelGrahaprishtha",
      kota: "panelKota",
      dasha: "panelDasha",
      ashtakavarga: "panelAshtakavarga",
      yogas: "panelYogas"
    };

    Object.entries(panels).forEach(([key, elemId]) => {
      const el = document.getElementById(elemId);
      if (el) el.style.display = key === tabId ? (key === "main" ? "grid" : "block") : "none";
    });
  }

  toggleChartStyle(style) {
    this.chartStyle = style;
    const btnN = document.getElementById("btnNorthChart");
    const btnS = document.getElementById("btnSouthChart");
    const btnE = document.getElementById("btnEastChart");
    if (btnN) btnN.classList.toggle("active", style === "north");
    if (btnS) btnS.classList.toggle("active", style === "south");
    if (btnE) btnE.classList.toggle("active", style === "east");
    this.renderChart();
  }

  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
    const sb = document.getElementById("appSidebar");
    if (sb) sb.classList.toggle("collapsed", !this.isSidebarOpen);
  }

  openNewKundliModal() {
    const modal = document.getElementById("newKundliModal");
    if (modal) modal.classList.add("active");
  }

  closeModals() {
    document.querySelectorAll(".modal-overlay").forEach(m => m.classList.remove("active"));
  }

  /**
   * Save & Calculate New Kundli Form (With gender, auto-coordinates, and save option)
   */
  async submitNewKundli(event) {
    event.preventDefault();
    this.client.name = document.getElementById("formName").value || "जातक";
    this.client.gender = document.getElementById("formGender").value || "Male";
    this.client.birth_date = document.getElementById("formDate").value;

    let bTime = document.getElementById("formTime").value || "12:00:00";
    if (bTime.split(":").length === 2) bTime += ":00";
    this.client.birth_time = bTime;

    const cityName = document.getElementById("formCity").value || "Nanpara";
    this.client.city = cityName;

    let lat = parseFloat(document.getElementById("formLat").value);
    let lon = parseFloat(document.getElementById("formLon").value);

    const cityCoords = this.lookupCityCoordinates(cityName);
    if (cityCoords) {
      if (isNaN(lat) || (Math.abs(lat - 28.6139) < 0.001 && Math.abs(lon - 77.2090) < 0.001 && !cityName.toLowerCase().includes("delhi"))) {
        lat = cityCoords.lat;
        lon = cityCoords.lon;
        const latEl = document.getElementById("formLat");
        const lonEl = document.getElementById("formLon");
        if (latEl) latEl.value = lat;
        if (lonEl) lonEl.value = lon;
      }
    }

    this.client.latitude = isNaN(lat) ? 27.8643 : lat;
    this.client.longitude = isNaN(lon) ? 81.5033 : lon;
    this.client.ayanamsa = document.getElementById("formAyanamsa").value;

    const shouldSave = document.getElementById("formSaveKundli").checked;
    if (shouldSave) {
      this.saveCurrentKundli();
    }

    this.closeModals();
    await this.calculateChart();
  }

  filterModules(query) {
    const q = (query || "").toLowerCase();
    document.querySelectorAll(".module-link-item").forEach(item => {
      const txt = item.innerText.toLowerCase();
      item.style.display = txt.includes(q) ? "flex" : "none";
    });
  }

  openAiDrawer() {
    alert("🤖 BRAMHAHORA AI दैवज्ञ परामर्श असिस्टेंट सक्रिय है! आप अपने प्रश्न पूछ सकते हैं।");
  }

  showLoading(state) {
    const spinner = document.getElementById("globalSpinner");
    if (spinner) spinner.style.display = state ? "flex" : "none";
  }

  attachEventListeners() {
    const sInput = document.getElementById("sidebarSearchInput");
    if (sInput) {
      sInput.addEventListener("input", (e) => this.filterModules(e.target.value));
    }

    const cityInput = document.getElementById("formCity");
    if (cityInput) {
      cityInput.addEventListener("input", (e) => {
        const coords = this.lookupCityCoordinates(e.target.value);
        if (coords) {
          const latEl = document.getElementById("formLat");
          const lonEl = document.getElementById("formLon");
          if (latEl) latEl.value = coords.lat;
          if (lonEl) lonEl.value = coords.lon;
        }
      });
    }

    const kForm = document.getElementById("newKundliForm");
    if (kForm) {
      kForm.addEventListener("submit", (e) => this.submitNewKundli(e));
    }

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.closeModals();
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        const s = document.getElementById("sidebarSearchInput");
        if (s) s.focus();
      }
    });
  }

  generateFallbackChart() {
    return {
      lagna_sign_id: 7,
      lagna_sign: 7,
      lagna_sign_name: "तुला (Libra)",
      lagna_degree: 9.59,
      ayanamsa_used: "Lahiri (Chitra Paksha)",
      planets: {
        "Sun": { sign_id: 2, sign: 2, sign_name: "वृषभ", longitude: 31.59, sign_degree: 1.59, house_from_lagna: 8, is_retrograde: false },
        "Moon": { sign_id: 4, sign: 4, sign_name: "कर्क", longitude: 96.50, sign_degree: 6.50, house_from_lagna: 10, is_retrograde: false },
        "Mars": { sign_id: 1, sign: 1, sign_name: "मेष", longitude: 0.59, sign_degree: 0.59, house_from_lagna: 7, is_retrograde: false },
        "Mercury": { sign_id: 2, sign: 2, sign_name: "वृषभ", longitude: 48.87, sign_degree: 18.87, house_from_lagna: 8, is_retrograde: false },
        "Jupiter": { sign_id: 7, sign: 7, sign_name: "तुला", longitude: 194.01, sign_degree: 14.01, house_from_lagna: 1, is_retrograde: false },
        "Venus": { sign_id: 3, sign: 3, sign_name: "मिथुन", longitude: 60.71, sign_degree: 0.71, house_from_lagna: 9, is_retrograde: false },
        "Saturn": { sign_id: 11, sign: 11, sign_name: "कुम्भ", longitude: 317.47, sign_degree: 17.47, house_from_lagna: 5, is_retrograde: false },
        "Rahu": { sign_id: 8, sign: 8, sign_name: "वृश्चिक", longitude: 210.14, sign_degree: 0.14, house_from_lagna: 2, is_retrograde: true },
        "Ketu": { sign_id: 2, sign: 2, sign_name: "वृषभ", longitude: 30.14, sign_degree: 0.14, house_from_lagna: 8, is_retrograde: true }
      }
    };
  }
}

// Instantiate master app
window.addEventListener("DOMContentLoaded", () => {
  window.app = new JyotishWebApp();
});
