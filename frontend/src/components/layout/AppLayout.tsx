import { Outlet } from 'react-router-dom';
import { NavBar } from '../ui/NavBar';
import { useAuthStore } from '../../stores/authStore';

export function AppLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <>
      {isAuthenticated && <NavBar />}
      <div className="app-container">
        <Outlet />
      </div>
    </>
  );
}
