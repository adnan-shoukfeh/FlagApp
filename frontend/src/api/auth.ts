import client from './client';
import type { LoginResponse } from '../types/api';

export async function googleLogin(idToken: string): Promise<LoginResponse> {
  const { data } = await client.post<LoginResponse>('/auth/google/', {
    id_token: idToken,
  });
  return data;
}
