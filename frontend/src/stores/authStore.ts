import { create } from 'zustand';
import { googleLogin } from '../api/auth';
import type { LoginUser } from '../types/api';

interface AuthState {
  user: LoginUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (googleIdToken: string) => Promise<void>;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (googleIdToken: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await googleLogin(googleIdToken);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      set({ user: data.user, isAuthenticated: true, isLoading: false });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Login failed';
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    set({ user: null, isAuthenticated: false, error: null });
  },

  hydrate: () => {
    const token = localStorage.getItem('access_token');
    const userJson = localStorage.getItem('user');
    if (token && userJson) {
      try {
        const user = JSON.parse(userJson) as LoginUser;
        set({ user, isAuthenticated: true });
      } catch {
        // Corrupted data — clear and start fresh
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
    }
  },
}));
