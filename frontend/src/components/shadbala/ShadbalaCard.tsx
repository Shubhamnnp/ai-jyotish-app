'use client';

import React from 'react';
import { ShadbalaPlanet } from '@/types/astrology';

interface ShadbalaCardProps {
  planets: ShadbalaPlanet[];
  className?: string;
}

export const ShadbalaCard: React.FC<ShadbalaCardProps> = ({ planets, className = '' }) => {
  if (!planets || planets.length === 0) {
    return null;
  }

  // Calculate summary stats
  const strongCount = planets.filter((p) => p.is_strong).length;
  const avgRatio = planets.reduce((acc, p) => acc + p.strength_ratio, 0) / planets.length;
  const topPlanet = [...planets].sort((a, b) => b.strength_ratio - a.strength_ratio)[0];
  const lowestPlanet = [...planets].sort((a, b) => a.strength_ratio - b.strength_ratio)[0];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Executive Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
          <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">शिरोमणि बली ग्रह</div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-base font-bold text-emerald-600 dark:text-emerald-400">{topPlanet.name_hi}</span>
            <span className="text-xs font-mono text-slate-500">{topPlanet.strength_ratio.toFixed(2)}x</span>
          </div>
        </div>

        <div className="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
          <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">न्यूनतम बली ग्रह</div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-base font-bold text-amber-600 dark:text-amber-400">{lowestPlanet.name_hi}</span>
            <span className="text-xs font-mono text-slate-500">{lowestPlanet.strength_ratio.toFixed(2)}x</span>
          </div>
        </div>

        <div className="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
          <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">बलवान् ग्रह</div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-base font-bold text-slate-800 dark:text-slate-100">{strongCount} / 7</span>
            <span className="text-xs text-slate-500">ग्रह समर्थ</span>
          </div>
        </div>

        <div className="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
          <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">औसत सामर्थ्य</div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-base font-bold text-blue-600 dark:text-blue-400">{avgRatio.toFixed(2)}x</span>
            <span className="text-xs text-slate-500">मानक (1.0x)</span>
          </div>
        </div>
      </div>

      {/* Modern Comparative Gauges */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
            षड्बल सामर्थ्य अनुपात (Shadbala Strength Gauge)
          </h3>
          <span className="text-xs font-mono text-slate-500">
            न्यूनतम मानक: 1.00x = बलवान्
          </span>
        </div>

        <div className="space-y-3.5">
          {planets.map((planet) => {
            const ratio = planet.strength_ratio;
            const pct = Math.min(Math.round((ratio / 2.0) * 100), 100);
            const isStrong = planet.is_strong;

            return (
              <div key={planet.name} className="flex flex-col gap-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-800 dark:text-slate-100 w-16">
                      {planet.name_hi} ({planet.name.slice(0, 3)})
                    </span>
                    <span
                      className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                        isStrong
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400'
                          : 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                      }`}
                    >
                      {isStrong ? 'बलवान्' : 'निर्बल'}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 font-mono">
                    <span className="text-slate-400 text-[11px]">
                      {planet.total_virupas.toFixed(0)} / {planet.required_virupas.toFixed(0)} V
                    </span>
                    <span
                      className={`text-xs font-bold w-12 text-right ${
                        isStrong
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-rose-600 dark:text-rose-400'
                      }`}
                    >
                      {ratio.toFixed(2)}x
                    </span>
                  </div>
                </div>

                {/* Relative Progress Bar with 1.00 marker (at 50%) */}
                <div className="relative w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${pct}%` }}
                    className={`h-full rounded-full transition-all duration-500 ${
                      isStrong
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                        : 'bg-gradient-to-r from-rose-500 to-amber-500'
                    }`}
                  />
                  {/* Benchmark tick at 50% (representing 1.00x) */}
                  <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-slate-400/60 dark:bg-slate-500/80 z-10" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ShadbalaCard;
