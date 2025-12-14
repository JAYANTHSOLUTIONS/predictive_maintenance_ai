import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Wrench, Phone, Calendar, Shield, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { ActivityLog, api } from '../../services/api';

export function ActivityFeed() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    // Only set loading on initial fetch
    if (logs.length === 0) setLoading(true);
    const data = await api.getAgentActivity();
    if (data) setLogs(data.reverse()); // Show newest first
    setLoading(false);
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  // Helper to map API types to Icons and Colors
  const getIconAndColor = (type: string, agent: string) => {
    if (agent.includes('Diagnosis')) return { icon: Wrench, color: 'text-green-600', bg: 'bg-green-100' };
    if (agent.includes('Risk')) return { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100' };
    if (agent.includes('Scheduling')) return { icon: Calendar, color: 'text-purple-600', bg: 'bg-purple-100' };
    if (agent.includes('Customer')) return { icon: Phone, color: 'text-blue-600', bg: 'bg-blue-100' };
    return { icon: CheckCircle, color: 'text-slate-600', bg: 'bg-slate-100' };
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Real-Time Activity Feed</CardTitle>
          <div className="flex items-center gap-2">
            <RefreshCw className={`w-3 h-3 text-slate-400 ${loading ? 'animate-spin' : ''}`} />
            <Badge variant="secondary" className="animate-pulse">Live</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-3">
            {logs.length === 0 ? (
                <div className="text-center py-10 text-slate-400">
                    <p>No activity detected yet.</p>
                    <p className="text-xs">Run diagnostics to generate logs.</p>
                </div>
            ) : (
                logs.map((activity, index) => {
                const style = getIconAndColor(activity.type, activity.agent);
                const Icon = style.icon;
                return (
                    <div
                    key={`${activity.id}-${index}`}
                    className="flex items-start space-x-3 p-3 rounded-lg hover:bg-slate-50 transition-colors border border-slate-100"
                    >
                    <div className={`${style.bg} ${style.color} w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0`}>
                        <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-bold text-slate-800">{activity.agent}</span>
                        <span className="text-xs text-slate-500 font-mono">{activity.time}</span>
                        </div>
                        <p className="text-sm text-slate-700 leading-snug">
                        {activity.message}
                        </p>
                        {activity.vehicle_id && (
                            <p className="text-xs text-slate-500 mt-1 font-mono bg-slate-50 inline-block px-1 rounded">
                                → {activity.vehicle_id}
                            </p>
                        )}
                    </div>
                    </div>
                );
                })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}