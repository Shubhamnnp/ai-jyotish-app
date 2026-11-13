'use client';

import React from 'react';
import { DashaInfo } from '@/types/astrology';

interface DashaTimelineProps {
  dasha?: DashaInfo;
  className?: string;
}

export const DashaTimeline: React.FC<DashaTimelineProps> = ({ dasha, className = '' }) => {
  if (!dasha) {
    return null;
  }

  // Active Dasha cards
  const levels = [
    { label: 'महादशा (Mahadasha)', planet: dasha.mahadasha, color: 'text-amber-600 dark:text-amber-400', border: 'border-amber-500/40' },
    { label: 'अन्तर्दशा (Antardasha)', planet: dasha.antardasha, color: 'text-blue-600 dark:text-blue-400', border: 'border-blue-500/40' },
    { label: 'प्रत्यन्तर्दशा (Pratyantardasha)', planet: dasha.pratyantardasha, color: 'text-purple-600 dark:text-purple-400', border: 'border-purple-500/40' },
    { label: 'सूक्ष्मदशा (Sukshma)', planet: dasha.sookshmadasha, color: 'text-emerald-600 dark:text-emerald-400', border: 'border-emerald-500/40' },
  ];

  const pct = Math.min(Math.max(dasha.progress_percentage || 50, 0), 100);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Active Dasha Hierarchy Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {levels.map((lvl) => (
          <div
            key={lvl.label}
            className={`p-3 bg-white dark:bg-slate-900 border ${lvl.border} rounded-lg shadow-2xs`}
          >
            <div className="text-[10px] font-medium text-slate-500 tracking-wider truncate">
              {lvl.label}
            </div>
            <div className={`mt-1 text-lg font-bold ${lvl.color}`}>
              {lvl.planet}
            </div>
          </div>
        ))}
      </div>

      {/* Timeline Progress */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">
              सक्रिय विंशोत्तरी काल-चक्र
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              {dasha.mahadasha} - {dasha.antardasha}
            </span>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {dasha.start_date} → {dasha.end_date}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-slate-500">
            <span>महादशा प्रगति</span>
            <span className="font-mono font-medium">{pct.toFixed(1)}% पूर्ण</span>
          </div>
          <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              style={{ width: `${pct}%` }}
              className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full transition-all duration-700"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashaTimeline;
