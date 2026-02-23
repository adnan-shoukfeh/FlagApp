import client from './client';
import type {
  DailyChallengeResponse,
  AnswerSubmission,
  AnswerResult,
  ChallengeHistoryItem,
  PaginatedResponse,
} from '../types/api';

export async function fetchDailyChallenge(): Promise<DailyChallengeResponse> {
  const { data } = await client.get<DailyChallengeResponse>('/daily/');
  return data;
}

export async function submitAnswer(submission: AnswerSubmission): Promise<AnswerResult> {
  const { data } = await client.post<AnswerResult>('/daily/answer/', submission);
  return data;
}

export async function fetchChallengeHistory(
  page = 1
): Promise<PaginatedResponse<ChallengeHistoryItem>> {
  const { data } = await client.get<PaginatedResponse<ChallengeHistoryItem>>(
    '/daily/history/',
    { params: { page } }
  );
  return data;
}
