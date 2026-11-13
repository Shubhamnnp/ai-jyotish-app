"use client";

import React, { useState } from "react";
import { KundaliChart, PlanetPosition } from "@/types/astrology";
import { PLANET_META, ZODIAC_SIGNS } from "@/lib/api";

interface Props {
  chart: KundaliChart;
  title?: string;
  className?: string;
  onPlanetClick?: (planet: PlanetPosition) => void;
}

interface HouseCoord {
  id: number;
  signX: number;
  signY: number;
  planetsX: number;
  planetsY: number;
  label: string;
}

const HOUSE_COORDS: HouseCoord[] = [
  { id: 1, signX: 250, signY: 185, planetsX: 250, planetsY: 110, label: "१ लग्न" },
  { id: 2, signX: 165, signY: 90, planetsX: 135, planetsY: 45, label: "२ धन" },
  { id: 3, signX: 90, signY: 165, planetsX: 45, planetsY: 135, label: "३ सहज" },
  { id: 4, signX: 185, signY: 250, planetsX: 110, planetsY: 250, label: "४ सुख" },
  { id: 5, signX: 90, signY: 335, planetsX: 45, planetsY: 365, label: "५ सुत" },
  { id: 6, signX: 165, signY: 410, planetsX: 135, planetsY: 455, label: "६ रिपु" },
  { id: 7, signX: 250, signY: 315, planetsX: 250, planetsY: 390, label: "७ जाया" },
  { id: 8, signX: 335, signY: 410, planetsX: 365, planetsY: 455, label: "८ रन्ध्र" },
  { id: 9, signX: 410, signY: 335, planetsX: 455, planetsY: 365, label: "९ भाग्य" },
  { id: 10, signX: 315, signY: 250, planetsX: 390, planetsY: 250, label: "१० कर्म" },
  { id: 11, signX: 410, signY: 165, planetsX: 455, planetsY: 135, label: "११ लाभ" },
  { id: 12, signX: 335, signY: 90, planetsX: 365, planetsY: 45, label: "१२ व्यय" },
];

