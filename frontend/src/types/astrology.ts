export interface PlanetPosition {
  name: string;
  name_hi?: string;
  longitude: number;
  sign_id: number;
  sign_name: string;
  sign_degree: number;
  house: number;
  is_retrograde: boolean;
  is_combust?: boolean;
  speed: number;
  nakshatra: string;
  nakshatra_name?: string;
  nakshatra_pada: number;
  dignity?: string;
}

export interface HouseCusp {
  house_number: number;
  longitude: number;
  sign_id: number;
  sign_name: string;
  sign_degree: number;
  lord: string;
  occupants?: string[];
}

export interface PanchangData {
  tithi?: string;
  vara?: string;
  nakshatra?: string;
  yoga?: string;
  karana?: string;
  sunrise?: string;
  sunset?: string;
}

export interface KundaliChart {
  native_name?: string;
  birth_date?: string;
  birth_time?: string;
  latitude: number;
  longitude: number;
  ayanamsa_name: string;
  ayanamsa_value: number;
  julian_day: number;
  lagna_sign_id: number;
  lagna_sign_name: string;
  lagna_degree: number;
  planets: Record<string, PlanetPosition>;
  houses: HouseCusp[];
  panchang?: PanchangData;
}

export interface ShadbalaPlanet {
  name: string;
  name_hi: string;
  sthana_bala: number;
  dik_bala: number;
  kaala_bala: number;
  cheshta_bala: number;
  naisargika_bala: number;
  drik_bala: number;
  total_virupas: number;
  total_rupas: number;
  required_virupas: number;
  strength_ratio: number;
  is_strong: boolean;
  ishta_phala?: number;
  kashta_phala?: number;
}

export interface DashaInfo {
  mahadasha: string;
  antardasha: string;
  pratyantardasha: string;
  sookshmadasha: string;
  start_date: string;
  end_date: string;
  progress_percentage: number;
}

export interface BirthInput {
  name: string;
  date: string; // YYYY-MM-DD
  time: string; // HH:MM:SS
  latitude: number;
  longitude: number;
  timezone_offset: number;
  city_name: string;
}
