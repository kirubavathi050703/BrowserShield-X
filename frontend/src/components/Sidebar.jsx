import React from 'react';
import { 
  ShieldAlert, LayoutDashboard, Search, Eye, History, 
  Lock, FileText, BarChart3, Network, HelpCircle, Settings 
} from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'scan', label: 'Scan File', icon: Search },
  { id: 'monitor', label: 'Download Monitor', icon: Eye },
  { id: 'history', label: 'Scan History', icon: History },
  { id: 'quarantine', label: 'Quarantine Vault', icon: Lock },
  { id: 'report', label: 'Security Report', icon: FileText },
  { id: 'analytics', label: 'Model Analytics', icon: BarChart3 },
  { id: 'federated', label: 'Federated Learning', icon: Network },
  { id: 'explainability', label: 'Explainability (XAI)', icon: HelpCircle },
  { id: 'settings', label: 'System Settings', icon: Settings },
];

export default function Sidebar({ activePage, setActivePage }) {
  return (
    <aside style={{
      width: '260px',
      height: '100vh',
      position: 'fixed',
      left: 0,
      top: 0,
      background: '#0D1322',
      borderRight: '1px solid rgba(255,255,255,0.08)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 50
    }}>
      {/* Brand Header */}
      <div style={{ padding: '24px 20px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #00F0FF 0%, #3B82F6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(0, 240, 255, 0.4)'
          }}>
            <ShieldAlert size={24} color="#090D16" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFF' }}>
              Browser<span style={{ color: '#00F0FF' }}>Shield-X</span>
            </h1>
            <p style={{ fontSize: '0.7rem', color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Adaptive Multi-Layer FL
            </p>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                margin: '4px 0',
                borderRadius: '10px',
                border: 'none',
                background: isActive ? 'rgba(0, 240, 255, 0.12)' : 'transparent',
                color: isActive ? '#00F0FF' : '#9CA3AF',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                borderLeft: isActive ? '3px solid #00F0FF' : '3px solid transparent'
              }}
            >
              <Icon size={18} color={isActive ? '#00F0FF' : '#9CA3AF'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer System Version */}
      <div style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.08)', fontSize: '0.75rem', color: '#6B7280' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10B981' }}></div>
          <span>Engine Status: Online v2.0</span>
        </div>
      </div>
    </aside>
  );
}
