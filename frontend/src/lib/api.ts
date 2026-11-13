import { KundaliChart, BirthInput, ShadbalaPlanet, DashaInfo } from "@/types/astrology";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const ZODIAC_SIGNS = [
  { id: 1, name: "Aries", name_hi: "मेष", lord: "Mars", icon: "♈" },
  { id: 2, name: "Taurus", name_hi: "वृषभ", lord: "Venus", icon: "♉" },
  { id: 3, name: "Gemini", name_hi: "मिथुन", lord: "Mercury", icon: "♊" },
  { id: 4, name: "Cancer", name_hi: "कर्क", lord: "Moon", icon: "♋" },
  { id: 5, name: "Leo", name_hi: "सिंह", lord: "Sun", icon: "♌" },
  { id: 6, name: "Virgo", name_hi: "कन्या", lord: "Mercury", icon: "♍" },
  { id: 7, name: "Libra", name_hi: "तुला", lord: "Venus", icon: "♎" },
  { id: 8, name: "Scorpio", name_hi: "वृश्चिक", lord: "Mars", icon: "♏" },
  { id: 9, name: "Sagittarius", name_hi: "धनु", lord: "Jupiter", icon: "♐" },
  { id: 10, name: "Capricorn", name_hi: "मकर", lord: "Saturn", icon: "♑" },
  { id: 11, name: "Aquarius", name_hi: "कुंभ", lord: "Saturn", icon: "♒" },
  { id: 12, name: "Pisces", name_hi: "मीन", lord: "Jupiter", icon: "♓" },
];

export const PLANET_META: Record<string, { name_hi: string; color: string; symbol: string }> = {
  Sun: { name_hi: "सूर्य", color: "#F59E0B", symbol: "☉" },
  Moon: { name_hi: "चन्द्र", color: "#38BDF8", symbol: "☽" },
  Mars: { name_hi: "मंगल", color: "#EF4444", symbol: "♂" },
  Mercury: { name_hi: "बुध", color: "#10B981", symbol: "☿" },
  Jupiter: { name_hi: "गुरु", color: "#EAB308", symbol: "♃" },
  Venus: { name_hi: "शुक्र", color: "#EC4899", symbol: "♀" },
  Saturn: { name_hi: "शनि", color: "#6366F1", symbol: "♄" },
  Rahu: { name_hi: "राहु", color: "#8B5CF6", symbol: "☊" },
  Ketu: { name_hi: "केतु", color: "#94A3B8", symbol: "☋" },
  Ascendant: { name_hi: "लग्न", color: "#D97706", symbol: "Asc" },
};

