'use client';

import React from 'react';
import { KundaliChart, PlanetPosition } from '@/types/astrology';

interface SouthIndianChartProps {
  chart: KundaliChart;
  title?: string;
  className?: string;
  onPlanetClick?: (planet: PlanetPosition) => void;
}

// Fixed zodiac layout in traditional South Indian format (Clockwise from Aries)
// Grid layout 4x4:
// [Pisces(12),  Aries(1),      Taurus(2),   Gemini(3)]
// [Aquarius(11),   --- CENTER (2x2) ---     Cancer(4)]
// [Capricorn(10),  --- CENTER (2x2) ---     Leo(5)]
// [Sagittarius(9), Scorpio(8),  Libra(7),    Virgo(6)]
const SOUTH_INDIAN_CELLS = [
  { signNum: 12, name: 'Pisces', hi: 'मीन', row: 0, col: 0 },
  { signNum: 1, name: 'Aries', hi: 'मेष', row: 0, col: 1 },
  { signNum: 2, name: 'Taurus', hi: 'वृषभ', row: 0, col: 2 },
  { signNum: 3, name: 'Gemini', hi: 'मिथुन', row: 0, col: 3 },

  { signNum: 11, name: 'Aquarius', hi: 'कुम्भ', row: 1, col: 0 },
  { signNum: 4, name: 'Cancer', hi: 'कर्क', row: 1, col: 3 },

  { signNum: 10, name: 'Capricorn', hi: 'मकर', row: 2, col: 0 },
  { signNum: 5, name: 'Leo', hi: 'सिंह', row: 2, col: 3 },

  { signNum: 9, name: 'Sagittarius', hi: 'धनु', row: 3, col: 0 },
  { signNum: 8, name: 'Scorpio', hi: 'वृश्चिक', row: 3, col: 1 },
  { signNum: 7, name: 'Libra', hi: 'तुला', row: 3, col: 2 },
  { signNum: 6, name: 'Virgo', hi: 'कन्या', row: 3, col: 3 },
];

export const SouthIndianChart: React.FC<SouthIndianChartProps> = ({
  chart,
  title = 'दक्षिण भारतीय चक्र (South Indian Chart)',
  className = '',
  onPlanetClick,
}) => {
  const lagnaSign = chart.lagna_sign_id || 1;

  // Group planets by sign_id (1-12)
  const planetsBySign: Record<number, PlanetPosition[]> = {};
  for (let i = 1; i <= 12; i++) {
    planetsBySign[i] = [];
  }

  const allPlanets = Object.values(chart.planets || {});
  allPlanets.forEach((p) => {
    if (planetsBySign[p.sign_id]) {
      planetsBySign[p.sign_id].push(p);
    }
  });

  return (
    <div className={`flex flex-col items-center justify-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm ${className}`}>
      {title && (
        <div className="w-full flex items-center justify-between pb-3 mb-2 border-b border-slate-100 dark:border-slate-800">
          <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">{title}</span>
          <span className="text-xs text-amber-600 dark:text-amber-400 font-mono font-medium">
            लग्न: {chart.lagna_sign_name} ({chart.lagna_degree.toFixed(2)}°)
          </span>
        </div>
      )}

      {/* 4x4 Grid Container */}
      <div className="grid grid-cols-4 grid-rows-4 w-full max-w-[460px] aspect-square border-2 border-amber-600/70 dark:border-amber-500/70 rounded-lg overflow-hidden bg-slate-50 dark:bg-slate-950">
        {/* Render the 12 Sign cells */}
        {SOUTH_INDIAN_CELLS.map((cell) => {
          const isLagna = cell.signNum === lagnaSign;
          const planetsInBox = planetsBySign[cell.signNum] || [];

          return (
            <div
              key={cell.signNum}
              style={{
                gridRowStart: cell.row + 1,
                gridColumnStart: cell.col + 1,
              }}
              className={`relative border border-amber-500/30 dark:border-amber-500/20 p-1.5 flex flex-col justify-between transition-colors hover:bg-amber-50/50 dark:hover:bg-amber-950/20 ${
                isLagna ? 'bg-amber-500/10 dark:bg-amber-500/15 ring-1 ring-inset ring-amber-500/40' : ''
              }`}
            >
              {/* Top Bar inside cell: Sign indicator + Lagna mark */}
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium">
                <span className="font-sans opacity-70">{cell.hi}</span>
                {isLagna && (
                  <span className="px-1 py-0.2 bg-amber-500 text-slate-950 font-bold text-[9px] rounded uppercase shadow-sm">
                    Lagna
                  </span>
                )}
              </div>

              {/* Planets inside cell */}
              <div className="flex flex-wrap gap-1 content-start py-0.5">
                {planetsInBox.map((p) => (
                  <button
                    key={p.name}
                    onClick={() => onPlanetClick?.(p)}
                    className="inline-flex items-center gap-0.5 px-1 py-0.5 rounded text-[11px] font-semibold bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 hover:border-amber-500 hover:text-amber-600 transition-colors shadow-2xs"
                    title={`${p.name_hi || p.name} ${p.sign_degree.toFixed(2)}° [${p.nakshatra_name || p.nakshatra}]`}
                  >
                    <span>{p.name_hi || p.name.slice(0, 2)}</span>
                    <span className="text-[9px] font-mono font-normal text-slate-500">
                      {Math.floor(p.sign_degree)}°
                    </span>
                    {p.is_retrograde && (
                      <span className="text-[9px] font-bold text-rose-500">(R)</span>
                    )}
                  </button>
                ))}
              </div>

              {/* Bottom house numbering relative to Lagna */}
              <div className="text-[9px] text-slate-400 text-right font-mono">
                H{((cell.signNum - lagnaSign + 12) % 12) + 1}
              </div>
            </div>
          );
        })}

        {/* Center 2x2 Area (Row 2-3, Col 2-3) */}
        <div
          style={{
            gridRow: '2 / span 2',
            gridColumn: '2 / span 2',
          }}
          className="flex flex-col items-center justify-center p-3 bg-gradient-to-br from-amber-500/5 via-transparent to-amber-500/10 border border-amber-500/20 text-center"
        >
          <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-600 dark:text-amber-400 font-bold mb-1">
            ॐ
          </div>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
            {chart.native_name || 'लग्न कुण्डली'}
          </span>
          <span className="text-[10px] text-slate-500 mt-0.5">
            {chart.ayanamsa_name} अयनांश
          </span>
          <span className="text-[10px] text-amber-600/90 dark:text-amber-400/90 font-mono mt-1">
            {chart.lagna_sign_name} ({chart.lagna_degree.toFixed(2)}°)
          </span>
        </div>
      </div>
    </div>
  );
};

export default SouthIndianChart;
