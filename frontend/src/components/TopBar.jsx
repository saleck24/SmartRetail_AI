import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const PAGE_META = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Vue générale des opérations en temps réel' },
  '/stocks':    { title: 'Gestion des Stocks', subtitle: 'Niveaux de stock et alertes de rupture' },
  '/predictor': { title: 'Prédictions IA', subtitle: 'Moteur LightGBM — Prédiction de la demande' },
  '/analytics': { title: 'Rapports & Benchmark', subtitle: 'Comparaison scientifique des modèles IA' },
};

export default function TopBar() {
  const location = useLocation();
  const meta = PAGE_META[location.pathname] || { title: 'SmartRetail_AI', subtitle: '' };
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const fmt = (n) => String(n).padStart(2, '0');
  const clock = `${fmt(time.getHours())}:${fmt(time.getMinutes())}:${fmt(time.getSeconds())}`;
  const dateStr = time.toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  return (
    <header className="topbar">
      <div>
        <div className="topbar-title">{meta.title}</div>
        <div className="topbar-subtitle">{meta.subtitle}</div>
      </div>
      <div className="topbar-spacer" />
      <div style={{ textAlign: 'right', marginRight: 12 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'capitalize' }}>{dateStr}</div>
      </div>
      <div className="topbar-clock">{clock}</div>
      <div className="topbar-status">
        <span className="status-dot" />
        API Connectée
      </div>
    </header>
  );
}
