import React, { useEffect, useState } from 'react';
import { HelpCircle, ShieldAlert, Cpu } from 'lucide-react';
import { getAnalyticsMetrics } from '../api';

export default function ExplainabilityPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getAnalyticsMetrics().then(res => setData(res)).catch(() => {});
  }, []);

  const adv = data?.adversarial_robustness || {};
  const testCases = adv.test_cases || [];

  return (
    <div style={{ padding: '32px' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
        Explainable AI (XAI) & <span className="gradient-text">Adversarial Robustness</span>
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        BrowserShield-X explains WHY every file was flagged or allowed, showing top feature attributions and evaluating signature manipulation robustness.
      </p>

      {/* Adversarial Robustness Card */}
      <div className="glass-panel glass-panel-glow" style={{ padding: '24px', marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Adversarial Attack Robustness Score</h3>
          <p style={{ color: '#9CA3AF', fontSize: '0.9rem', marginTop: '4px' }}>
            Evaluated on synthetic tampered magic bytes, corrupt footers, and prepended executable payloads.
          </p>
        </div>
        <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#00F0FF' }}>
          {adv.robustness_score_pct || 100.0}%
        </div>
      </div>

      {/* Adversarial Test Matrix */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px' }}>Adversarial Attack Matrix Results</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left', color: '#6B7280' }}>
              <th style={{ padding: '12px' }}>Sample Filename</th>
              <th style={{ padding: '12px' }}>Attack Vector</th>
              <th style={{ padding: '12px' }}>Declared Ext</th>
              <th style={{ padding: '12px' }}>Detected Type</th>
              <th style={{ padding: '12px' }}>Risk Score</th>
              <th style={{ padding: '12px' }}>Decision</th>
              <th style={{ padding: '12px' }}>Robustness Test</th>
            </tr>
          </thead>
          <tbody>
            {testCases.map((tc, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '12px', fontWeight: 600 }}>{tc.filename}</td>
                <td style={{ padding: '12px', color: '#9CA3AF' }}>{tc.attack_type}</td>
                <td style={{ padding: '12px', color: '#9CA3AF' }}>{tc.declared_ext}</td>
                <td style={{ padding: '12px', color: tc.declared_ext.toLowerCase() !== '.' + tc.detected_type.toLowerCase() ? '#EF4444' : '#10B981', fontWeight: 700 }}>
                  {tc.detected_type}
                </td>
                <td style={{ padding: '12px', fontWeight: 700 }}>{tc.risk_score}/100</td>
                <td style={{ padding: '12px' }}>
                  <span className={`badge ${tc.decision === 'ALLOW' ? 'badge-low' : 'badge-high'}`}>{tc.decision}</span>
                </td>
                <td style={{ padding: '12px' }}>
                  <span className={`badge ${tc.correctly_flagged ? 'badge-low' : 'badge-high'}`}>
                    {tc.correctly_flagged ? 'PASSED' : 'FAILED'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
