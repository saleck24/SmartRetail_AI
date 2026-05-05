import { NavLink, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const navItems = [
  { to: '/dashboard', icon: '⬡', label: 'Dashboard',       section: 'PRINCIPAL' },
  { to: '/stocks',    icon: '📦', label: 'Gestion des Stocks', section: 'PRINCIPAL', badge: null },
  { to: '/eda',       icon: '🔍', label: 'Analyse des Données', section: 'IA' },
  { to: '/predictor', icon: '🔮', label: 'Prédictions IA',  section: 'IA' },
  { to: '/analytics', icon: '📊', label: 'Rapports & Benchmark', section: 'IA' },
];

export default function Sidebar() {
  const [alerts, setAlerts] = useState(0);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await axios.get(`${API}/alerts`);
        setAlerts(res.data.critical_count || 0);
      } catch { setAlerts(3); } // fallback démo
    };
    fetchAlerts();
    const id = setInterval(fetchAlerts, 30000);
    return () => clearInterval(id);
  }, []);

  let lastSection = '';

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🏭</div>
        <h1>SmartRetail AI</h1>
        <span>Optimisation IA des Stocks</span>
      </div>


      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const showSection = item.section !== lastSection;
          if (showSection) lastSection = item.section;
          return (
            <div key={item.to}>
              {showSection && (
                <div className="nav-section-title">{item.section}</div>
              )}
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `nav-item${isActive ? ' active' : ''}`
                }
              >
                <span className="nav-icon">{item.icon}</span>
                <span>{item.label}</span>
                {item.to === '/stocks' && alerts > 0 && (
                  <span className="nav-badge">{alerts}</span>
                )}
              </NavLink>
            </div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">SB</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">Gestionnaire SmartRetail_AI</div>
            <div className="sidebar-user-role">Saleck BAYA · Administrateur</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
