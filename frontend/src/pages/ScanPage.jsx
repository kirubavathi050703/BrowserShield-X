import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UploadCloud, CheckCircle2, AlertCircle, FileSearch, ShieldAlert, ArrowRight, Wifi, WifiOff } from 'lucide-react';
import { scanFile } from '../api';
import RiskGauge from '../components/RiskGauge';

export default function ScanPage({ onSelectReport, setActivePage }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await axios.get('http://127.0.0.1:8000/', { timeout: 2000 });
        setBackendOnline(true);
      } catch (e) {
        setBackendOnline(false);
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleScan = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const res = await scanFile(selectedFile);
      setScanResult(res);
    } catch (err) {
      if (err.message === 'Network Error' || !err.response) {
        setError('Cannot connect to scanner backend. Please make sure the Python backend server (python main.py) is running on port 8000.');
      } else {
        setError(err.response?.data?.detail || 'Scan failed. Please check file format.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
          Interactive <span className="gradient-text">File Scanner</span>
        </h2>
        <div>
          {backendOnline === true && (
            <span className="badge badge-low" style={{ fontSize: '0.8rem', padding: '6px 14px' }}>
              <Wifi size={14} style={{ marginRight: '6px' }} />
              Backend Online (Port 8000)
            </span>
          )}
          {backendOnline === false && (
            <span className="badge badge-high" style={{ fontSize: '0.8rem', padding: '6px 14px' }}>
              <WifiOff size={14} style={{ marginRight: '6px' }} />
              Backend Offline (Port 8000)
            </span>
          )}
        </div>
      </div>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        Upload any file to execute deep 7-layer verification (Magic Bytes, Footer, MIME, Entropy, Byte Histograms, and Internal Structures).
      </p>

      {backendOnline === false && (
        <div className="glass-panel" style={{ padding: '16px 20px', borderColor: '#EF4444', color: '#FCA5A5', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertCircle size={22} color="#EF4444" />
          <div>
            <strong>Python Backend is Offline:</strong> Please double-click <code>start_all.bat</code> or run <code>python main.py</code> in a terminal so the scanner can receive files.
          </div>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div 
        className="glass-panel"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        style={{
          padding: '48px',
          textAlign: 'center',
          border: '2px dashed rgba(0, 240, 255, 0.3)',
          borderRadius: '16px',
          marginBottom: '28px',
          background: 'rgba(17, 24, 39, 0.5)',
          cursor: 'pointer'
        }}
      >
        <UploadCloud size={48} color="#00F0FF" style={{ marginBottom: '16px' }} />
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px' }}>
          Drag & Drop File to Scan or Click to Browse
        </h3>
        <p style={{ color: '#6B7280', fontSize: '0.85rem', marginBottom: '20px' }}>
          Supports PDF, PNG, JPG, GIF, ZIP, DOCX, XLSX, PPTX, EXE, DLL, and unknown extensions.
        </p>

        <input 
          type="file" 
          id="fileInput" 
          onChange={handleFileChange} 
          style={{ display: 'none' }} 
        />
        <label htmlFor="fileInput" className="btn-secondary">
          Choose File
        </label>

        {selectedFile && (
          <div style={{ marginTop: '20px', fontSize: '0.95rem', color: '#00F0FF', fontWeight: 600 }}>
            Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </div>
        )}
      </div>

      {selectedFile && (
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <button className="btn-primary" onClick={handleScan} disabled={loading} style={{ padding: '12px 32px', fontSize: '1rem' }}>
            {loading ? 'Executing 7-Layer Scan...' : 'Start Multi-Layer Verification'}
          </button>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ padding: '16px', borderColor: '#EF4444', color: '#FCA5A5', marginBottom: '24px' }}>
          <AlertCircle size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
          {error}
        </div>
      )}

      {/* Scan Results Panel */}
      {scanResult && (
        <div className="glass-panel glass-panel-glow" style={{ padding: '32px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '32px', marginBottom: '32px' }}>
            {/* Risk Gauge */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderRight: '1px solid rgba(255,255,255,0.08)', paddingRight: '24px' }}>
              <RiskGauge score={scanResult.risk_score} category={scanResult.risk_category} decision={scanResult.decision} />
              <button 
                className="btn-primary" 
                style={{ marginTop: '24px' }}
                onClick={() => { onSelectReport(scanResult); setActivePage('report'); }}
              >
                <span>View Deep Report</span>
                <ArrowRight size={16} />
              </button>
            </div>

            {/* Quick Metrics */}
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px' }}>Scan Summary: {scanResult.filename}</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>Declared Extension</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700 }}>{scanResult.declared_extension}</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>Detected Content Type</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: scanResult.declared_extension.toLowerCase() !== '.' + scanResult.detected_type.toLowerCase() ? '#EF4444' : '#10B981' }}>
                    {scanResult.detected_type}
                  </div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>ML Classifier Confidence</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700 }}>{(scanResult.ml_confidence * 100).toFixed(1)}% ({scanResult.model_used})</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>Content MIME</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, fontFamily: 'monospace' }}>{scanResult.detected_mime}</div>
                </div>
              </div>

              {/* Reasons Breakdown */}
              <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>Verification Audit Reasons:</h4>
              <ul style={{ listStyle: 'none' }}>
                {scanResult.reasons.map((reason, idx) => (
                  <li key={idx} style={{
                    fontSize: '0.9rem',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    marginBottom: '8px',
                    background: reason.startsWith('✗') ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                    color: reason.startsWith('✗') ? '#FCA5A5' : '#6EE7B7',
                    borderLeft: reason.startsWith('✗') ? '3px solid #EF4444' : '3px solid #10B981'
                  }}>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
