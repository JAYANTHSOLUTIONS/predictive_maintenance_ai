import { useState } from 'react';
import { Login } from './components/auth/Login';
import { Register } from './components/auth/Register';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { MasterDashboard } from './components/dashboard/MasterDashboard';
import { VehicleHealth } from './components/vehicle-health/VehicleHealth';
import { Scheduling } from './components/scheduling/Scheduling';
import { Manufacturing } from './components/manufacturing/Manufacturing';
import { Security } from './components/security/Security';
import { Settings } from './components/settings/Settings';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'login' | 'register' | 'dashboard'>('login');
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentScreen('dashboard');
    setCurrentPage('dashboard');
  };

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
  };

  if (!isAuthenticated) {
    if (currentScreen === 'login') {
      return <Login onLogin={handleLogin} onSwitchToRegister={() => setCurrentScreen('register')} />;
    }
    if (currentScreen === 'register') {
      return <Register onRegister={handleLogin} onSwitchToLogin={() => setCurrentScreen('login')} />;
    }
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <MasterDashboard />;
      case 'vehicle-health':
        return <VehicleHealth />;
      case 'scheduling':
        return <Scheduling />;
      case 'manufacturing':
        return <Manufacturing />;
      case 'security':
        return <Security />;
      case 'settings':
        return <Settings />;
      default:
        return <MasterDashboard />;
    }
  };

  return (
    <DashboardLayout currentPage={currentPage} onNavigate={handleNavigate}>
      {renderPage()}
    </DashboardLayout>
  );
}
