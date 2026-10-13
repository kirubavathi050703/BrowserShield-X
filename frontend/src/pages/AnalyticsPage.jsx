import React, { useEffect, useState } from 'react';
import { BarChart3, RefreshCw, Cpu, Award } from 'lucide-react';
import { getAnalyticsMetrics, runExperiments } from '../api';

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const res = await getAnalyticsMetrics();
      setData(res);
    } catch (err) {}
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runExperiments();
      setData(res.summary);
    } catch (err) {}
    setLoading(false);
  };

  const models = data?.centralized_models || {};
  const ablation = data?.ablation_study || {};

  return (
    <div style={{ padding: '32px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
            Model Analytics & <span className="gradient-text">Empirical Benchmarks</span>
          </h2>
          <p style={{ color: '#9CA3AF' }}>
            Quantitative evaluation comparing Logistic Regression, Random Forest, XGBoost, and PyTorch Neural Network across accuracy, ROC-AUC, FPR, and FNR.
          </p>
        </div>
        <button className="btn-primary" onClick={handleRun} disabled={loading}>
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          <span>{loading ? 'Running Experiments...' : 'Re-Run Experiment Suite'}</span>
        </button>
      </div>

      {/* Model Benchmark Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '28px' }}>
        {['LogisticRegression', 'RandomForest', 'XGBoost', 'NeuralNetwork'].map((mName) => {
          const m = models[mName] || {};
          const isBest = models.best_model === mName;
          return (
            <div key={mName} className={`glass-panel ${isBest ? 'glass-panel-glow' : ''}`} style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ fontWeight: 700, fontSize: '1.05rem' }}>{mName}</h4>
                {isBest && <span className="badge badge-low">BEST MODEL</span>}
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: isBest ? '#00F0FF' : '#FFF', marginBottom: '16px' }}>
                {m.f1_score !== undefined ? (m.f1_score * 100).toFixed(1) + '%' : 'N/A'}
                <span style={{ fontSize: '0.75rem', color: '#9CA3AF', marginLeft: '6px' }}>F1-Score</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem', color: '#9CA3AF' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Accuracy:</span>
                  <span style={{ color: '#FFF', fontWeight: 600 }}>{m.accuracy ? (m.accuracy * 100).toFixed(1) + '%' : 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>ROC-AUC:</span>
                  <span style={{ color: '#FFF', fontWeight: 600 }}>{m.roc_auc || 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>FPR / FNR:</span>
                  <span style={{ color: '#F87171' }}>{m.fpr !== undefined ? `${(m.fpr*100).toFixed(1)}% / ${(m.fnr*100).toFixed(1)}%` : 'N/A'}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Feature Ablation Study */}
      <div className="glass-panel" style={{ padding: '28px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>7-Step Feature Ablation Study</h3>
        <p style={{ color: '#9CA3AF', fontSize: '0.85rem', marginBottom: '20px' }}>
          Evaluates incremental performance gain as detection layers are added to the model.
        </p>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left', color: '#6B7280' }}>
              <th style={{ padding: '12px' }}>Ablation Step</th>
              <th style={{ padding: '12px' }}>Features Used</th>
              <th style={{ padding: '12px' }}>Accuracy</th>
              <th style={{ padding: '12px' }}>F1-Score</th>
              <th style={{ padding: '12px' }}>ROC-AUC</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(ablation).map(([stepName, metrics]) => (
              <tr key={stepName} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '12px', fontWeight: 600, color: '#00F0FF' }}>{stepName}</td>
                <td style={{ padding: '12px' }}>{metrics.num_features_used} / 42</td>
                <td style={{ padding: '12px', fontWeight: 700 }}>{(metrics.accuracy * 100).toFixed(1)}%</td>
                <td style={{ padding: '12px', fontWeight: 700, color: '#10B981' }}>{(metrics.f1_score * 100).toFixed(1)}%</td>
                <td style={{ padding: '12px', fontWeight: 700 }}>{metrics.roc_auc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
