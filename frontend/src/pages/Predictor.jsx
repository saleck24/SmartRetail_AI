import { useState } from 'react';
import axios from 'axios';
import AlertBadge from '../components/AlertBadge';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'secret-token-123';

function getStatus(stock, predicted) {
  if (predicted <= 0) return 'SUFFISANT';
  const ratio = stock / predicted;
  if (ratio < 0.2)  return 'RUPTURE';
  if (ratio < 0.7)  return 'FLUX_TENDU';
  if (ratio > 2.0)  return 'SURSTOCK';
  return 'SUFFISANT';
}

function computeRecommendation(stock, predicted) {
  const reorder = Math.max(0, predicted - stock);
  if (reorder > 0) return `Commander ${reorder} unités supplémentaires`;
  return 'Stock suffisant — aucune commande requise';
}

export default function Predictor() {
  const [form, setForm] = useState({
    date: new Date().toISOString().split('T')[0],
    store_id: 1,
    item_id: 1034,
    stock_actuel: 12,
    sales_lag_7: 45,
    sales_rolling_mean_7: 41,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(
        `${API}/predict`,
        {
          date: form.date,
          store_id: parseInt(form.store_id),
          item_id: parseInt(form.item_id),
          sales_lag_7: parseFloat(form.sales_lag_7),
          sales_rolling_mean_7: parseFloat(form.sales_rolling_mean_7),
        },
        { headers: { 'X-API-Key': API_KEY } }
      );
      const demand = res.data.expected_demand;
      const stock = parseInt(form.stock_actuel);
      setResult({
        demand,
        stock,
        status: getStatus(stock, demand),
        reorder: computeRecommendation(stock, demand),
        gap: demand - stock,
      });
    } catch (e) {
      // Mode démo si API pas connectée
      const demand = Math.round(parseFloat(form.sales_rolling_mean_7) * 1.15 + Math.random() * 10);
      const stock = parseInt(form.stock_actuel);
      setResult({
        demand,
        stock,
        status: getStatus(stock, demand),
        reorder: computeRecommendation(stock, demand),
        gap: demand - stock,
        demo: true,
      });
    }
    setLoading(false);
  };

  const statusMeta = {
    RUPTURE:    { color: 'var(--danger)',  msg: 'Risque de rupture de stock critique !', icon: '🔴' },
    FLUX_TENDU: { color: 'var(--warning)', msg: 'Stocks insuffisants — réapprovisionnement recommandé.', icon: '🟡' },
    SUFFISANT:  { color: 'var(--success)', msg: 'Stock suffisant pour la période prévue.', icon: '🟢' },
    SURSTOCK:   { color: 'var(--blue)',    msg: 'Sur-stock détecté — réduire les commandes.', icon: '🔵' },
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔮 Prédictions IA — LightGBM</h2>
        <p className="page-subtitle">
          Moteur de prédiction entraîné sur plus de 24M d'enregistrements (Corporación Favorita · Google Colab)
        </p>
      </div>

      {/* Info box */}
      <div className="alert-box info" style={{ marginBottom: 24 }}>
        <span className="alert-icon">🤖</span>
        <div>
          <div className="alert-title">Modèle LightGBM — Architecture SmartRetail_AI</div>
          <div className="alert-msg">
            Le moteur de prédiction est exposé via l'API FastAPI sécurisée (X-API-Key). 
            Le frontend envoie les features en JSON et reçoit la demande prédite en ms.
            La décision SmartRetail_AI (alerte rupture / commande) est calculée en combinant la prédiction IA et le stock physique actuel.
          </div>
        </div>
      </div>

      <div className="predictor-grid">
        {/* Formulaire */}
        <div className="card" style={{ padding: '24px' }}>
          <div className="card-title" style={{ marginBottom: 20 }}>
            <span className="card-title-icon">⚙</span>
            Paramètres de Prédiction
          </div>

          <div className="form-group">
            <label className="form-label">Date de Prédiction</label>
            <input
              type="date"
              className="form-input"
              value={form.date}
              min="2013-01-01"
              max="2017-08-16"
              onChange={e => handleChange('date', e.target.value)}
            />
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              Données Favorita : Jan 2013 → Aoû 2017
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">ID Magasin (1–54)</label>
              <input
                type="number" min="1" max="54"
                className="form-input"
                value={form.store_id}
                onChange={e => handleChange('store_id', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">ID Article</label>
              <input
                type="number" min="1"
                className="form-input"
                value={form.item_id}
                onChange={e => handleChange('item_id', e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Stock Physique Actuel (unités)</label>
            <input
              type="number" min="0"
              className="form-input"
              value={form.stock_actuel}
              onChange={e => handleChange('stock_actuel', e.target.value)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Ventes J-7 (lag)</label>
              <input
                type="number" min="0"
                className="form-input"
                value={form.sales_lag_7}
                onChange={e => handleChange('sales_lag_7', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Moy. Mobile 7j</label>
              <input
                type="number" min="0"
                className="form-input"
                value={form.sales_rolling_mean_7}
                onChange={e => handleChange('sales_rolling_mean_7', e.target.value)}
              />
            </div>
          </div>

          <button
            className="btn btn-primary btn-lg"
            style={{ width: '100%' }}
            onClick={handlePredict}
            disabled={loading}
          >
            {loading ? (
              <><span className="spinner" /> Calcul en cours...</>
            ) : (
              <> Lancer la Prédiction IA</>
            )}
          </button>
        </div>

        {/* Résultat */}
        <div className="card">
          {!result ? (
            <div className="result-panel" style={{ color: 'var(--text-muted)' }}>
              <div style={{ fontSize: 64, marginBottom: 16 }}>🎯</div>
              <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>En attente de prédiction</div>
              <div style={{ fontSize: 13 }}>Renseignez les paramètres et lancez la prédiction IA</div>
            </div>
          ) : (
            <div className="result-panel">
              {result.demo && (
                <div style={{
                  position: 'absolute', top: 12, right: 12,
                  fontSize: 10, background: 'rgba(245,158,11,0.1)',
                  color: 'var(--warning)', padding: '2px 8px', borderRadius: 99,
                  border: '1px solid rgba(245,158,11,0.2)',
                }}>MODE DÉMO</div>
              )}

              <div style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '1px' }}>
                Demande Prédite
              </div>
              <div className="result-gauge">{result.demand}</div>
              <div className="result-unit">unités attendues</div>

              <AlertBadge status={result.status} />

              <div style={{
                margin: '20px 0', padding: '16px 20px',
                background: 'rgba(255,255,255,0.03)',
                borderRadius: 'var(--radius)',
                border: '1px solid var(--border)',
                width: '100%', textAlign: 'left',
              }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                  Analyse SmartRetail_AI
                </div>
                {[
                  { label: 'Stock Actuel', value: `${result.stock} unités` },
                  { label: 'Demande Prédite', value: `${result.demand} unités`, color: 'var(--cyan)' },
                  { label: 'Écart', value: `${result.gap > 0 ? '+' : ''}${result.gap} unités`, color: result.gap > 0 ? 'var(--danger)' : 'var(--success)' },
                  { label: 'Recommandation', value: result.reorder, color: 'var(--warning)' },
                ].map(row => (
                  <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 13 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{row.label}</span>
                    <span style={{ fontWeight: 600, color: row.color || 'var(--text-primary)' }}>{row.value}</span>
                  </div>
                ))}
              </div>

              <div style={{
                background: statusMeta[result.status]?.color + '15',
                border: `1px solid ${statusMeta[result.status]?.color}30`,
                borderRadius: 'var(--radius)',
                padding: '12px 16px',
                width: '100%',
                fontSize: 13,
                color: statusMeta[result.status]?.color,
                fontWeight: 500,
                textAlign: 'left',
              }}>
                {statusMeta[result.status]?.icon} {statusMeta[result.status]?.msg}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
