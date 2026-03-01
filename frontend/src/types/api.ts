/* TypeScript interfaces matching backend serializers */

// --- Auth (users/views.py GoogleLoginView) ---

export interface LoginUser {
  id: number;
  email: string;
  username: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: LoginUser;
}

export interface TokenRefreshResponse {
  access: string;
  refresh: string;
}

export interface AuthError {
  error: string;
  detail?: string;
}

// --- Daily Challenge (flags/serializers/daily_challenge_serializers.py) ---

export interface ChallengeCountry {
  flag_emoji: string;
  flag_svg_url: string;
  flag_png_url: string;
  flag_alt_text: string;
}

export interface ChallengeQuestion {
  id: number;
  category: string;
  format: string;
  question_text: string;
  metadata: Record<string, unknown>;
}

export interface UserChallengeStatus {
  has_completed: boolean;
  attempts_used: number;
  attempts_remaining: number;
  is_correct: boolean | null;
  last_attempt_at: string | null;
}

export interface DailyChallengeResponse {
  id: number;
  date: string;
  question: ChallengeQuestion;
  country: ChallengeCountry;
  user_status: UserChallengeStatus;
}

// --- Answer Submission (flags/serializers/question_serializers.py + flags/views.py) ---

export interface AnswerSubmission {
  answer_data: { text: string };
  time_taken_seconds?: number;
}

export interface AnswerResult {
  is_correct: boolean;
  explanation: string;
  attempts_remaining: number;
  user_answer_id: number;
  correct_answer?: Record<string, unknown>;
}

// --- Challenge History ---

export interface ChallengeHistoryUserAnswer {
  is_correct: boolean;
  attempts_used: number;
  answered_at: string;
}

export interface ChallengeHistoryCountry {
  code: string;
  name: string;
  flag_emoji: string;
  flag_svg_url: string;
  flag_png_url: string;
}

export interface ChallengeHistoryItem {
  id: number;
  date: string;
  country: ChallengeHistoryCountry;
  user_answer: ChallengeHistoryUserAnswer | null;
}

// --- Country / Encyclopedia ---

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
  area_km2: number;
  highest_point: string | null;
  population: number;
  capital: string;
  largest_city: string;
  languages: string[];
  religions: string[] | null;
  currencies: Record<string, { name: string; symbol: string }>;
  gdp_nominal: number | null;
  gdp_ppp_per_capita: number | null;
  median_age: number | null;
  life_expectancy: number | null;
  school_expectancy: number | null;
  fertility_rate: number | null;
  arable_land_percent: number | null;
  difficulty_tier: string | null;
  popularity_score: number;
}

// --- Pagination ---

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
