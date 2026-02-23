import { create } from 'zustand';
import { fetchDailyChallenge, submitAnswer } from '../api/challenge';
import type { DailyChallengeResponse, AnswerResult } from '../types/api';

interface ChallengeState {
  challenge: DailyChallengeResponse | null;
  lastAnswer: AnswerResult | null;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  startTime: number | null;

  loadChallenge: () => Promise<void>;
  submit: (text: string) => Promise<AnswerResult>;
  startTimer: () => void;
  reset: () => void;
}

export const useChallengeStore = create<ChallengeState>((set, get) => ({
  challenge: null,
  lastAnswer: null,
  isLoading: false,
  isSubmitting: false,
  error: null,
  startTime: null,

  loadChallenge: async () => {
    set({ isLoading: true, error: null });
    try {
      const challenge = await fetchDailyChallenge();
      set({ challenge, isLoading: false });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load challenge';
      set({ error: message, isLoading: false });
    }
  },

  submit: async (text: string) => {
    set({ isSubmitting: true, error: null });
    const { startTime } = get();

    const timeTaken = startTime
      ? Math.round((Date.now() - startTime) / 1000)
      : undefined;

    try {
      const result = await submitAnswer({
        answer_data: { text },
        time_taken_seconds: timeTaken,
      });

      // Optimistically update local challenge status
      set((state) => {
        if (!state.challenge) return { lastAnswer: result, isSubmitting: false };

        return {
          lastAnswer: result,
          isSubmitting: false,
          challenge: {
            ...state.challenge,
            user_status: {
              ...state.challenge.user_status,
              attempts_used: state.challenge.user_status.attempts_used + 1,
              attempts_remaining: result.attempts_remaining,
              is_correct: result.is_correct ? true : (result.attempts_remaining === 0 ? false : null),
              has_completed: result.is_correct || result.attempts_remaining === 0,
              last_attempt_at: new Date().toISOString(),
            },
          },
        };
      });

      return result;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to submit answer';
      set({ error: message, isSubmitting: false });
      throw err;
    }
  },

  startTimer: () => {
    set({ startTime: Date.now() });
  },

  reset: () => {
    set({
      challenge: null,
      lastAnswer: null,
      isLoading: false,
      isSubmitting: false,
      error: null,
      startTime: null,
    });
  },
}));
