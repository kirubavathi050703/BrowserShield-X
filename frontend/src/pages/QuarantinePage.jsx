import React, { useEffect, useState } from 'react';
import { Lock, Unlock, Trash2, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { getQuarantinedFiles, restoreQuarantinedFile, deleteQuarantinedFile } from '../api';

export default function QuarantinePage() {
  const [records, setRecords] = useState([]);
  const [msg, setMsg] = useState(null);

  const fetchRecords = async () => {
    try {
      const data = await getQuarantinedFiles();
      setRecords(data.records || []);
    } catch (err) {}
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleRestore = async (id) => {
    try {
      await restoreQuarantinedFile(id);
      setMsg({ type: 'success', text: `File ${id} successfully restored.` });
      fetchRecords();
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to restore file.' });
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteQuarantinedFile(id);
      setMsg({ type: 'success', text: `File ${id} permanently deleted.` });
      fetchRecords();
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to delete file.' });
    }
  };

  return (
    <div style={{ padding: '32px' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
        Quarantine <span className="gradient-text">Vault Storage</span>
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        High-risk files (risk score &ge; 60) are stripped of executable permissions and isolated safely in restricted vault storage.
      </p>

      {msg && (
        <div className="glass-panel" style={{ padding: '16px', marginBottom: '24px', borderColor: msg.type === 'success' ? '#10B981' : '#EF4444', color: msg.type === 'success' ? '#6EE7B7' : '#FCA5A5' }}>
          {msg.text}
        </div>
      )}

      <div className="glass-panel" style={{ padding: '24px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left', color: '#6B7280' }}>
              <th style={{ padding: '12px' }}>Original Filename</th>
              <th style={{ padding: '12px' }}>Detected Type</th>
              <th style={{ padding: '12px' }}>Risk Score</th>
              <th style={{ padding: '12px' }}>Status</th>
              <th style={{ padding: '12px' }}>SHA-256 Hash</th>
              <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map((rec, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '12px', fontWeight: 600 }}>{rec.filename}</td>
                <td style={{ padding: '12px', color: '#EF4444', fontWeight: 700 }}>{rec.detected_type}</td>
                <td style={{ padding: '12px', fontWeight: 700 }}>{rec.risk_score}/100</td>
                <td style={{ padding: '12px' }}>
                  <span className={`badge ${rec.status === 'quarantined' ? 'badge-critical' : rec.status === 'restored' ? 'badge-low' : 'badge-high'}`}>
                    {rec.status}
                  </span>
                </td>
                <td style={{ padding: '12px', fontSize: '0.75rem', fontFamily: 'monospace', color: '#9CA3AF' }}>
                  {rec.sha256_hash ? rec.sha256_hash.substring(0, 16) + '...' : 'N/A'}
                </td>
                <td style={{ padding: '12px', textAlign: 'right' }}>
                  {rec.status === 'quarantined' && (
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                      <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleRestore(rec.quarantine_id)}>
                        <Unlock size={14} />
                        <span>Restore</span>
                      </button>
                      <button className="btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleDelete(rec.quarantine_id)}>
                        <Trash2 size={14} />
                        <span>Delete</span>
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
