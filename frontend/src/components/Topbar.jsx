import React from 'react';
import { Activity, ShieldCheck, UploadCloud } from 'lucide-react';

export default function Topbar({ onQuickScan }) {
  return (
    <header style={{
      marginLeft: '260px',
      height: '70px',
      background: 'rgba(13, 19, 34, 0.8)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 32px',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div className="badge badge-low">
          <Activity size={12} />
          <span>7-Layer Active Defense</span>
        </div>
        <span style={{ fontSize: '0.85rem', color: '#6B7280' }}>|</span>
        <div style={{ fontSize: '0.85rem', color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldCheck size={16} color="#10B981" />
          <span>Federated Learning Engine: Synchronized</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button className="btn-primary" onClick={onQuickScan}>
          <UploadCloud size={18} />
          <span>Scan New File</span>
        </button>
      </div>
    </header>
  );
}
