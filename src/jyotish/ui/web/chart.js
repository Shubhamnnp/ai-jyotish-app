/**
 * BRAMHAHORA - Vedic Kundali Vector SVG Chart Engine
 * Renders high-precision, classical North, South & East Indian Kundali Charts
 * Styled with traditional Dark Maroon & Charcoal Shastriya borders
 */

const KundliChartRenderer = {
  // Planetary symbols & colors
  grahaInfo: {
    "Sun": { name: "सूर्य", sym: "☉ Su", col: "#991B1B" },
    "Moon": { name: "चन्द्र", sym: "☽ Mo", col: "#1E40AF" },
    "Mars": { name: "मंगल", sym: "♂ Ma", col: "#B91C1C" },
    "Mercury": { name: "बुध", sym: "☿ Me", col: "#047857" },
    "Jupiter": { name: "गुरु", sym: "♃ Ju", col: "#B45309" },
    "Venus": { name: "शुक्र", sym: "♀ Ve", col: "#BE185D" },
    "Saturn": { name: "शनि", sym: "♄ Sa", col: "#334155" },
    "Rahu": { name: "राहु", sym: "☊ Ra", col: "#6D28D9" },
    "Ketu": { name: "केतु", sym: "☋ Ke", col: "#92400E" },
    "Uranus": { name: "हर्षल", sym: "♅ Ur", col: "#0369A1" },
    "Neptune": { name: "नेपच्यून", sym: "♆ Ne", col: "#0369A1" },
    "Pluto": { name: "प्लूटो", sym: "♇ Pl", col: "#0369A1" }
  },

  rashiNames: ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"],

  /**
   * Universal Chart Dispatcher
   */
  renderChart(chartData, style = "north", vargaKey = "D1") {
    if (!chartData) return `<div class="p-4 text-center">कुण्डली डेटा लोड हो रहा है...</div>`;
    if (style === "south") {
      return this.renderSouthIndian(chartData, vargaKey);
    } else if (style === "east") {
      return this.renderEastIndian(chartData, vargaKey);
    }
    return this.renderNorthIndian(chartData, vargaKey);
  },

  /**
   * Render North Indian Diamond Chart SVG (Dark Maroon Shastriya Aesthetics)
   */
  renderNorthIndian(chartData, vargaKey = "D1") {
    const size = 520;
    const mid = size / 2;
    
    // Determine lagna sign
    let lagnaSign = 1;
    if (vargaKey === "D1") {
      lagnaSign = chartData.lagna_sign_id || chartData.lagna_sign || 1;
    } else if (chartData.vargas && chartData.vargas[vargaKey]) {
      lagnaSign = chartData.vargas[vargaKey].lagna_sign_id || chartData.vargas[vargaKey].lagna_sign || 1;
    }

    // Organize planets by house
    const housePlanets = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[] };
    
    const planetsSource = (vargaKey === "D1") 
      ? chartData.planets 
      : (chartData.vargas && chartData.vargas[vargaKey] ? chartData.vargas[vargaKey].planets : chartData.planets);

    if (planetsSource) {
      Object.entries(planetsSource).forEach(([pName, pObj]) => {
        let pSign = pObj.sign_id || pObj.sign || 1;
        let hNum = pObj.house_from_lagna || pObj.house_number || (((pSign - lagnaSign + 12) % 12) + 1);
        let degVal = pObj.sign_degree != null 
          ? pObj.sign_degree 
          : (pObj.degree_in_varga != null 
            ? pObj.degree_in_varga 
            : (pObj.longitude_in_sign != null ? pObj.longitude_in_sign : (pObj.longitude ? pObj.longitude % 30 : null)));

        if (housePlanets[hNum]) {
          housePlanets[hNum].push({
            name: pName,
            is_retro: pObj.is_retrograde || false,
            deg: degVal != null ? degVal.toFixed(1) : ""
          });
        }
      });
    }

    // Exact house centers & sign label positions
    const houseCoords = {
      1:  { rashiPos: { x: mid, y: mid - 32 },  plPos: { x: mid, y: mid - 75 } },
      2:  { rashiPos: { x: mid - 75, y: 75 },   plPos: { x: mid - 85, y: 45 } },
      3:  { rashiPos: { x: 75, y: mid - 75 },   plPos: { x: 45, y: mid - 85 } },
      4:  { rashiPos: { x: mid - 32, y: mid },  plPos: { x: mid - 75, y: mid } },
      5:  { rashiPos: { x: 75, y: mid + 75 },   plPos: { x: 45, y: mid + 85 } },
      6:  { rashiPos: { x: mid - 75, y: size - 75 }, plPos: { x: mid - 85, y: size - 45 } },
      7:  { rashiPos: { x: mid, y: mid + 32 },  plPos: { x: mid, y: mid + 75 } },
      8:  { rashiPos: { x: mid + 75, y: size - 75 }, plPos: { x: mid + 85, y: size - 45 } },
      9:  { rashiPos: { x: size - 75, y: mid + 75 }, plPos: { x: size - 45, y: mid + 85 } },
      10: { rashiPos: { x: mid + 32, y: mid },  plPos: { x: mid + 75, y: mid } },
      11: { rashiPos: { x: size - 75, y: mid - 75 }, plPos: { x: size - 45, y: mid - 85 } },
      12: { rashiPos: { x: mid + 75, y: 75 },   plPos: { x: mid + 85, y: 45 } }
    };

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="svg-kundli" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="kundliParchment" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#FFFFFF" />
          <stop offset="100%" stop-color="#FFFBEB" />
        </radialGradient>
      </defs>

      <!-- Outer Boundary Rectangle (Dark Maroon #6B1D2F) -->
      <rect x="5" y="5" width="${size - 10}" height="${size - 10}" fill="url(#kundliParchment)" stroke="#6B1D2F" stroke-width="3" rx="8" />

      <!-- Inner Geometry Lines (Dark Maroon #800000) -->
      <g stroke="#800000" stroke-width="2.2" stroke-linecap="round">
        <!-- Outer Diamond -->
        <line x1="${mid}" y1="5" x2="${size - 5}" y2="${mid}" />
        <line x1="${size - 5}" y1="${mid}" x2="${mid}" y2="${size - 5}" />
        <line x1="${mid}" y1="${size - 5}" x2="5" y2="${mid}" />
        <line x1="5" y1="${mid}" x2="${mid}" y2="5" />

        <!-- Diagonal Crossed Lines -->
        <line x1="5" y1="5" x2="${size - 5}" y2="${size - 5}" />
        <line x1="${size - 5}" y1="5" x2="5" y2="${size - 5}" />
      </g>`;

    // Render Sign Numbers and Planets for each house
    for (let h = 1; h <= 12; h++) {
      let rashiNum = ((lagnaSign + h - 2) % 12) + 1;
      let pos = houseCoords[h];

      // Sign number (Bold dark maroon)
      svg += `<text x="${pos.rashiPos.x}" y="${pos.rashiPos.y}" text-anchor="middle" dominant-baseline="central" fill="#6B1D2F" font-weight="900" font-size="14" font-family="'Segoe UI', Roboto, sans-serif">${rashiNum}</text>`;

      // Planets in house
      let planets = housePlanets[h] || [];
      if (planets.length > 0) {
        let startY = pos.plPos.y - ((planets.length - 1) * 8);
        planets.forEach((p, idx) => {
          let gInfo = this.grahaInfo[p.name] || { sym: p.name.substring(0,2), col: "#1E293B" };
          let retLabel = p.is_retro ? "<tspan fill='#DC2626' font-weight='900'> (R)</tspan>" : "";
          let degLabel = p.deg ? `<tspan fill='#64748B' font-size='9.5'> ${p.deg}°</tspan>` : "";
          let curY = startY + (idx * 16);
          svg += `<text x="${pos.plPos.x}" y="${curY}" text-anchor="middle" dominant-baseline="central" fill="${gInfo.col}" font-weight="850" font-size="12" font-family="'Segoe UI', Roboto, sans-serif">${gInfo.sym}${retLabel}${degLabel}</text>`;
        });
      }
    }

    // Chart Center Watermark / Label
    svg += `<g opacity="0.12">
      <text x="${mid}" y="${mid}" text-anchor="middle" dominant-baseline="central" fill="#6B1D2F" font-size="30" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">${vargaKey}</text>
    </g>`;

    svg += `</svg>`;
    return svg;
  },

  /**
   * Render South Indian Square Chart SVG (Dark Maroon Shastriya Grid)
   */
  renderSouthIndian(chartData, vargaKey = "D1") {
    const size = 520;
    const box = size / 4;
    
    const signBoxes = {
      12: { r: 0, c: 0 }, 1: { r: 0, c: 1 }, 2: { r: 0, c: 2 }, 3: { r: 0, c: 3 },
      11: { r: 1, c: 0 }, 4: { r: 1, c: 3 },
      10: { r: 2, c: 0 }, 5: { r: 2, c: 3 },
      9: { r: 3, c: 0 }, 8: { r: 3, c: 1 }, 7: { r: 3, c: 2 }, 6: { r: 3, c: 3 }
    };

    let lagnaSign = (vargaKey === "D1") 
      ? (chartData.lagna_sign_id || chartData.lagna_sign || 1)
      : (chartData.vargas && chartData.vargas[vargaKey] ? (chartData.vargas[vargaKey].lagna_sign_id || chartData.vargas[vargaKey].lagna_sign || 1) : 1);

    const planetsSource = (vargaKey === "D1") 
      ? chartData.planets 
      : (chartData.vargas && chartData.vargas[vargaKey] ? chartData.vargas[vargaKey].planets : chartData.planets);

    const signPlanets = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[] };
    if (planetsSource) {
      Object.entries(planetsSource).forEach(([pName, pObj]) => {
        let pSign = pObj.sign_id || pObj.sign || 1;
        let degVal = pObj.sign_degree != null 
          ? pObj.sign_degree 
          : (pObj.degree_in_varga != null 
            ? pObj.degree_in_varga 
            : (pObj.longitude_in_sign != null ? pObj.longitude_in_sign : (pObj.longitude ? pObj.longitude % 30 : null)));

        if (signPlanets[pSign]) {
          signPlanets[pSign].push({
            name: pName,
            is_retro: pObj.is_retrograde || false,
            deg: degVal != null ? degVal.toFixed(1) : ""
          });
        }
      });
    }

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="svg-kundli" xmlns="http://www.w3.org/2000/svg">
      <!-- Background & Outer Boundary -->
      <rect x="5" y="5" width="${size - 10}" height="${size - 10}" fill="#FFFDF8" stroke="#6B1D2F" stroke-width="3" rx="8" />

      <!-- South Indian 4x4 Grid Lines (Dark Maroon #800000) -->
      <g stroke="#800000" stroke-width="2.2" stroke-linecap="round">
        <line x1="${box}" y1="5" x2="${box}" y2="${size - 5}" />
        <line x1="${box * 2}" y1="5" x2="${box * 2}" y2="${box}" />
        <line x1="${box * 2}" y1="${box * 3}" x2="${box * 2}" y2="${size - 5}" />
        <line x1="${box * 3}" y1="5" x2="${box * 3}" y2="${size - 5}" />

        <line x1="5" y1="${box}" x2="${size - 5}" y2="${box}" />
        <line x1="5" y1="${box * 2}" x2="${box}" y2="${box * 2}" />
        <line x1="${box * 3}" y1="${box * 2}" x2="${size - 5}" y2="${box * 2}" />
        <line x1="5" y1="${box * 3}" x2="${size - 5}" y2="${box * 3}" />
      </g>`;

    // Center Box Watermark
    svg += `<g opacity="0.14">
      <text x="${size / 2}" y="${size / 2}" text-anchor="middle" dominant-baseline="central" fill="#6B1D2F" font-size="26" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">${vargaKey} South Indian</text>
    </g>`;

    // Populate each sign box
    for (let s = 1; s <= 12; s++) {
      let b = signBoxes[s];
      let bx = b.c * box;
      let by = b.r * box;

      let isLagna = (s === lagnaSign);
      if (isLagna) {
        // Red Lagna diagonal slash
        svg += `<line x1="${bx + 5}" y1="${by + 5}" x2="${bx + box - 5}" y2="${by + box - 5}" stroke="#DC2626" stroke-width="2" stroke-dasharray="4,3" />`;
        svg += `<text x="${bx + 10}" y="${by + 18}" fill="#DC2626" font-weight="900" font-size="12">लग्न (Asc)</text>`;
      }

      // Rashi label
      svg += `<text x="${bx + box - 8}" y="${by + 16}" text-anchor="end" fill="#6B1D2F" font-size="11" font-weight="800">${this.rashiNames[s - 1]}</text>`;

      // Planets
      let pls = signPlanets[s] || [];
      pls.forEach((p, idx) => {
        let gInfo = this.grahaInfo[p.name] || { sym: p.name.substring(0,2), col: "#1E293B" };
        let curY = by + 34 + (idx * 16);
        let retLabel = p.is_retro ? "<tspan fill='#DC2626'> (R)</tspan>" : "";
        let degLabel = p.deg ? `<tspan fill='#64748B' font-size='9.5'> ${p.deg}°</tspan>` : "";
        svg += `<text x="${bx + 12}" y="${curY}" fill="${gInfo.col}" font-weight="850" font-size="11.5">${gInfo.sym}${retLabel}${degLabel}</text>`;
      });
    }

    svg += `</svg>`;
    return svg;
  },

  /**
   * Render East Indian (Bangla/Assam/Odisha) Chart SVG (Dark Maroon Shastriya Aesthetic)
   */
  renderEastIndian(chartData, vargaKey = "D1") {
    const size = 520;
    const mid = size / 2;

    let lagnaSign = (vargaKey === "D1") 
      ? (chartData.lagna_sign_id || chartData.lagna_sign || 1)
      : (chartData.vargas && chartData.vargas[vargaKey] ? (chartData.vargas[vargaKey].lagna_sign_id || chartData.vargas[vargaKey].lagna_sign || 1) : 1);

    const planetsSource = (vargaKey === "D1") 
      ? chartData.planets 
      : (chartData.vargas && chartData.vargas[vargaKey] ? chartData.vargas[vargaKey].planets : chartData.planets);

    const signPlanets = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[] };
    if (planetsSource) {
      Object.entries(planetsSource).forEach(([pName, pObj]) => {
        let pSign = pObj.sign_id || pObj.sign || 1;
        let degVal = pObj.sign_degree != null 
          ? pObj.sign_degree 
          : (pObj.degree_in_varga != null 
            ? pObj.degree_in_varga 
            : (pObj.longitude_in_sign != null ? pObj.longitude_in_sign : (pObj.longitude ? pObj.longitude % 30 : null)));

        if (signPlanets[pSign]) {
          signPlanets[pSign].push({
            name: pName,
            is_retro: pObj.is_retrograde || false,
            deg: degVal != null ? degVal.toFixed(1) : ""
          });
        }
      });
    }

    // East Indian Sign Coordinates (Signs 1-12 fixed)
    const eastSignCoords = {
      1:  { rashiPos: { x: mid, y: 120 }, plPos: { x: mid, y: 70 } },
      2:  { rashiPos: { x: 130, y: 40 }, plPos: { x: 130, y: 75 } },
      3:  { rashiPos: { x: 40, y: 130 }, plPos: { x: 75, y: 130 } },
      4:  { rashiPos: { x: 120, y: mid }, plPos: { x: 70, y: mid } },
      5:  { rashiPos: { x: 40, y: 390 }, plPos: { x: 75, y: 390 } },
      6:  { rashiPos: { x: 130, y: 480 }, plPos: { x: 130, y: 445 } },
      7:  { rashiPos: { x: mid, y: 400 }, plPos: { x: mid, y: 450 } },
      8:  { rashiPos: { x: 390, y: 480 }, plPos: { x: 390, y: 445 } },
      9:  { rashiPos: { x: 480, y: 390 }, plPos: { x: 445, y: 390 } },
      10: { rashiPos: { x: 400, y: mid }, plPos: { x: 450, y: mid } },
      11: { rashiPos: { x: 480, y: 130 }, plPos: { x: 445, y: 130 } },
      12: { rashiPos: { x: 390, y: 40 }, plPos: { x: 390, y: 75 } }
    };

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="svg-kundli" xmlns="http://www.w3.org/2000/svg">
      <!-- Background & Outer Box (Dark Maroon) -->
      <rect x="5" y="5" width="${size - 10}" height="${size - 10}" fill="#FFFDF8" stroke="#6B1D2F" stroke-width="3" rx="8" />

      <!-- Inner Geometry Lines (East Indian) -->
      <g stroke="#800000" stroke-width="2.2" stroke-linecap="round">
        <!-- Outer Diamond -->
        <line x1="${mid}" y1="5" x2="${size - 5}" y2="${mid}" />
        <line x1="${size - 5}" y1="${mid}" x2="${mid}" y2="${size - 5}" />
        <line x1="${mid}" y1="${size - 5}" x2="5" y2="${mid}" />
        <line x1="5" y1="${mid}" x2="${mid}" y2="5" />

        <!-- Diagonal Crossed Lines -->
        <line x1="5" y1="5" x2="${size - 5}" y2="${size - 5}" />
        <line x1="${size - 5}" y1="5" x2="5" y2="${size - 5}" />
      </g>`;

    // Watermark
    svg += `<g opacity="0.14">
      <text x="${mid}" y="${mid}" text-anchor="middle" dominant-baseline="central" fill="#6B1D2F" font-size="26" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">${vargaKey} East Indian</text>
    </g>`;

    // Render 12 Fixed Signs & Lagna
    for (let s = 1; s <= 12; s++) {
      let pos = eastSignCoords[s];
      let isLagna = (s === lagnaSign);

      let rashiColor = isLagna ? "#DC2626" : "#6B1D2F";
      let rashiText = `${s} ${this.rashiNames[s - 1]}`;
      if (isLagna) {
        rashiText += " (लग्न)";
      }
      svg += `<text x="${pos.rashiPos.x}" y="${pos.rashiPos.y}" text-anchor="middle" dominant-baseline="central" fill="${rashiColor}" font-weight="${isLagna ? 900 : 800}" font-size="${isLagna ? 12 : 11}" font-family="'Segoe UI', Roboto, sans-serif">${rashiText}</text>`;

      // Planets in sign
      let pls = signPlanets[s] || [];
      if (pls.length > 0) {
        let startY = pos.plPos.y - ((pls.length - 1) * 8);
        pls.forEach((p, idx) => {
          let gInfo = this.grahaInfo[p.name] || { sym: p.name.substring(0,2), col: "#1E293B" };
          let curY = startY + (idx * 16);
          let retLabel = p.is_retro ? "<tspan fill='#DC2626'> (R)</tspan>" : "";
          let degStr = p.deg ? `<tspan font-size="9.5" fill="#64748B"> ${p.deg}°</tspan>` : "";
          svg += `<text x="${pos.plPos.x}" y="${curY}" text-anchor="middle" dominant-baseline="central" fill="${gInfo.col}" font-weight="850" font-size="11.5" font-family="'Segoe UI', Roboto, sans-serif">${gInfo.sym}${retLabel}${degStr}</text>`;
        });
      }
    }

    svg += `</svg>`;
    return svg;
  },

  /**
   * Render Chandra Kundali (Moon as Ascendant)
   */
  renderChandraChart(chartData, style = "north") {
    if (!chartData || !chartData.planets || !chartData.planets.Moon) {
      return `<div class="p-3 text-center">चन्द्र कुण्डली डेटा उपलब्ध नहीं है</div>`;
    }
    const moonSign = chartData.planets.Moon.sign_id || 1;
    const chandraData = {
      lagna_sign_id: moonSign,
      lagna_sign: moonSign,
      lagna_sign_name: chartData.planets.Moon.sign_name || "Moon Sign",
      planets: chartData.planets
    };
    return this.renderChart(chandraData, style, "CHANDRA");
  },

  /**
   * Render Surya Kundali (Sun as Ascendant)
   */
  renderSuryaChart(chartData, style = "north") {
    if (!chartData || !chartData.planets || !chartData.planets.Sun) {
      return `<div class="p-3 text-center">सूर्य कुण्डली डेटा उपलब्ध नहीं है</div>`;
    }
    const sunSign = chartData.planets.Sun.sign_id || 1;
    const suryaData = {
      lagna_sign_id: sunSign,
      lagna_sign: sunSign,
      lagna_sign_name: chartData.planets.Sun.sign_name || "Sun Sign",
      planets: chartData.planets
    };
    return this.renderChart(suryaData, style, "SURYA");
  },

  /**
   * Render Bhava Chalit Chart (Cusp Positions)
   */
  renderChalitChart(chartData, chalitData, style = "north") {
    if (!chartData) return `<div class="p-3 text-center">चलित कुण्डली डेटा लोड हो रहा है...</div>`;
    const lagnaSign = chartData.lagna_sign_id || chartData.lagna_sign || 1;
    
    // Map chalit houses
    const chalitPlanets = {};
    if (chalitData && chalitData.planet_positions) {
      chalitData.planet_positions.forEach(item => {
        const pName = item.planet;
        const chalitHouse = item.chalit_house || 1;
        const mappedSign = ((lagnaSign + chalitHouse - 2) % 12) + 1;
        chalitPlanets[pName] = {
          name: pName,
          sign_id: mappedSign,
          sign: mappedSign,
          house_from_lagna: chalitHouse,
          house_number: chalitHouse,
          is_retrograde: item.is_retrograde || (chartData.planets && chartData.planets[pName] ? chartData.planets[pName].is_retrograde : false),
          sign_degree: item.chalit_degree || (chartData.planets && chartData.planets[pName] ? chartData.planets[pName].sign_degree : 0)
        };
      });
    }

    const customChart = {
      lagna_sign_id: lagnaSign,
      lagna_sign: lagnaSign,
      lagna_sign_name: chartData.lagna_sign_name,
      planets: Object.keys(chalitPlanets).length > 0 ? chalitPlanets : chartData.planets
    };
    return this.renderChart(customChart, style, "CHALIT");
  }
};

window.KundliChartRenderer = KundliChartRenderer;
