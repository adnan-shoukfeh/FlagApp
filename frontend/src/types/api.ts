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

// --- Pagination ---

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
