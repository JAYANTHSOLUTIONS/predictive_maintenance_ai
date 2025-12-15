import { useState } from 'react';
import { Search, Bell, Settings } from 'lucide-react';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { useAuth } from '../../context/AuthContext';
import { UserProfilePanel } from './UserProfilePanel';

interface HeaderProps {
  onNavigate?: (page: string) => void;
}

export function Header({ onNavigate }: HeaderProps) {
  const { user } = useAuth();
  const [profilePanelOpen, setProfilePanelOpen] = useState(false);

  const [notifications] = useState([
    { id: 1, text: 'Diagnosis Agent identified transmission issue on VIN#12345', time: '5m ago', unread: true },
    { id: 2, text: 'Scheduling Agent optimized 12 appointments', time: '15m ago', unread: true },
    { id: 3, text: 'Security Alert: Anomalous API access blocked', time: '1h ago', unread: false },
  ]);

  const unreadCount = notifications.filter((n) => n.unread).length;

  // Generate initials safely (e.g., "John Doe" -> "JD")
  const initials = user?.fullName
    ? user.fullName.split(' ').map((n) => n[0]).join('').substring(0, 2).toUpperCase()
    : 'U';

  return (
    <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 sticky top-0 z-10">
      {/* Search */}
      <div className="flex-1 max-w-2xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            type="search"
            placeholder={`Search ${user?.plant || 'data'}...`} 
            className="pl-10"
          />
        </div>
      </div>

      {/* Right Side Actions */}
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5 text-slate-600" />
              {unreadCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                >
                  {unreadCount}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {notifications.map((notification) => (
              <DropdownMenuItem key={notification.id} className="flex flex-col items-start p-3 cursor-pointer">
                <div className="flex items-start justify-between w-full">
                  <p className="text-sm pr-2 font-medium text-slate-700">{notification.text}</p>
                  {notification.unread && (
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-1 flex-shrink-0" />
                  )}
                </div>
                <span className="text-xs text-slate-500 mt-1">{notification.time}</span>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-center text-sm text-blue-600 cursor-pointer justify-center font-medium">
              View all notifications
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Settings Button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onNavigate?.('settings')}
          className="relative hover:bg-slate-100 transition-all duration-200 hover:scale-105"
          title="Settings"
        >
          <Settings className="w-5 h-5 text-slate-600" />
        </Button>

        {/* User Profile Avatar */}
        <Button
          variant="ghost"
          onClick={() => setProfilePanelOpen(true)}
          className="relative hover:bg-slate-100 p-1 rounded-full transition-all duration-200 hover:scale-105"
          title="Profile"
        >
          <Avatar className="h-10 w-10 ring-2 ring-slate-200 hover:ring-blue-500 transition-all duration-200">
            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold text-sm">
              {initials}
            </AvatarFallback>
          </Avatar>
        </Button>
      </div>

      {/* User Profile Panel */}
      <UserProfilePanel
        isOpen={profilePanelOpen}
        onClose={() => setProfilePanelOpen(false)}
      />
    </header>
  );
}