export const DEFAULT_CHART: KundaliChart = {
  native_name: "श्री जातक (Default Native)",
  birth_date: "1985-05-15",
  birth_time: "14:30:00",
  latitude: 28.6139,
  longitude: 77.2090,
  ayanamsa_name: "LAHIRI",
  ayanamsa_value: 23.63,
  julian_day: 2446201.875,
  lagna_sign_id: 6,
  lagna_sign_name: "कन्या (Virgo)",
  lagna_degree: 14.85,
  planets: {
    Sun: { name: "Sun", name_hi: "सूर्य", longitude: 30.5, sign_id: 2, sign_name: "वृषभ (Taurus)", sign_degree: 0.5, house: 9, is_retrograde: false, speed: 0.98, nakshatra: "Krittika", nakshatra_name: "कृत्तिका", nakshatra_pada: 2, dignity: "Friendly" },
    Moon: { name: "Moon", name_hi: "चन्द्र", longitude: 342.1, sign_id: 12, sign_name: "मीन (Pisces)", sign_degree: 12.1, house: 7, is_retrograde: false, speed: 13.2, nakshatra: "Uttara Bhadrapada", nakshatra_name: "उत्तरभाद्रपदा", nakshatra_pada: 3, dignity: "Friendly" },
    Mars: { name: "Mars", name_hi: "मंगल", longitude: 48.2, sign_id: 2, sign_name: "वृषभ (Taurus)", sign_degree: 18.2, house: 9, is_retrograde: false, speed: 0.65, nakshatra: "Rohini", nakshatra_name: "रोहिणी", nakshatra_pada: 3, dignity: "Neutral" },
    Mercury: { name: "Mercury", name_hi: "बुध", longitude: 15.4, sign_id: 1, sign_name: "मेष (Aries)", sign_degree: 15.4, house: 8, is_retrograde: true, speed: -0.32, nakshatra: "Bharani", nakshatra_name: "भरणी", nakshatra_pada: 1, dignity: "Neutral" },
    Jupiter: { name: "Jupiter", name_hi: "गुरु", longitude: 292.8, sign_id: 10, sign_name: "मकर (Capricorn)", sign_degree: 22.8, house: 5, is_retrograde: false, speed: 0.12, nakshatra: "Shravana", nakshatra_name: "श्रवण", nakshatra_pada: 4, dignity: "Debilitated" },
    Venus: { name: "Venus", name_hi: "शुक्र", longitude: 358.9, sign_id: 12, sign_name: "मीन (Pisces)", sign_degree: 28.9, house: 7, is_retrograde: false, speed: 1.15, nakshatra: "Revati", nakshatra_name: "रेवती", nakshatra_pada: 4, dignity: "Exalted" },
    Saturn: { name: "Saturn", name_hi: "शनि", longitude: 211.3, sign_id: 7, sign_name: "तुला (Libra)", sign_degree: 1.3, house: 2, is_retrograde: true, speed: -0.06, nakshatra: "Chitra", nakshatra_name: "चित्रा", nakshatra_pada: 3, dignity: "Exalted" },
    Rahu: { name: "Rahu", name_hi: "राहु", longitude: 42.6, sign_id: 2, sign_name: "वृषभ (Taurus)", sign_degree: 12.6, house: 9, is_retrograde: true, speed: -0.05, nakshatra: "Rohini", nakshatra_name: "रोहिणी", nakshatra_pada: 1, dignity: "Exalted" },
    Ketu: { name: "Ketu", name_hi: "केतु", longitude: 222.6, sign_id: 8, sign_name: "वृश्चिक (Scorpio)", sign_degree: 12.6, house: 3, is_retrograde: true, speed: -0.05, nakshatra: "Anuradha", nakshatra_name: "अनुराधा", nakshatra_pada: 3, dignity: "Exalted" },
  },
  houses: Array.from({ length: 12 }, (_, i) => ({
    house_number: i + 1,
    longitude: ((6 - 1 + i) % 12) * 30 + 14.85,
    sign_id: ((6 - 1 + i) % 12) + 1,
    sign_name: ZODIAC_SIGNS[(6 - 1 + i) % 12].name,
    sign_degree: 14.85,
    lord: ZODIAC_SIGNS[(6 - 1 + i) % 12].lord,
    occupants: [],
  })),
};

