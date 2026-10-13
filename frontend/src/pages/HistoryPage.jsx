import React, { useEffect, useState } from 'react';
import { History, Search, FileText, Filter } from 'lucide-react';
import { getScanHistory } from '../api';

export default function HistoryPage({ onSelectReport, setActivePage }) {
  const [scans, setScans] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDecision, setFilterDecision] = useState('ALL');

  useEffect(() => {
    getScanHistory(200).then(data => setScans(data.scans || [])).catch(() => {});
  }, []);

  const filtered = scans.filter(s => {
    const matchSearch = s.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        s.declared_extension.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        s.detected_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchFilter = filterDecision === 'ALL' || s.decision === filterDecision;
    return matchSearch && matchFilter;
  });

  return (
    <div style={{ padding: '32px' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
        Scan <span className="gradient-text">History & Audit Logs</span>
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        Persistent audit log of all scanned files, risk evaluations, decision reasons, and SHA-256 integrity hashes.
      </p>

      {/* Filter Controls */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={18} color="#9CA3AF" style={{ position: 'absolute', left: '16px', top: '14px' }} />
          <input
            type="text"
            placeholder="Search by filename, extension, or detected type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px 12px 48px',
              borderRadius: '10px',
              border: '1px solid rgba(255,255,255,0.08)',
              background: 'rgba(17, 24, 39, 0.75)',
              color: '#FFF',
              fontSize: '0.9rem'
            }}
          />
        </div>

        <select
          value={filterDecision}
          onChange={(e) => setFilterDecision(e.target.value)}
          style={{
            padding: '12px 16px',
            borderRadius: '10px',
            border: '1px solid rgba(255,255,255,0.08)',
            background: '#111827',
            color: '#FFF',
            fontSize: '0.9rem'
          }}
        >
          <option value="ALL">All Decisions</option>
          <option value="ALLOW">ALLOW Only</option>
          <option value="REVIEW">REVIEW Only</option>
          <option value="BLOCK">BLOCK Only</option>
        </select>
      </div>

      {/* Scan History Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left', color: '#6B7280' }}>
              <th style={{ padding: '12px' }}>Timestamp</th>
              <th style={{ padding: '12px' }}>Filename</th>
              <th style={{ padding: '12px' }}>Declared Ext</th>
              <th style={{ padding: '12px' }}>Detected Content</th>
              <th style={{ padding: '12px' }}>Risk Score</th>
              <th style={{ padding: '12px' }}>Decision</th>
              <th style={{ padding: '12px' }}>Source</th>
              <th style={{ padding: '12px', textAlign: 'right' }}>Report</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '12px', color: '#9CA3AF', fontSize: '0.8rem', fontFamily: 'monospace' }}>
                  {new Date(s.timestamp).toLocaleTimeString()}
                </td>
                <td style={{ padding: '12px', fontWeight: 600 }}>{s.filename}</td>
                <td style={{ padding: '12px', color: '#9CA3AF' }}>{s.declared_extension}</td>
                <td style={{ padding: '12px', color: s.declared_extension.toLowerCase() !== '.' + s.detected_type.toLowerCase() ? '#EF4444' : '#10B981', fontWeight: 700 }}>
                  {s.detected_type}
                </td>
                <td style={{ padding: '12px', fontWeight: 700 }}>{s.risk_score}/100</td>
                <td style={{ padding: '12px' }}>
                  <span className={`badge ${s.decision === 'ALLOW' ? 'badge-low' : s.decision === 'REVIEW' ? 'badge-medium' : 'badge-high'}`}>
                    {s.decision}
                  </span>
                </td>
                <td style={{ padding: '12px', color: '#9CA3AF', fontSize: '0.8rem' }}>{s.scanned_from}</td>
                <td style={{ padding: '12px', textAlign: 'right' }}>
                  <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => { onSelectReport(s); setActivePage('report'); }}>
                    Inspect
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
