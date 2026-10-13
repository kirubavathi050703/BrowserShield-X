import React, { useEffect, useState } from 'react';
import { Settings, Save, CheckCircle2, AlertCircle } from 'lucide-react';
import { getSystemSettings, updateRiskWeights } from '../api';

export default function SettingsPage() {
  const [weights, setWeights] = useState({
    rule_engine: 0.35,
    ml_prediction: 0.35,
    structural_anomaly: 0.15,
    mime_mismatch: 0.15
  });
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSystemSettings().then(data => {
      if (data.risk_weights) setWeights(data.risk_weights);
    }).catch(() => {});
  }, []);

  const handleChange = (key, val) => {
    setWeights(prev => ({ ...prev, [key]: parseFloat(val) || 0 }));
  };

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);

  const handleSave = async () => {
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      setMsg({ type: 'error', text: `Sum of weights must equal 1.0 (Current sum: ${totalWeight.toFixed(2)})` });
      return;
    }
    setLoading(true);
    try {
      await updateRiskWeights(weights);
      setMsg({ type: 'success', text: 'Risk scoring weights updated successfully!' });
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update settings.' });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '32px' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
        System & <span className="gradient-text">Risk Engine Configuration</span>
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        Customize dynamic risk scoring weights and system thresholds. All weights must sum to 1.0.
      </p>

      {msg && (
        <div className="glass-panel" style={{ padding: '16px', marginBottom: '24px', borderColor: msg.type === 'success' ? '#10B981' : '#EF4444', color: msg.type === 'success' ? '#6EE7B7' : '#FCA5A5' }}>
          {msg.text}
        </div>
      )}

      {/* Config Form */}
      <div className="glass-panel" style={{ padding: '32px', maxWidth: '650px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '20px' }}>Dynamic Risk Weight Fusion</h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '28px' }}>
          <div>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: '#F9FAFB', display: 'block', marginBottom: '6px' }}>
              Deterministic Rule Engine Weight
            </label>
            <input 
              type="number" 
              step="0.05" 
              min="0" 
              max="1" 
              value={weights.rule_engine} 
              onChange={(e) => handleChange('rule_engine', e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#111827', border: '1px solid rgba(255,255,255,0.1)', color: '#FFF' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: '#F9FAFB', display: 'block', marginBottom: '6px' }}>
              Machine Learning Classifier Probability Weight
            </label>
            <input 
              type="number" 
              step="0.05" 
              min="0" 
              max="1" 
              value={weights.ml_prediction} 
              onChange={(e) => handleChange('ml_prediction', e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#111827', border: '1px solid rgba(255,255,255,0.1)', color: '#FFF' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: '#F9FAFB', display: 'block', marginBottom: '6px' }}>
              Structural Anomaly Weight
            </label>
            <input 
              type="number" 
              step="0.05" 
              min="0" 
              max="1" 
              value={weights.structural_anomaly} 
              onChange={(e) => handleChange('structural_anomaly', e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#111827', border: '1px solid rgba(255,255,255,0.1)', color: '#FFF' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: '#F9FAFB', display: 'block', marginBottom: '6px' }}>
              MIME Discrepancy Weight
            </label>
            <input 
              type="number" 
              step="0.05" 
              min="0" 
              max="1" 
              value={weights.mime_mismatch} 
              onChange={(e) => handleChange('mime_mismatch', e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#111827', border: '1px solid rgba(255,255,255,0.1)', color: '#FFF' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem', color: totalWeight === 1.0 ? '#10B981' : '#EF4444', fontWeight: 600 }}>
            Total Weight Sum: {totalWeight.toFixed(2)} / 1.00
          </span>
          <button className="btn-primary" onClick={handleSave} disabled={loading}>
            <Save size={16} />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
}