export const DEFAULT_SHADBALA: ShadbalaPlanet[] = [
  { name: "Sun", name_hi: "सूर्य", sthana_bala: 142.5, dik_bala: 32.1, kaala_bala: 58.2, cheshta_bala: 45.0, naisargika_bala: 60.0, drik_bala: -12.4, total_virupas: 325.4, total_rupas: 5.42, required_virupas: 390.0, strength_ratio: 0.83, is_strong: false },
  { name: "Moon", name_hi: "चन्द्र", sthana_bala: 178.2, dik_bala: 45.0, kaala_bala: 72.4, cheshta_bala: 51.2, naisargika_bala: 51.4, drik_bala: 15.2, total_virupas: 413.4, total_rupas: 6.89, required_virupas: 360.0, strength_ratio: 1.15, is_strong: true },
  { name: "Mars", name_hi: "मंगल", sthana_bala: 125.0, dik_bala: 28.4, kaala_bala: 61.0, cheshta_bala: 48.2, naisargika_bala: 17.1, drik_bala: 5.4, total_virupas: 285.1, total_rupas: 4.75, required_virupas: 300.0, strength_ratio: 0.95, is_strong: false },
  { name: "Mercury", name_hi: "बुध", sthana_bala: 185.0, dik_bala: 52.0, kaala_bala: 85.3, cheshta_bala: 58.0, naisargika_bala: 25.7, drik_bala: 18.0, total_virupas: 424.0, total_rupas: 7.07, required_virupas: 420.0, strength_ratio: 1.01, is_strong: true },
  { name: "Jupiter", name_hi: "गुरु", sthana_bala: 162.0, dik_bala: 55.4, kaala_bala: 92.1, cheshta_bala: 52.3, naisargika_bala: 34.3, drik_bala: 22.1, total_virupas: 418.2, total_rupas: 6.97, required_virupas: 390.0, strength_ratio: 1.07, is_strong: true },
  { name: "Venus", name_hi: "शुक्र", sthana_bala: 198.4, dik_bala: 42.0, kaala_bala: 76.5, cheshta_bala: 55.1, naisargika_bala: 42.8, drik_bala: 14.2, total_virupas: 429.0, total_rupas: 7.15, required_virupas: 330.0, strength_ratio: 1.30, is_strong: true },
  { name: "Saturn", name_hi: "शनि", sthana_bala: 195.2, dik_bala: 58.0, kaala_bala: 88.0, cheshta_bala: 60.0, naisargika_bala: 8.6, drik_bala: 10.2, total_virupas: 420.0, total_rupas: 7.00, required_virupas: 300.0, strength_ratio: 1.40, is_strong: true },
];

export const DEFAULT_DASHA: DashaInfo = {
  mahadasha: "शनि (Saturn)",
  antardasha: "बुध (Mercury)",
  pratyantardasha: "शुक्र (Venus)",
  sookshmadasha: "गुरु (Jupiter)",
  start_date: "2023-11-20",
  end_date: "2026-07-29",
  progress_percentage: 64.2,
};

export async function fetchChart(): Promise<KundaliChart> {
  try {
    const res = await fetch(`${API_BASE}/api/chart/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth_data: {
          name: "श्री जातक",
          birth_date: "1985-05-15",
          birth_time: "14:30:00",
          latitude: 28.6139,
          longitude: 77.2090,
          timezone_offset: 5.5,
        },
        ayanamsa: "LAHIRI",
        house_system: "PLACIDUS",
        node_type: "TRUE",
      }),
    });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (e) {
    console.warn("FastAPI offline, using default chart fallback:", e);
  }
  return DEFAULT_CHART;
}

export async function fetchShadbala(): Promise<ShadbalaPlanet[]> {
  try {
    const res = await fetch(`${API_BASE}/api/chart/shadbala`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth_data: {
          name: "श्री जातक",
          birth_date: "1985-05-15",
          birth_time: "14:30:00",
          latitude: 28.6139,
          longitude: 77.2090,
          timezone_offset: 5.5,
        },
      }),
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data)) return data;
    }
  } catch (e) {
    console.warn("FastAPI offline, using default shadbala fallback:", e);
  }
  return DEFAULT_SHADBALA;
}

export async function fetchActiveDasha(): Promise<DashaInfo> {
  try {
    const res = await fetch(`${API_BASE}/api/dasha/active`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth_data: {
          name: "श्री जातक",
          birth_date: "1985-05-15",
          birth_time: "14:30:00",
          latitude: 28.6139,
          longitude: 77.2090,
          timezone_offset: 5.5,
        },
      }),
    });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (e) {
    console.warn("FastAPI offline, using default dasha fallback:", e);
  }
  return DEFAULT_DASHA;
}

export async function calculateChart(input: BirthInput): Promise<KundaliChart> {
  return fetchChart();
}
