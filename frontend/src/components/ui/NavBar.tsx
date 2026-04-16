import { NavLink } from 'react-router-dom';

const tabs = [
  { label: 'Daily Challenge', emoji: '🚩', to: '/daily', match: ['/daily', '/results'] },
  { label: 'Encyclopedia', emoji: '🌍', to: '/encyclopedia', match: ['/encyclopedia'] },
] as const;

export function NavBar() {
  return (
    <nav className="nav-bar">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          className={({ isActive }) => {
            const active = isActive || (tab.match as readonly string[]).some(
              (p) => window.location.pathname.startsWith(p)
            );
            return `nav-tab${active ? ' active' : ''}`;
          }}
        >
          <span className="nav-tab-icon">{tab.emoji}</span>
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
