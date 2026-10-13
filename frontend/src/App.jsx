import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';

import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import MonitorPage from './pages/MonitorPage';
import HistoryPage from './pages/HistoryPage';
import QuarantinePage from './pages/QuarantinePage';
import ReportPage from './pages/ReportPage';
import AnalyticsPage from './pages/AnalyticsPage';
import FederatedPage from './pages/FederatedPage';
import ExplainabilityPage from './pages/ExplainabilityPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedReport, setSelectedReport] = useState(null);

  const handleSelectReport = (reportData) => {
    setSelectedReport(reportData);
    setActivePage('report');
  };

  const renderContent = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage setActivePage={setActivePage} onSelectReport={handleSelectReport} />;
      case 'scan':
        return <ScanPage setActivePage={setActivePage} onSelectReport={handleSelectReport} />;
      case 'monitor':
        return <MonitorPage />;
      case 'history':
        return <HistoryPage setActivePage={setActivePage} onSelectReport={handleSelectReport} />;
      case 'quarantine':
        return <QuarantinePage />;
      case 'report':
        return <ReportPage report={selectedReport} setActivePage={setActivePage} />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'federated':
        return <FederatedPage />;
      case 'explainability':
        return <ExplainabilityPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <DashboardPage setActivePage={setActivePage} onSelectReport={handleSelectReport} />;
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#090D16' }}>
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Topbar onQuickScan={() => setActivePage('scan')} />
        <main style={{ marginLeft: '260px', flex: 1, overflowY: 'auto' }}>
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
