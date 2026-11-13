'use client';

import React, { useState, useEffect } from 'react';
import { NorthIndianChart } from '@/components/kundali/NorthIndianChart';
import { SouthIndianChart } from '@/components/kundali/SouthIndianChart';
import { ShadbalaCard } from '@/components/shadbala/ShadbalaCard';
import { DashaTimeline } from '@/components/dasha/DashaTimeline';
import { PrashnaWorkbench } from '@/components/prashna/PrashnaWorkbench';
import { fetchChart, fetchShadbala, fetchActiveDasha, DEFAULT_CHART, DEFAULT_SHADBALA, DEFAULT_DASHA } from '@/lib/api';
import { KundaliChart, ShadbalaPlanet, DashaInfo, PlanetPosition } from '@/types/astrology';

export default function DashboardPage() {
  const [chart, setChart] = useState<KundaliChart>(DEFAULT_CHART);
  const [shadbala, setShadbala] = useState<ShadbalaPlanet[]>(DEFAULT_SHADBALA);
  const [dasha, setDasha] = useState<DashaInfo>(DEFAULT_DASHA);
  const [chartFormat, setChartFormat] = useState<'north' | 'south' | 'dual'>('north');
  const [activeTab, setActiveTab] = useState<'kundali' | 'shadbala' | 'dasha' | 'prashna'>('kundali');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPlanet, setSelectedPlanet] = useState<PlanetPosition | null>(null);
  const [isPramanaOpen, setIsPramanaOpen] = useState(false);

  // Load from backend API if available, gracefully fallback
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const c = await fetchChart();
        setChart(c);
        const sb = await fetchShadbala();
        if (sb && sb.length > 0) setShadbala(sb);
        const d = await fetchActiveDasha();
        if (d) setDasha(d);
      } catch (e) {
        console.warn('Backend API connection using resilient client state:', e);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* ─── 1. EXECUTIVE HEADER ─── */}
      <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-4 py-2.5">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center font-bold text-slate-950 text-base shadow-sm">
              ॐ
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-slate-100">
                  Jyotish<span className="text-amber-500">OS</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded">
                  PRO v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Premium Classical Vedic Astrology Platform
              </p>
            </div>
          </div>

          {/* Native Summary Capsule */}
          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <div className="flex flex-col">
              <span className="font-semibold text-slate-200">
                {chart.native_name || 'श्री जातक'}
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {chart.birth_date} • {chart.birth_time} (IST)
              </span>
            </div>
            <div className="h-6 w-px bg-slate-800" />
            <div className="flex flex-col">
              <span className="text-slate-300 font-mono text-[11px]">
                {chart.latitude.toFixed(2)}°N, {chart.longitude.toFixed(2)}°E
              </span>
              <span className="text-[10px] text-amber-500 font-medium">
                {chart.ayanamsa_name} अयनांश ({chart.ayanamsa_value.toFixed(2)}°)
              </span>
            </div>
          </div>

          {/* Engine Status & Chart Switcher */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md text-[11px]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Swiss Ephemeris</span>
            </div>

            <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-0.5">
              <button
                onClick={() => setChartFormat('north')}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                  chartFormat === 'north'
                    ? 'bg-amber-500 text-slate-950 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                उत्तर (North)
              </button>
              <button
                onClick={() => setChartFormat('south')}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                  chartFormat === 'south'
                    ? 'bg-amber-500 text-slate-950 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                दक्षिण (South)
              </button>
              <button
                onClick={() => setChartFormat('dual')}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                  chartFormat === 'dual'
                    ? 'bg-amber-500 text-slate-950 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                द्विचक्र (Dual)
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ─── 2. PRIMARY NAVIGATION TABS ─── */}
      <div className="border-b border-slate-800 bg-slate-900/60 px-4">
        <div className="max-w-7xl mx-auto flex gap-1">
          {[
            { id: 'kundali', label: 'कुण्डली चक्र (Charts & Positions)' },
            { id: 'shadbala', label: 'षड्बल सामर्थ्य (Shadbala Strength)' },
            { id: 'dasha', label: 'विंशोत्तरी दशा (Vimshottari Dasha)' },
            { id: 'prashna', label: 'तात्कालिक प्रश्न (Prashna Engine)' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2.5 text-xs font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'border-amber-500 text-amber-400 font-semibold bg-amber-500/5'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ─── 3. MAIN DASHBOARD CONTENT ─── */}
      <main className="max-w-7xl mx-auto w-full p-4 flex-1 space-y-4">
        {activeTab === 'kundali' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Chart Column (7 cols on desktop) */}
            <div className={chartFormat === 'dual' ? 'lg:col-span-12' : 'lg:col-span-7'}>
              {chartFormat === 'dual' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <NorthIndianChart
                    chart={chart}
                    title="लग्न कुण्डली (उत्तर भारतीय)"
                    onPlanetClick={(p) => setSelectedPlanet(p)}
                  />
                  <SouthIndianChart
                    chart={chart}
                    title="लग्न कुण्डली (दक्षिण भारतीय)"
                    onPlanetClick={(p) => setSelectedPlanet(p)}
                  />
                </div>
              ) : chartFormat === 'north' ? (
                <NorthIndianChart
                  chart={chart}
                  title="लग्न कुण्डली (D1 - Rashi Chart)"
                  onPlanetClick={(p) => setSelectedPlanet(p)}
                />
              ) : (
                <SouthIndianChart
                  chart={chart}
                  title="लग्न कुण्डली (D1 - Rashi Chart)"
                  onPlanetClick={(p) => setSelectedPlanet(p)}
                />
              )}
            </div>

            {/* Planetary Matrix & Selected Inspector (5 cols on desktop) */}
            {chartFormat !== 'dual' && (
              <div className="lg:col-span-5 space-y-3">
                {/* Planet Selected Micro-Card */}
                {selectedPlanet && (
                  <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-center justify-between animate-fadeIn">
                    <div className="flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center text-sm">
                        {selectedPlanet.name_hi}
                      </span>
                      <div>
                        <div className="text-xs font-bold text-slate-100">
                          {selectedPlanet.name_hi} ({selectedPlanet.name})
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {selectedPlanet.sign_name} • {selectedPlanet.sign_degree.toFixed(2)}° [{selectedPlanet.nakshatra_name}-P{selectedPlanet.nakshatra_pada}]
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedPlanet(null)}
                      className="text-xs text-slate-400 hover:text-slate-200 px-2 py-1"
                    >
                      ✕
                    </button>
                  </div>
                )}

                {/* Planetary Coordinate Table */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
                  <div className="px-3.5 py-2.5 border-b border-slate-800 flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200">
                      ग्रह स्पष्ट एवं स्थिति तालिका
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      निरयण राशि चक्र
                    </span>
                  </div>

                  <div className="overflow-x-auto max-h-[460px] overflow-y-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-950/60 text-[10px] text-slate-400 uppercase tracking-wider sticky top-0 border-b border-slate-800">
                        <tr>
                          <th className="py-2 px-3">ग्रह</th>
                          <th className="py-2 px-2">राशि</th>
                          <th className="py-2 px-2">अंश</th>
                          <th className="py-2 px-2">नक्षत्र</th>
                          <th className="py-2 px-2 text-center">भाव</th>
                          <th className="py-2 px-2 text-center">गति</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                        {Object.values(chart.planets || {}).map((p) => {
                          const deg = Math.floor(p.sign_degree);
                          const min = Math.round((p.sign_degree - deg) * 60);
                          const isSelected = selectedPlanet?.name === p.name;

                          return (
                            <tr
                              key={p.name}
                              onClick={() => setSelectedPlanet(p)}
                              className={`cursor-pointer transition-colors ${
                                isSelected
                                  ? 'bg-amber-500/15 text-amber-300'
                                  : 'hover:bg-slate-800/40 text-slate-300'
                              }`}
                            >
                              <td className="py-2 px-3 font-sans font-semibold text-slate-100 flex items-center gap-1.5">
                                <span>{p.name_hi || p.name}</span>
                                <span className="text-[10px] text-slate-500">
                                  {p.name.slice(0, 2)}
                                </span>
                              </td>
                              <td className="py-2 px-2 font-sans text-slate-300">
                                {p.sign_name}
                              </td>
                              <td className="py-2 px-2">
                                {deg}° {min.toString().padStart(2, '0')}'
                              </td>
                              <td className="py-2 px-2 font-sans text-slate-400 truncate max-w-[90px]">
                                {p.nakshatra_name || p.nakshatra}-P{p.nakshatra_pada}
                              </td>
                              <td className="py-2 px-2 text-center font-bold text-amber-400">
                                {p.house}
                              </td>
                              <td className="py-2 px-2 text-center font-sans">
                                {p.is_retrograde ? (
                                  <span className="px-1 py-0.5 rounded text-[9px] bg-rose-500/20 text-rose-400 font-bold">
                                    वक्र
                                  </span>
                                ) : (
                                  <span className="text-slate-500 text-[10px]">
                                    मार्गी
                                  </span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'shadbala' && <ShadbalaCard planets={shadbala} />}

        {activeTab === 'dasha' && <DashaTimeline dasha={dasha} />}

        {activeTab === 'prashna' && <PrashnaWorkbench />}

        {/* ─── 4. BOTTOM COLLAPSIBLE SHASTRIYA DRAWER ─── */}
        <div className="pt-2">
          <button
            onClick={() => setIsPramanaOpen(!isPramanaOpen)}
            className="w-full flex items-center justify-between p-3 bg-slate-900 border border-slate-800 rounded-xl text-left text-xs text-slate-300 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-amber-500 font-bold">📜</span>
              <span className="font-semibold text-slate-200">
                शास्त्रीय प्रमाण एवं ग्रंथ सूत्र (Shastriya Reference Drawer)
              </span>
            </div>
            <span className="text-slate-400 text-xs font-mono">
              {isPramanaOpen ? '▲ बन्द करें' : '▼ विस्तार करें'}
            </span>
          </button>

          {isPramanaOpen && (
            <div className="mt-2 p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3 text-xs leading-relaxed text-slate-300">
              <div className="border-l-2 border-amber-500 pl-3">
                <div className="font-bold text-amber-400">
                  बृहत्पाराशर होराशास्त्रम् (BPHS Ch. 27-29)
                </div>
                <div className="font-serif italic text-slate-400 mt-1">
                  स्थानं दिग्कालचेष्टा च नैसर्गं दृग्बलं तथा। षड्विधं बलमेतेषां ग्रहाणां कथयाम्यहम्॥
                </div>
                <div className="text-slate-400 mt-1 text-[11px]">
                  स्थान बल, दिग्बल, काल बल, चेष्टा बल, नैसर्गिक बल एवं दृग्बल — ये षड्बल के छह मुख्य आधार हैं।
                </div>
              </div>

              <div className="border-l-2 border-blue-500 pl-3">
                <div className="font-bold text-blue-400">
                  ताजिक नीलकण्ठी (संज्ञा तंत्र)
                </div>
                <div className="font-serif italic text-slate-400 mt-1">
                  शीघ्रगो मन्दगस्याग्रे दीप्तांशे यदि संस्थितः। इत्थशालं विजानीयात् कार्यसिद्धिकरं परम्॥
                </div>
                <div className="text-slate-400 mt-1 text-[11px]">
                  शीघ्रगामी ग्रह जब मन्दगामी ग्रह के दीप्तांश भीतर संबंध बनाता है तो इत्थशाल योग बनता है, जो तात्कालिक कार्य सिद्धि का प्रमाण है।
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* ─── 5. CLEAN FOOTER ─── */}
      <footer className="border-t border-slate-900 py-3 px-4 text-center text-[11px] text-slate-500 font-mono">
        JyotishOS Engine • Swiss Ephemeris v2.10 • Parashara & Tajika Shastras
      </footer>
    </div>
  );
}
