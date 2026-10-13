import React, { useEffect, useState } from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Eye, ArrowUpRight, Cpu, HardDrive } from 'lucide-react';
import { getScanHistory, getAnalyticsMetrics } from '../api';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, AreaChart, Area, XAxis, YAxis } from 'recharts';

export default function DashboardPage({ setActivePage, onSelectReport }) {
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    getScanHistory(50).then(data => setHistory(data.scans || [])).catch(() => {});
    getAnalyticsMetrics().then(data => setAnalytics(data)).catch(() => {});
  }, []);

  const totalScanned = history.length;
  const allowedCount = history.filter(s => s.decision === 'ALLOW').length;
  const reviewCount = history.filter(s => s.decision === 'REVIEW').length;
  const blockedCount = history.filter(s => s.decision === 'BLOCK' || s.decision === 'QUARANTINE').length;
  const avgRisk = totalScanned > 0 ? (history.reduce((acc, s) => acc + s.risk_score, 0) / totalScanned).toFixed(1) : 0;

  const pieData = [
    { name: 'Allowed', value: allowedCount || 1, color: '#10B981' },
    { name: 'Review', value: reviewCount || 0, color: '#F59E0B' },
    { name: 'Blocked', value: blockedCount || 1, color: '#EF4444' }
  ];

  return (
    <div style={{ padding: '32px' }}>
      {/* Hero Banner */}
      <div className="glass-panel glass-panel-glow" style={{ padding: '28px', marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
            Multi-Layer File Security & <span className="gradient-text">Federated Intelligence</span>
          </h2>
          <p style={{ color: '#9CA3AF', maxWidth: '650px', fontSize: '0.95rem' }}>
            BrowserShield-X protects your system immediately after download completion using 7 independent content verification layers, SHAP explainability, and privacy-preserving federated models.
          </p>
        </div>
        <button className="btn-primary" onClick={() => setActivePage('scan')}>
          <span>Upload & Scan File</span>
          <ArrowUpRight size={18} />
        </button>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '28px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#9CA3AF', fontWeight: 500 }}>Total Scanned</span>
            <Eye size={20} color="#00F0FF" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800 }}>{totalScanned}</div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', marginTop: '4px' }}>Real-Time Monitored</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#9CA3AF', fontWeight: 500 }}>Files Allowed</span>
            <ShieldCheck size={20} color="#10B981" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10B981' }}>{allowedCount}</div>
          <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginTop: '4px' }}>Verified Legitimate</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#9CA3AF', fontWeight: 500 }}>Threats Blocked</span>
            <ShieldAlert size={20} color="#EF4444" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#EF4444' }}>{blockedCount}</div>
          <div style={{ fontSize: '0.75rem', color: '#EF4444', marginTop: '4px' }}>Spoof / Quarantined</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#9CA3AF', fontWeight: 500 }}>Average Risk Score</span>
            <AlertTriangle size={20} color="#F59E0B" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: avgRisk >= 60 ? '#EF4444' : '#F59E0B' }}>{avgRisk}<span style={{ fontSize: '1rem', color: '#9CA3AF' }}>/100</span></div>
          <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginTop: '4px' }}>Multi-Factor Weighted</div>
        </div>
      </div>

      {/* Analytics & Distribution Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '28px' }}>
        {/* Risk Trend Chart */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '20px' }}>Scan Activity & Risk Score Distribution</h3>
          <div style={{ width: '100%', height: '240px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history.slice(0, 15).reverse()}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00F0FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="filename" stroke="#6B7280" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6B7280" domain={[0, 100]} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="risk_score" stroke="#00F0FF" fillOpacity={1} fill="url(#riskGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Security Decisions Donut */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px' }}>Decision Ratio</h3>
          <div style={{ width: '100%', height: '180px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: '#9CA3AF', marginTop: '12px' }}>
            <span style={{ color: '#10B981' }}>● Allow ({allowedCount})</span>
            <span style={{ color: '#F59E0B' }}>● Review ({reviewCount})</span>
            <span style={{ color: '#EF4444' }}>● Block ({blockedCount})</span>
          </div>
        </div>
      </div>

      {/* Recent Threats Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Recent Scanned Downloads</h3>
          <button className="btn-secondary" onClick={() => setActivePage('history')}>View Full History</button>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left', color: '#6B7280' }}>
              <th style={{ padding: '12px' }}>File Name</th>
              <th style={{ padding: '12px' }}>Declared</th>
              <th style={{ padding: '12px' }}>Detected Content</th>
              <th style={{ padding: '12px' }}>Risk Score</th>
              <th style={{ padding: '12px' }}>Decision</th>
              <th style={{ padding: '12px', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {history.slice(0, 5).map((scan, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '12px', fontWeight: 500 }}>{scan.filename}</td>
                <td style={{ padding: '12px', color: '#9CA3AF' }}>{scan.declared_extension}</td>
                <td style={{ padding: '12px', color: scan.declared_extension.toLowerCase() !== '.' + scan.detected_type.toLowerCase() ? '#EF4444' : '#10B981', fontWeight: 600 }}>
                  {scan.detected_type}
                </td>
                <td style={{ padding: '12px', fontWeight: 700 }}>{scan.risk_score}/100</td>
                <td style={{ padding: '12px' }}>
                  <span className={`badge ${scan.decision === 'ALLOW' ? 'badge-low' : scan.decision === 'REVIEW' ? 'badge-medium' : 'badge-high'}`}>
                    {scan.decision}
                  </span>
                </td>
                <td style={{ padding: '12px', textAlign: 'right' }}>
                  <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => { onSelectReport(scan); setActivePage('report'); }}>
                    Inspect Report
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
