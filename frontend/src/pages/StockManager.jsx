import { useState, useEffect } from 'react';
import axios from 'axios';
import AlertBadge from '../components/AlertBadge';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const DEMO_STOCKS = [
  { id: 1,  item: 1002, name: 'Farine T55 (5kg)',         store: 12, stock: 8,   predicted: 87, family: 'Alimentation', status: 'RUPTURE' },
  { id: 2,  item: 1017, name: 'Huile Végétale (1L)',       store: 7,  stock: 23,  predicted: 41, family: 'Alimentation', status: 'FLUX_TENDU' },
  { id: 3,  item: 1034, name: 'Sucre Blanc (1kg)',          store: 3,  stock: 12,  predicted: 65, family: 'Alimentation', status: 'RUPTURE' },
  { id: 4,  item: 2001, name: 'Détergent Liquide (2L)',     store: 19, stock: 54,  predicted: 38, family: 'Ménage',       status: 'SUFFISANT' },
  { id: 5,  item: 1051, name: 'Eau Minérale (6x1.5L)',     store: 5,  stock: 30,  predicted: 48, family: 'Boissons',     status: 'FLUX_TENDU' },
  { id: 6,  item: 3011, name: 'Shampoing (500ml)',          store: 2,  stock: 90,  predicted: 25, family: 'Hygiène',      status: 'SURSTOCK' },
  { id: 7,  item: 1066, name: 'Riz Basmati (5kg)',         store: 9,  stock: 150, predicted: 72, family: 'Alimentation', status: 'SURSTOCK' },
  { id: 8,  item: 2033, name: 'Lessive Poudre (3kg)',      store: 11, stock: 18,  predicted: 34, family: 'Ménage',       status: 'FLUX_TENDU' },
  { id: 9,  item: 1089, name: 'Pâtes Spaghetti (500g)',    store: 4,  stock: 6,   predicted: 52, family: 'Alimentation', status: 'RUPTURE' },
  { id: 10, item: 4022, name: 'Savon de Ménage (250g)',    store: 8,  stock: 200, predicted: 30, family: 'Hygiène',      status: 'SURSTOCK' },
];

const FAMILIES = ['Tous', 'Alimentation', 'Ménage', 'Boissons', 'Hygiène'];
const STATUSES = ['Tous', 'RUPTURE', 'FLUX_TENDU', 'SUFFISANT', 'SURSTOCK'];

export default function StockManager() {
  const [stocks, setStocks] = useState(DEMO_STOCKS);
  const [filter, setFilter] = useState('Tous');
  const [statusFilter, setStatusFilter] = useState('Tous');
  const [search, setSearch] = useState('');

  const filtered = stocks.filter(s =>
    (filter === 'Tous' || s.family === filter) &&
    (statusFilter === 'Tous' || s.status === statusFilter) &&
    (search === '' || s.name.toLowerCase().includes(search.toLowerCase()))
  );

  const counts = {
    RUPTURE:    stocks.filter(s => s.status === 'RUPTURE').length,
    FLUX_TENDU: stocks.filter(s => s.status === 'FLUX_TENDU').length,
    SUFFISANT:  stocks.filter(s => s.status === 'SUFFISANT').length,
    SURSTOCK:   stocks.filter(s => s.status === 'SURSTOCK').length,
  };

  const coverage = (s) => {
    const pct = (s.stock / Math.max(s.predicted, 1)) * 100;
    return Math.min(pct, 100);
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">📦 Gestion des Stocks</h2>
        <p className="page-subtitle">Suivi en temps réel avec alertes intelligentes générées par le modèle LightGBM</p>
      </div>

      {/* Résumé statuts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        {[
          { key: 'RUPTURE',    label: 'Ruptures',   color: 'var(--danger)',  bg: 'var(--danger-bg)',  icon: '🔴' },
          { key: 'FLUX_TENDU', label: 'Flux Tendu', color: 'var(--warning)', bg: 'var(--warning-bg)', icon: '🟡' },
          { key: 'SUFFISANT',  label: 'Suffisant',  color: 'var(--success)', bg: 'var(--success-bg)', icon: '🟢' },
          { key: 'SURSTOCK',   label: 'Sur-Stock',  color: 'var(--blue)',    bg: 'var(--info-bg)',    icon: '🔵' },
        ].map(item => (
          <div
            key={item.key}
            className="card"
            style={{ padding: '16px 20px', cursor: 'pointer', borderColor: statusFilter === item.key ? item.color : undefined }}
            onClick={() => setStatusFilter(s => s === item.key ? 'Tous' : item.key)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 4 }}>{item.label}</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: item.color }}>{counts[item.key]}</div>
              </div>
              <div style={{ fontSize: 28 }}>{item.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="card" style={{ marginBottom: 20, padding: '16px 20px' }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <input
            className="form-input"
            style={{ maxWidth: 260 }}
            placeholder="🔍 Rechercher un produit..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <div style={{ display: 'flex', gap: 6 }}>
            {FAMILIES.map(f => (
              <button
                key={f}
                className={`btn ${filter === f ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                onClick={() => setFilter(f)}
              >{f}</button>
            ))}
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => { setFilter('Tous'); setStatusFilter('Tous'); setSearch(''); }}>
            ↺ Réinitialiser
          </button>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-muted)' }}>
            {filtered.length} produits affichés
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Produit</th>
                <th>Famille</th>
                <th>Magasin</th>
                <th>Stock Actuel</th>
                <th>Demande Prédite (IA)</th>
                <th>Couverture</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.id}>
                  <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>#{s.item}</td>
                  <td style={{ fontWeight: 600, maxWidth: 200, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {s.name}
                  </td>
                  <td>
                    <span className="badge badge-muted">{s.family}</span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>Magasin #{s.store}</td>
                  <td>
                    <span style={{
                      fontWeight: 700,
                      color: s.stock < s.predicted * 0.3 ? 'var(--danger)' : s.stock < s.predicted * 0.7 ? 'var(--warning)' : 'var(--success)'
                    }}>
                      {s.stock} unités
                    </span>
                  </td>
                  <td style={{ color: 'var(--cyan)', fontWeight: 600 }}>{s.predicted} unités</td>
                  <td style={{ minWidth: 140 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div className="progress-bar" style={{ flex: 1 }}>
                        <div
                          className="progress-fill"
                          style={{
                            width: `${coverage(s)}%`,
                            background: coverage(s) < 30
                              ? 'linear-gradient(90deg,#EF4444,#F87171)'
                              : coverage(s) < 70
                              ? 'linear-gradient(90deg,#F59E0B,#FCD34D)'
                              : 'linear-gradient(90deg,#10B981,#34D399)',
                          }}
                        />
                      </div>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', minWidth: 34 }}>{Math.round(coverage(s))}%</span>
                    </div>
                  </td>
                  <td><AlertBadge status={s.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
