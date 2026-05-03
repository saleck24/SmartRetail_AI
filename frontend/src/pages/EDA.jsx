import React from 'react';

export default function EDA() {
  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔍 Analyse Exploratoire (EDA)</h2>
        <p className="page-subtitle">
          Visualisation des dynamiques de ventes sur le dataset Corporación Favorita (2017)
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Aperçu Global des Ventes</span>
          </div>
          <div className="card-body" style={{ textAlign: 'center' }}>
            <img 
              src="/assets_soutenance/eda_plots/01_eda_overview.png" 
              alt="EDA Overview" 
              style={{ maxWidth: '100%', borderRadius: 'var(--radius)', marginBottom: '16px' }} 
            />
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', textAlign: 'left', lineHeight: 1.6 }}>
              <strong>Légende :</strong> Ce graphique montre la répartition globale et la distribution des ventes sur l'année 2017. Il confirme la présence de données très variées (des produits très vendus à côté de produits rarement achetés), justifiant l'utilisation d'un modèle d'Intelligence Artificielle robuste pour capter toutes les nuances.
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Analyse de la Saisonnalité</span>
          </div>
          <div className="card-body" style={{ textAlign: 'center' }}>
            <img 
              src="/assets_soutenance/eda_plots/02_seasonality.png" 
              alt="Seasonality" 
              style={{ maxWidth: '100%', borderRadius: 'var(--radius)', marginBottom: '16px' }} 
            />
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', textAlign: 'left', lineHeight: 1.6 }}>
              <strong>Légende :</strong> La saisonnalité est un facteur critique dans le commerce de détail. On observe ici les pics de ventes récurrents liés aux jours de la semaine (les week-ends génèrent plus de volume) et aux mois de l'année. Ces cycles répétitifs ont été encodés pour permettre à LightGBM d'anticiper les futurs pics de demande.
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <span className="card-title">Interprétabilité du Modèle (Feature Importance - LightGBM)</span>
        </div>
        <div className="card-body" style={{ textAlign: 'center' }}>
          <img 
            src="/assets_soutenance/benchmark_plots/lgbm_feature_importance.png" 
            alt="Feature Importance" 
            style={{ maxWidth: '100%', borderRadius: 'var(--radius)', marginBottom: '16px' }} 
          />
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', textAlign: 'left', lineHeight: 1.6, maxWidth: '800px', margin: '0 auto' }}>
            <strong>Légende :</strong> Contrairement au Deep Learning qui est souvent considéré comme une "boîte noire", LightGBM est totalement interprétable. Ce graphique classe les variables qui ont eu le plus de poids dans la prise de décision de l'IA (comme l'historique des ventes récentes, les jours de promotions, etc.). Cela prouve que le modèle a parfaitement assimilé la logique métier de l'entreprise.
          </p>
        </div>
      </div>
    </div>
  );
}
