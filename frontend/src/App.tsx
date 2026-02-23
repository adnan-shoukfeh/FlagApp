import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginScreen } from './screens/LoginScreen';
import { DailyChallengeScreen } from './screens/DailyChallengeScreen';
import { ResultsScreen } from './screens/ResultsScreen';

export default function App() {
  const hydrate = useAuthStore((s) => s.hydrate);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/login" element={<LoginScreen />} />
          <Route
            path="/daily"
            element={
              <ProtectedRoute>
                <DailyChallengeScreen />
              </ProtectedRoute>
            }
          />
          <Route
            path="/results"
            element={
              <ProtectedRoute>
                <ResultsScreen />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/daily" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
