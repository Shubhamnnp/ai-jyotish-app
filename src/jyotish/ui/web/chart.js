/**
 * JyotishOS - Vedic Kundali Vector SVG Chart Engine
 * Renders high-precision, responsive North & South Indian Kundali Charts
 */

const KundliChartRenderer = {
  // Planetary symbols & colors
  grahaInfo: {
    "Sun": { name: "सूर्य", sym: "☉ Su", col: "#E11D48" },
    "Moon": { name: "चन्द्र", sym: "☽ Mo", col: "#2563EB" },
    "Mars": { name: "मंगल", sym: "♂ Ma", col: "#DC2626" },
    "Mercury": { name: "बुध", sym: "☿ Me", col: "#059669" },
    "Jupiter": { name: "गुरु", sym: "♃ Ju", col: "#D97706" },
    "Venus": { name: "शुक्र", sym: "♀ Ve", col: "#DB2777" },
    "Saturn": { name: "शनि", sym: "♄ Sa", col: "#475569" },
    "Rahu": { name: "राहु", sym: "☊ Ra", col: "#7C3AED" },
    "Ketu": { name: "केतु", sym: "☋ Ke", col: "#B45309" },
    "Uranus": { name: "हर्षल", sym: "♅ Ur", col: "#0284C7" },
    "Neptune": { name: "नेपच्यून", sym: "♆ Ne", col: "#0284C7" },
    "Pluto": { name: "प्लूटो", sym: "♇ Pl", col: "#0284C7" }
  },

  rashiNames: ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"],

  /**
   * Render North Indian Diamond Chart SVG
   * @param {Object} chartData - Complete natal chart object from /api/chart/calculate
   * @param {String} vargaKey - e.g. "D1", "D9", "D10"
   */
  renderNorthIndian(chartData, vargaKey = "D1") {
    const size = 500;
    const mid = size / 2;
    
    // Determine lagna sign
    let lagnaSign = 1;
    if (vargaKey === "D1" && chartData.lagna_sign) {
      lagnaSign = chartData.lagna_sign;
    } else if (chartData.vargas && chartData.vargas[vargaKey] && chartData.vargas[vargaKey].lagna_sign) {
      lagnaSign = chartData.vargas[vargaKey].lagna_sign;
    }

    // Organize planets by house
    const housePlanets = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[] };
    
    const planetsSource = (vargaKey === "D1") ? chartData.planets : (chartData.vargas && chartData.vargas[vargaKey] ? chartData.vargas[vargaKey].planets : chartData.planets);

    if (planetsSource) {
      Object.entries(planetsSource).forEach(([pName, pObj]) => {
        let pSign = pObj.sign || 1;
        // House = ((pSign - lagnaSign + 12) % 12) + 1
        let hNum = ((pSign - lagnaSign + 12) % 12) + 1;
        if (housePlanets[hNum]) {
          housePlanets[hNum].push({
            name: pName,
            is_retro: pObj.is_retrograde || false,
            deg: pObj.longitude_in_sign ? pObj.longitude_in_sign.toFixed(1) : ""
          });
        }
      });
    }

    // House diamond polygon definitions
    const houseCoords = {
      1: { rashiPos: { x: mid, y: mid - 35 }, plPos: { x: mid, y: mid - 65 } },
      2: { rashiPos: { x: mid - 85, y: 70 }, plPos: { x: mid - 85, y: 40 } },
      3: { rashiPos: { x: 70, y: mid - 85 }, plPos: { x: 40, y: mid - 85 } },
      4: { rashiPos: { x: mid - 35, y: mid }, plPos: { x: mid - 65, y: mid } },
      5: { rashiPos: { x: 70, y: mid + 85 }, plPos: { x: 40, y: mid + 85 } },
      6: { rashiPos: { x: mid - 85, y: size - 70 }, plPos: { x: mid - 85, y: size - 40 } },
      7: { rashiPos: { x: mid, y: mid + 35 }, plPos: { x: mid, y: mid + 65 } },
      8: { rashiPos: { x: mid + 85, y: size - 70 }, plPos: { x: mid + 85, y: size - 40 } },
      9: { rashiPos: { x: size - 70, y: mid + 85 }, plPos: { x: size - 40, y: mid + 85 } },
      10: { rashiPos: { x: mid + 35, y: mid }, plPos: { x: mid + 65, y: mid } },
      11: { rashiPos: { x: size - 70, y: mid - 85 }, plPos: { x: size - 40, y: mid - 85 } },
      12: { rashiPos: { x: mid + 85, y: 70 }, plPos: { x: mid + 85, y: 40 } }
    };

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="svg-kundli" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="kundliGoldGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#FFFFFF" />
          <stop offset="100%" stop-color="#F8FAFC" />
        </radialGradient>
        <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
          <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#0073CF" flood-opacity="0.15"/>
        </filter>
      </defs>

      <!-- Background Square -->
      <rect x="4" y="4" width="${size - 8}" height="${size - 8}" fill="url(#kundliGoldGrad)" stroke="#0073CF" stroke-width="2.5" rx="10" />

      <!-- Inner Geometry Lines -->
      <g stroke="#00B0F0" stroke-width="2">
        <!-- Outer Diamond -->
        <line x1="${mid}" y1="4" x2="${size - 4}" y2="${mid}" />
        <line x1="${size - 4}" y1="${mid}" x2="${mid}" y2="${size - 4}" />
        <line x1="${mid}" y1="${size - 4}" x2="4" y2="${mid}" />
        <line x1="4" y1="${mid}" x2="${mid}" y2="4" />

        <!-- Diagonal Crossed Lines -->
        <line x1="4" y1="4" x2="${size - 4}" y2="${size - 4}" />
        <line x1="${size - 4}" y1="4" x2="4" y2="${size - 4}" />
      </g>`;

    // Render Sign Numbers and Planets for each house
    for (let h = 1; h <= 12; h++) {
      let rashiNum = ((lagnaSign + h - 2) % 12) + 1;
      let pos = houseCoords[h];

      // Sign number
      svg += `<text x="${pos.rashiPos.x}" y="${pos.rashiPos.y}" text-anchor="middle" dominant-baseline="central" fill="#0073CF" font-weight="900" font-size="13" font-family="sans-serif">${rashiNum}</text>`;

      // Planets in house
      let planets = housePlanets[h] || [];
      if (planets.length > 0) {
        let startY = pos.plPos.y - ((planets.length - 1) * 7);
        planets.forEach((p, idx) => {
          let gInfo = this.grahaInfo[p.name] || { sym: p.name.substring(0,2), col: "#2563EB" };
          let retLabel = p.is_retro ? "<tspan fill='#DC2626' font-weight='900'> (R)</tspan>" : "";
          let curY = startY + (idx * 15);
          svg += `<text x="${pos.plPos.x}" y="${curY}" text-anchor="middle" dominant-baseline="central" fill="${gInfo.col}" font-weight="850" font-size="11.5" font-family="sans-serif">${gInfo.sym}${retLabel}</text>`;
        });
      }
    }

    // Chart Center Watermark / Label
    svg += `<g opacity="0.18">
      <text x="${mid}" y="${mid}" text-anchor="middle" dominant-baseline="central" fill="#0073CF" font-size="28" font-weight="900" font-family="sans-serif">${vargaKey}</text>
    </g>`;

    svg += `</svg>`;
    return svg;
  },

  /**
   * Render South Indian Square Chart SVG
   */
  renderSouthIndian(chartData, vargaKey = "D1") {
    const size = 500;
    const box = size / 4;
    
    // South Indian sign positions:
    // Row 0: Pisces(12), Aries(1), Taurus(2), Gemini(3)
    // Row 1: Aquarius(11), [CENTER], [CENTER], Cancer(4)
    // Row 2: Capricorn(10), [CENTER], [CENTER], Leo(5)
    // Row 3: Sagittarius(9), Scorpio(8), Libra(7), Virgo(6)
    const signBoxes = {
      12: { r: 0, c: 0 }, 1: { r: 0, c: 1 }, 2: { r: 0, c: 2 }, 3: { r: 0, c: 3 },
      11: { r: 1, c: 0 }, 4: { r: 1, c: 3 },
      10: { r: 2, c: 0 }, 5: { r: 2, c: 3 },
      9: { r: 3, c: 0 }, 8: { r: 3, c: 1 }, 7: { r: 3, c: 2 }, 6: { r: 3, c: 3 }
    };

    let lagnaSign = (vargaKey === "D1" && chartData.lagna_sign) ? chartData.lagna_sign : 1;
    const planetsSource = (vargaKey === "D1") ? chartData.planets : (chartData.vargas && chartData.vargas[vargaKey] ? chartData.vargas[vargaKey].planets : chartData.planets);

    const signPlanets = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[] };
    if (planetsSource) {
      Object.entries(planetsSource).forEach(([pName, pObj]) => {
        let pSign = pObj.sign || 1;
        if (signPlanets[pSign]) {
          signPlanets[pSign].push({
            name: pName,
            is_retro: pObj.is_retrograde || false
          });
        }
      });
    }

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="svg-kundli" xmlns="http://www.w3.org/2000/svg">
      <!-- Background & Outer Boundary -->
      <rect x="4" y="4" width="${size - 8}" height="${size - 8}" fill="#FFFFFF" stroke="#0073CF" stroke-width="2.5" rx="8" />

      <!-- South Indian 4x4 Grid Lines -->
      <g stroke="#00B0F0" stroke-width="1.8">
        <line x1="${box}" y1="4" x2="${box}" y2="${size - 4}" />
        <line x1="${box * 2}" y1="4" x2="${box * 2}" y2="${box}" />
        <line x1="${box * 2}" y1="${box * 3}" x2="${box * 2}" y2="${size - 4}" />
        <line x1="${box * 3}" y1="4" x2="${box * 3}" y2="${size - 4}" />

        <line x1="4" y1="${box}" x2="${size - 4}" y2="${box}" />
        <line x1="4" y1="${box * 2}" x2="${box}" y2="${box * 2}" />
        <line x1="${box * 3}" y1="${box * 2}" x2="${size - 4}" y2="${box * 2}" />
        <line x1="4" y1="${box * 3}" x2="${size - 4}" y2="${box * 3}" />
      </g>`;

    // Center Box Watermark
    svg += `<g opacity="0.15">
      <text x="${size / 2}" y="${size / 2}" text-anchor="middle" dominant-baseline="central" fill="#0073CF" font-size="24" font-weight="900" font-family="sans-serif">${vargaKey} South Indian</text>
    </g>`;

    // Populate each sign box
    for (let s = 1; s <= 12; s++) {
      let b = signBoxes[s];
      let bx = b.c * box;
      let by = b.r * box;

      let isLagna = (s === lagnaSign);
      if (isLagna) {
        // Red Lagna diagonal slash
        svg += `<line x1="${bx + 4}" y1="${by + 4}" x2="${bx + box - 4}" y2="${by + box - 4}" stroke="#EF4444" stroke-width="1.5" stroke-dasharray="3,3" />`;
        svg += `<text x="${bx + 8}" y="${by + 16}" fill="#DC2626" font-weight="900" font-size="11">लग्न (Asc)</text>`;
      }

      // Rashi label
      svg += `<text x="${bx + box - 6}" y="${by + 14}" text-anchor="end" fill="#64748B" font-size="10" font-weight="700">${this.rashiNames[s - 1]}</text>`;

      // Planets
      let pls = signPlanets[s] || [];
      pls.forEach((p, idx) => {
        let gInfo = this.grahaInfo[p.name] || { sym: p.name.substring(0,2), col: "#2563EB" };
        let curY = by + 30 + (idx * 16);
        let retLabel = p.is_retro ? "<tspan fill='#DC2626'> (R)</tspan>" : "";
        svg += `<text x="${bx + 10}" y="${curY}" fill="${gInfo.col}" font-weight="850" font-size="11">${gInfo.sym}${retLabel}</text>`;
      });
    }

    svg += `</svg>`;
    return svg;
  }
};

window.KundliChartRenderer = KundliChartRenderer;
