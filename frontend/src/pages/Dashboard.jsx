import { useEffect, useState } from 'react';
import axios from 'axios';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Legend
} from 'recharts';
import KPICard from '../components/KPICard';
import AlertBadge from '../components/AlertBadge';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Données de démo renforcées (fallback si API pas encore connectée)
const DEMO_SALES = [
  { month: 'Jan', ventes: 42300, prediction: 41800 },
  { month: 'Fév', ventes: 38900, prediction: 39200 },
  { month: 'Mar', ventes: 51200, prediction: 50900 },
  { month: 'Avr', ventes: 47600, prediction: 48100 },
  { month: 'Mai', ventes: 55800, prediction: 54900 },
  { month: 'Jun', ventes: 61200, prediction: 60800 },
  { month: 'Jul', ventes: 58700, prediction: 59100 },
  { month: 'Aoû', ventes: 63400, prediction: 62800 },
];

const DEMO_ALERTS = [
  { id: 1, store: 'Magasin #12', item: 'Farine T55 (5kg)', stock: 8, predicted: 87, status: 'RUPTURE' },
  { id: 2, store: 'Magasin #7',  item: 'Huile Végétale (1L)', stock: 23, predicted: 41, status: 'FLUX_TENDU' },
  { id: 3, store: 'Magasin #3',  item: 'Sucre Blanc (1kg)', stock: 12, predicted: 65, status: 'RUPTURE' },
  { id: 4, store: 'Magasin #19', item: 'Riz Basmati (5kg)', stock: 54, predicted: 38, status: 'SUFFISANT' },
  { id: 5, store: 'Magasin #5',  item: 'Eau Minérale (6x1.5L)', stock: 30, predicted: 48, status: 'FLUX_TENDU' },
];

const DEMO_KPIS = {
  total_sales: 418700,
  rupture_count: 3,
  rupture_rate: 12.4,
  model_accuracy: 91.3,
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius)', padding: '12px 16px', fontSize: 13,
    }}>
      <p style={{ fontWeight: 700, marginBottom: 6, color: 'var(--text-primary)' }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <strong>{p.value?.toLocaleString('fr-FR')}</strong>
        </p>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const [kpis, setKpis] = useState(DEMO_KPIS);
  const [salesData, setSalesData] = useState(DEMO_SALES);
  const [alerts, setAlerts] = useState(DEMO_ALERTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [kRes, aRes] = await Promise.all([
          axios.get(`${API}/kpis`),
          axios.get(`${API}/alerts`),
        ]);
        setKpis(kRes.data);
        setAlerts(aRes.data.alerts || DEMO_ALERTS);
      } catch { /* fallback démo */ }
      finally { setLoading(false); }
    };
    load();
  }, []);

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🏠 Dashboard Opérationnel</h2>
        <p className="page-subtitle">
          Surveillance en temps réel des ventes, stocks et alertes IA — Corporación Favorita · LightGBM
        </p>
      </div>

      {/* KPIs */}
      <div className="kpi-grid">
        <KPICard
          label="Volume de Ventes"
          value={kpis.total_sales}
          unit=" unités"
          icon="📈"
          gradient="linear-gradient(90deg,#06B6D4,#3B82F6)"
          glowColor="rgba(6,182,212,0.08)"
          trend={8.4}
          trendLabel="vs mois précédent"
        />
        <KPICard
          label="Alertes Rupture"
          value={kpis.rupture_count}
          unit=" alertes"
          icon="⚠️"
          gradient="linear-gradient(90deg,#EF4444,#F59E0B)"
          glowColor="rgba(239,68,68,0.08)"
          iconBg="rgba(239,68,68,0.12)"
          trend={-2}
          trendLabel="vs hier"
        />
        <KPICard
          label="Taux de Rupture"
          value={kpis.rupture_rate}
          unit="%"
          icon="📉"
          gradient="linear-gradient(90deg,#F59E0B,#EF4444)"
          glowColor="rgba(245,158,11,0.08)"
          iconBg="rgba(245,158,11,0.12)"
          trend={-1.2}
          trendLabel="vs semaine dernière"
        />
        <KPICard
          label="Précision Modèle"
          value={kpis.model_accuracy}
          unit="%"
          icon="🤖"
          gradient="linear-gradient(90deg,#8B5CF6,#06B6D4)"
          glowColor="rgba(139,92,246,0.08)"
          iconBg="rgba(139,92,246,0.12)"
          trend={2.1}
          trendLabel="après full-training Colab"
        />
      </div>

      {/* Graphes */}
      <div className="grid-2">
        {/* Ventes vs Prédictions */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">
              <span className="card-title-icon">📊</span>
              Ventes Réelles vs Prédictions IA
            </span>
          </div>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={salesData}>
                <defs>
                  <linearGradient id="gVentes" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gPred" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, paddingTop: 12 }} />
                <Area type="monotone" dataKey="ventes" stroke="#06B6D4" strokeWidth={2.5} fill="url(#gVentes)" name="Ventes Réelles" />
                <Area type="monotone" dataKey="prediction" stroke="#8B5CF6" strokeWidth={2} strokeDasharray="5 3" fill="url(#gPred)" name="Prédictions LightGBM" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alertes récentes */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">
              <span className="card-title-icon">🚨</span>
              Alertes Rupture en Cours
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Généré par LightGBM
            </span>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {alerts.slice(0, 4).map(alert => (
                <div key={alert.id} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '10px 14px',
                  background: alert.status === 'RUPTURE'
                    ? 'rgba(239,68,68,0.06)'
                    : alert.status === 'FLUX_TENDU'
                    ? 'rgba(245,158,11,0.06)'
                    : 'rgba(16,185,129,0.06)',
                  borderRadius: 'var(--radius-sm)',
                  border: `1px solid ${alert.status === 'RUPTURE' ? 'rgba(239,68,68,0.15)' : alert.status === 'FLUX_TENDU' ? 'rgba(245,158,11,0.15)' : 'rgba(16,185,129,0.15)'}`,
                }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {alert.item}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {alert.store} · Stock: {alert.stock} · Prédit: {alert.predicted}
                    </div>
                  </div>
                  <AlertBadge status={alert.status} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Barre de santé du système */}
      <div className="card" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <span className="card-title">
            <span className="card-title-icon">🤖</span>
            État du Système IA — LightGBM (Dataset 2017 Colab)
          </span>
          <span className="badge badge-success">✓ Modèle en production</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20 }}>
          {[
            { label: 'Précision (R²)', value: 91.3, color: 'var(--cyan)' },
            { label: 'MAE (unités)', value: 9.53, max: 20, isRaw: true, color: 'var(--success)' },
            { label: 'SMAPE (%)', value: 18.2, color: 'var(--purple)' },
            { label: 'Couverture Dataset', value: 100, color: 'var(--blue)' },
          ].map(item => (
            <div key={item.label}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 12 }}>
                <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                <span style={{ fontWeight: 700, color: item.color }}>
                  {item.isRaw ? item.value : `${item.value}%`}
                </span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${item.isRaw ? (item.value / item.max) * 100 : item.value}%`,
                    background: `linear-gradient(90deg, ${item.color}, ${item.color}88)`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
