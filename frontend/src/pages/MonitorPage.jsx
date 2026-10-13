import React, { useEffect, useState } from 'react';
import { Eye, EyeOff, FolderCheck, RefreshCw, AlertCircle } from 'lucide-react';
import { getMonitorStatus, startMonitor, stopMonitor } from '../api';

export default function MonitorPage() {
  const [status, setStatus] = useState({ is_active: false, watch_directory: '' });
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await getMonitorStatus();
      setStatus(data);
    } catch (err) {}
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleToggle = async () => {
    setLoading(true);
    try {
      if (status.is_active) {
        await stopMonitor();
      } else {
        await startMonitor();
      }
      await fetchStatus();
    } catch (err) {}
    setLoading(false);
  };

  return (
    <div style={{ padding: '32px' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
        Point-of-Download <span className="gradient-text">Watcher Service</span>
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        Automatic background monitoring of your downloads directory. Transient files (.crdownload, .part, .tmp) are ignored; stable completed files are scanned instantly and isolated if dangerous.
      </p>

      {/* Monitor Status Card */}
      <div className="glass-panel glass-panel-glow" style={{ padding: '32px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '16px',
              background: status.is_active ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: status.is_active ? '1px solid #10B981' : '1px solid #EF4444'
            }}>
              {status.is_active ? <Eye size={32} color="#10B981" /> : <EyeOff size={32} color="#EF4444" />}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800 }}>
                  Watcher Status: {status.is_active ? 'ACTIVE & PROTECTING' : 'STOPPED'}
                </h3>
                <span className={`badge ${status.is_active ? 'badge-low' : 'badge-high'}`}>
                  {status.is_active ? 'RUNNING' : 'DISABLED'}
                </span>
              </div>
              <p style={{ color: '#9CA3AF', fontSize: '0.9rem', marginTop: '4px', fontFamily: 'monospace' }}>
                Monitored Directory: {status.watch_directory || 'Initializing...'}
              </p>
            </div>
          </div>

          <button className={status.is_active ? 'btn-danger' : 'btn-primary'} onClick={handleToggle} disabled={loading} style={{ padding: '12px 24px' }}>
            {status.is_active ? 'Stop Download Watcher' : 'Start Download Watcher'}
          </button>
        </div>
      </div>

      {/* Workflow Explanation */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px' }}>Point-of-Download Workflow</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', textAlign: 'center', fontSize: '0.85rem' }}>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ fontWeight: 700, color: '#00F0FF', marginBottom: '4px' }}>1. Download Trigger</div>
            <div style={{ color: '#9CA3AF' }}>User downloads file in browser</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ fontWeight: 700, color: '#00F0FF', marginBottom: '4px' }}>2. Stability Check</div>
            <div style={{ color: '#9CA3AF' }}>Filter .crdownload & verify file write</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ fontWeight: 700, color: '#00F0FF', marginBottom: '4px' }}>3. 7-Layer Scan</div>
            <div style={{ color: '#9CA3AF' }}>Extract 42 features & rule audit</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ fontWeight: 700, color: '#00F0FF', marginBottom: '4px' }}>4. Risk Scoring</div>
            <div style={{ color: '#9CA3AF' }}>Compute 0-100 score & decision</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '10px' }}>
            <div style={{ fontWeight: 700, color: '#10B981', marginBottom: '4px' }}>5. Quarantine / Allow</div>
            <div style={{ color: '#9CA3AF' }}>Auto-isolate if risk &ge; 60</div>
          </div>
        </div>
      </div>
    </div>
  );
}
