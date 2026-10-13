import React from 'react';

export default function RiskGauge({ score, category, decision }) {
  const getColors = (val) => {
    if (val >= 80) return { stroke: '#A855F7', bg: 'rgba(168, 85, 247, 0.1)', badge: 'badge-critical' };
    if (val >= 60) return { stroke: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)', badge: 'badge-high' };
    if (val >= 30) return { stroke: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)', badge: 'badge-medium' };
    return { stroke: '#10B981', bg: 'rgba(16, 185, 129, 0.1)', badge: 'badge-low' };
  };

  const { stroke, badge } = getColors(score);
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: '160px', height: '160px' }}>
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="12"
            fill="transparent"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={stroke}
            strokeWidth="12"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s ease', transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{ fontSize: '2rem', fontWeight: 800, color: stroke }}>{score}</span>
          <span style={{ fontSize: '0.75rem', color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Risk Score</span>
        </div>
      </div>
      <div style={{ marginTop: '12px' }}>
        <span className={`badge ${badge}`}>
          {decision}: {category} RISK
        </span>
      </div>
    </div>
  );
}
