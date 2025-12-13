import {
  LayoutDashboard,
  Activity,
  Calendar,
  Factory,
  Shield,
  Settings,
  ChevronRight,
  Cpu,
  LogOut // <--- 1. Import LogOut Icon
} from 'lucide-react';
import { cn } from '../ui/utils';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

const menuItems = [
  { id: 'dashboard', label: 'Master Dashboard', icon: LayoutDashboard },
  { id: 'vehicle-health', label: 'Vehicle Health & Predictive', icon: Activity },
  { id: 'scheduling', label: 'Service Scheduling', icon: Calendar },
  { id: 'manufacturing', label: 'Manufacturing Insights', icon: Factory },
  { id: 'security', label: 'Security & UEBA', icon: Shield },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold">AI Orchestration</h1>
            <p className="text-xs text-slate-400">Platform v2.5</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                'w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )}
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </div>
              {isActive && <ChevronRight className="w-4 h-4" />}
            </button>
          );
        })}
      </nav>

      {/* --- 2. ADDED LOGOUT BUTTON SECTION --- */}
      <div className="px-4 pb-2">
        <button
            onClick={() => onNavigate('logout')} 
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-400 hover:bg-red-950/30 hover:text-red-400 transition-colors"
        >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Sign Out</span>
        </button>
      </div>

      {/* Agent Status Indicator */}
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
            <span className="text-xs font-semibold text-slate-200">System Status</span>
          </div>
          <p className="text-xs text-slate-400">All agents operational</p>
        </div>
      </div>
    </div>
  );
}