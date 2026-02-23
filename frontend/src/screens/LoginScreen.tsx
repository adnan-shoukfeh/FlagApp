import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { useAuthStore } from '../stores/authStore';
import { SignPanel } from '../components/ui/SignPanel';
import { Wordmark } from '../components/ui/Wordmark';

export function LoginScreen() {
  const { isAuthenticated, isLoading, error, login } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/daily', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSuccess = async (response: CredentialResponse) => {
    if (!response.credential) return;
    try {
      await login(response.credential);
      navigate('/daily', { replace: true });
    } catch {
      // Error is set in the store
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      flex: 1,
      gap: 'var(--space-8)',
    }}>
      <Wordmark />

      <SignPanel style={{ width: '100%', maxWidth: 400, textAlign: 'center' }}>
        <h2 style={{
          fontWeight: 700,
          fontSize: 'var(--text-2xl)',
          marginBottom: 'var(--space-2)',
        }}>
          Welcome
        </h2>
        <p style={{
          color: 'var(--color-text-secondary)',
          fontSize: 'var(--text-sm)',
          marginBottom: 'var(--space-6)',
        }}>
          Sign in to start your daily geography challenge
        </p>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => {
              useAuthStore.setState({ error: 'Google sign-in failed' });
            }}
            theme="filled_black"
            shape="pill"
            size="large"
          />
        </div>

        {isLoading && (
          <p style={{
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--text-sm)',
            marginTop: 'var(--space-4)',
          }}>
            Signing in...
          </p>
        )}

        {error && (
          <p style={{
            color: 'var(--color-incorrect)',
            fontSize: 'var(--text-sm)',
            marginTop: 'var(--space-4)',
          }}>
            {error}
          </p>
        )}
      </SignPanel>
    </div>
  );
}
