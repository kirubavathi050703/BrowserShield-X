import React, { useState } from 'react';
import { Network, Play, ShieldCheck, Lock } from 'lucide-react';
import { simulateFL } from '../api';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function FederatedPage() {
  const [strategy, setStrategy] = useState('FedProx');
  const [rounds, setRounds] = useState(5);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await simulateFL(rounds, strategy);
      setSimulationResult(res);
    } catch (err) {}
    setLoading(false);
  };

  return (
    <div style={{ padding: '32px' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
        Federated Learning & <span className="gradient-text">Privacy Protection</span>
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px' }}>
        Multi-client Flower FL simulation comparing FedAvg and FedProx strategies under Non-IID client datasets with Gaussian Differential Privacy ($\epsilon=1.5$).
      </p>

      {/* Controls */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px', display: 'flex', gap: '24px', alignItems: 'center' }}>
        <div>
          <label style={{ fontSize: '0.85rem', color: '#9CA3AF', display: 'block', marginBottom: '6px' }}>Aggregation Strategy</label>
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)} style={{ padding: '10px 16px', borderRadius: '8px', background: '#111827', color: '#FFF', border: '1px solid rgba(255,255,255,0.1)' }}>
            <option value="FedProx">FedProx (Proximal Term - Non-IID Robust)</option>
            <option value="FedAvg">FedAvg (Standard Averaging)</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.85rem', color: '#9CA3AF', display: 'block', marginBottom: '6px' }}>FL Communication Rounds</label>
          <input type="number" min="1" max="15" value={rounds} onChange={(e) => setRounds(parseInt(e.target.value))} style={{ padding: '10px 16px', borderRadius: '8px', background: '#111827', color: '#FFF', border: '1px solid rgba(255,255,255,0.1)', width: '100px' }} />
        </div>

        <div style={{ alignSelf: 'flex-end' }}>
          <button className="btn-primary" onClick={handleSimulate} disabled={loading}>
            <Play size={16} />
            <span>{loading ? 'Running FL Simulation...' : 'Execute FL Simulation'}</span>
          </button>
        </div>
      </div>

      {/* Non-IID Clients Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '28px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h4 style={{ fontWeight: 700, color: '#00F0FF', marginBottom: '6px' }}>Client 1: PDF & Office Partition</h4>
          <p style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>85% PDF / Office files, 15% mixed. High document spoof exposure.</p>
        </div>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h4 style={{ fontWeight: 700, color: '#3B82F6', marginBottom: '6px' }}>Client 2: Image & Archive Partition</h4>
          <p style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>80% PNG/JPEG/ZIP files, 20% mixed. High archive container payload exposure.</p>
        </div>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h4 style={{ fontWeight: 700, color: '#A855F7', marginBottom: '6px' }}>Client 3: Executable & Malicious Partition</h4>
          <p style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>75% PE/Executable files, 25% mixed. High signature tamper exposure.</p>
        </div>
      </div>

      {/* Simulation Results */}
      {simulationResult && (
        <div className="glass-panel glass-panel-glow" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              FL Convergence Graph ({simulationResult.strategy})
            </h3>
            <span className="badge badge-low">
              Final Accuracy: {(simulationResult.final_accuracy * 100).toFixed(1)}%
            </span>
          </div>

          <div style={{ width: '100%', height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={simulationResult.round_history}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="round" stroke="#6B7280" />
                <YAxis stroke="#6B7280" domain={[0, 1.0]} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)' }} />
                <Line type="monotone" dataKey="accuracy" stroke="#00F0FF" strokeWidth={3} dot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
