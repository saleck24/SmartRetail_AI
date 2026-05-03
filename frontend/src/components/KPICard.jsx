import { useEffect, useRef, useState } from 'react';

function animateCount(from, to, duration, setter) {
  const start = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    setter(Math.round(from + (to - from) * eased));
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

export default function KPICard({ label, value, unit = '', icon, gradient, glowColor, iconBg, trend, trendLabel, prefix = '' }) {
  const [displayed, setDisplayed] = useState(0);
  const prevRef = useRef(0);

  useEffect(() => {
    const numVal = typeof value === 'number' ? value : parseFloat(value) || 0;
    animateCount(prevRef.current, numVal, 1200, setDisplayed);
    prevRef.current = numVal;
  }, [value]);

  const trendClass = trend > 0 ? 'up' : trend < 0 ? 'down' : 'neutral';
  const trendArrow = trend > 0 ? '↑' : trend < 0 ? '↓' : '→';

  return (
    <div
      className="kpi-card"
      style={{
        '--kpi-gradient': gradient || 'linear-gradient(90deg, var(--cyan), var(--blue))',
        '--kpi-glow': glowColor || 'rgba(6,182,212,0.08)',
        '--kpi-icon-bg': iconBg || 'rgba(6,182,212,0.12)',
      }}
    >
      <div className="kpi-header">
        <div className="kpi-label">{label}</div>
        <div className="kpi-icon">{icon}</div>
      </div>
      <div className="kpi-value">
        {prefix}{displayed.toLocaleString('fr-FR')}{unit}
      </div>
      {trendLabel && (
        <div className={`kpi-trend ${trendClass}`}>
          <span>{trendArrow}</span>
          <span>{Math.abs(trend)}% {trendLabel}</span>
        </div>
      )}
    </div>
  );
}
