export interface CountryListItem {
  code: string;
  name: string;
  flag_emoji: string;
  flag_svg_url: string;
  population: number;
  capital: string;
}

export interface CountryDetail {
  id: number;
  code: string;
  name: string;
  flag_emoji: string;
  flag_svg_url: string;
  flag_png_url: string;
  flag_alt_text: string;
  coat_of_arms_svg_url: string | null;
  coat_of_arms_png_url: string | null;
  latitude: number;
  longitude: number;
  area_km2: number | null;
  highest_point: string | null;
  population: number;
  capital: string;
  largest_city: string | null;
  languages: string[];
  religions: string[];
  currencies: Record<string, { name: string; symbol: string }>;
  gdp_nominal: number | null;
  gdp_ppp_per_capita: number | null;
  median_age: number | null;
  life_expectancy: number | null;
  school_expectancy: number | null;
  fertility_rate: number | null;
  arable_land_percent: number | null;
  difficulty_tier: string;
  popularity_score: number;
}