export const NorthIndianChart: React.FC<Props> = ({ chart, title = "जन्म कुण्डली (D1)", className = "", onPlanetClick }) => {
  const [hoveredHouse, setHoveredHouse] = useState<number | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<PlanetPosition | null>(null);

  const lagnaId = chart.lagna_sign_id || 1;

  // Group planets by house (1 to 12)
  const planetsByHouse: Record<number, PlanetPosition[]> = {};
  for (let h = 1; h <= 12; h++) {
    planetsByHouse[h] = [];
  }

  Object.values(chart.planets || {}).forEach((p) => {
    // Calculate house from lagna if not explicitly provided
    let h = p.house;
    if (!h || h < 1 || h > 12) {
      h = ((p.sign_id - lagnaId + 12) % 12) + 1;
    }
    planetsByHouse[h]?.push(p);
  });

  return (
    <div className={`relative flex flex-col items-center bg-white dark:bg-slate-900 border border-amber-200/60 dark:border-slate-800 rounded-2xl p-4 shadow-sm ${className}`}>
      {/* Title & Badge */}
      <div className="w-full flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <span className="text-amber-500 font-bold text-lg">✦</span>
          <h3 className="font-bold text-slate-800 dark:text-slate-100 text-sm md:text-base">{title}</h3>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20">
          लग्न: {ZODIAC_SIGNS[(lagnaId - 1) % 12]?.name_hi} ({chart.lagna_degree ? `${Math.floor(chart.lagna_degree)}°` : ""})
        </span>
      </div>

      {/* SVG Canvas */}
      <div className="relative w-full max-w-[460px] aspect-square">
        <svg viewBox="0 0 500 500" className="w-full h-full select-none drop-shadow-sm font-sans">
          <defs>
            <linearGradient id="bgGradLight" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFDF9" />
              <stop offset="100%" stopColor="#FAF5EB" />
            </linearGradient>
            <linearGradient id="bgGradDark" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0F172A" />
              <stop offset="100%" stopColor="#0B0F19" />
            </linearGradient>
            <linearGradient id="kendraGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#D97706" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#F59E0B" stopOpacity="0.03" />
            </linearGradient>
          </defs>

          {/* Outer Square Background */}
          <rect x="10" y="10" width="480" height="480" rx="12" fill="url(#bgGradLight)" className="dark:hidden" />
          <rect x="10" y="10" width="480" height="480" rx="12" fill="url(#bgGradDark)" className="hidden dark:block" />

          {/* Kendra Houses subtle highlight (1, 4, 7, 10) */}
          <polygon points="250,20 480,250 250,480 20,250" fill="url(#kendraGrad)" />

          {/* Kundali Geometry Lines */}
          <g stroke="currentColor" className="text-amber-600/70 dark:text-amber-500/50" strokeWidth="1.75">
            {/* Outer Border */}
            <rect x="20" y="20" width="460" height="460" fill="none" rx="6" />

            {/* Diagonals */}
            <line x1="20" y1="20" x2="480" y2="480" />
            <line x1="480" y1="20" x2="20" y2="480" />

            {/* Inner Diamond */}
            <polygon points="250,20 480,250 250,480 20,250" fill="none" />
          </g>

          {/* House Regions: Signs & Planets */}
          {HOUSE_COORDS.map((hc) => {
            const signId = ((lagnaId - 1 + (hc.id - 1)) % 12) + 1;
            const signMeta = ZODIAC_SIGNS[signId - 1];
            const planets = planetsByHouse[hc.id] || [];
            const isHovered = hoveredHouse === hc.id;

            return (
              <g
                key={hc.id}
                onMouseEnter={() => setHoveredHouse(hc.id)}
                onMouseLeave={() => setHoveredHouse(null)}
                className="cursor-pointer transition-opacity"
              >
                {/* Sign Number */}
                <text
                  x={hc.signX}
                  y={hc.signY}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize="12"
                  fontWeight="700"
                  fill="currentColor"
                  className={isHovered ? "text-amber-500 font-extrabold" : "text-amber-700/60 dark:text-amber-400/50"}
                >
                  {signId}
                </text>

                {/* Planets inside House */}
                {planets.map((p, idx) => {
                  const meta = PLANET_META[p.name] || { name_hi: p.name, color: "#475569", symbol: "•" };
                  const yOffset = (idx - (planets.length - 1) / 2) * 16;
                  const deg = Math.floor(p.sign_degree);

                  return (
                    <g
                      key={p.name}
                      transform={`translate(${hc.planetsX}, ${hc.planetsY + yOffset})`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedPlanet(p);
                        onPlanetClick?.(p);
                      }}
                      className="hover:scale-110 transition-transform"
                    >
                      <rect
                        x="-30"
                        y="-8"
                        width="60"
                        height="16"
                        rx="4"
                        fill="currentColor"
                        className="text-slate-100 dark:text-slate-800/80 opacity-0 hover:opacity-100"
                      />
                      <text
                        x="0"
                        y="1"
                        textAnchor="middle"
                        dominantBaseline="central"
                        fontSize="11.5"
                        fontWeight="700"
                        fill={meta.color}
                      >
                        {meta.name_hi}{p.is_retrograde ? "(व)" : ""} <tspan fontSize="9" fontWeight="500" fill="currentColor" className="text-slate-500 dark:text-slate-400">{deg}°</tspan>
                      </text>
                    </g>
                  );
                })}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Planet Micro-Popup */}
      {selectedPlanet && (
        <div className="mt-3 w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl p-2.5 flex items-center justify-between text-xs animate-in fade-in">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800 dark:text-slate-100">
              {PLANET_META[selectedPlanet.name]?.name_hi} ({selectedPlanet.name})
            </span>
            <span className="text-slate-500 dark:text-slate-400">
              {selectedPlanet.sign_name} {Math.floor(selectedPlanet.sign_degree)}° {Math.round((selectedPlanet.sign_degree % 1) * 60)}'
            </span>
            <span className="px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 font-medium text-[10px]">
              {selectedPlanet.nakshatra}-P{selectedPlanet.nakshatra_pada}
            </span>
          </div>
          <button
            onClick={() => setSelectedPlanet(null)}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-bold px-1"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};
