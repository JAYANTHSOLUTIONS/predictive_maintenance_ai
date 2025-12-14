import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Brain, Eye, Calendar, ShieldCheck, MessageSquare, Wrench, RefreshCw } from 'lucide-react';
import { api } from '../../services/api'; // Import API

const agentsList = [
  { name: 'Master Agent', role: 'core', icon: Brain, color: 'text-purple-400', bgColor: 'bg-purple-900/30', activity: 'Orchestrating Workflow' },
  { name: 'IoT Listener', role: 'data', icon: Eye, color: 'text-blue-400', bgColor: 'bg-blue-900/30', activity: 'Ingesting Sensor Data' },
  { name: 'Diagnosis Agent', role: 'analysis', icon: Wrench, color: 'text-green-400', bgColor: 'bg-green-900/30', activity: 'Analyzing Faults' },
  { name: 'Scheduling Agent', role: 'ops', icon: Calendar, color: 'text-orange-400', bgColor: 'bg-orange-900/30', activity: 'Optimizing Slots' },
  { name: 'Customer Agent', role: 'ops', icon: MessageSquare, color: 'text-pink-400', bgColor: 'bg-pink-900/30', activity: 'Managing Alerts' },
  { name: 'Security Agent', role: 'security', icon: ShieldCheck, color: 'text-red-400', bgColor: 'bg-red-900/30', activity: 'UEBA Monitoring' },
];

export function AgentStatusWidget() {
  const [isOnline, setIsOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check Backend Status Live
  useEffect(() => {
    const checkStatus = async () => {
      const status = await api.getSystemStatus();
      setIsOnline(!!status);
      setLoading(false);
    };
    
    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Check every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="bg-slate-900 text-white border-slate-800 shadow-xl">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span>AI Agent Cluster</span>
          </div>
          <Badge variant="outline" className={`${isOnline ? 'border-green-500 text-green-400' : 'border-red-500 text-red-400'} bg-transparent`}>
            {loading ? "CONNECTING..." : isOnline ? "SYSTEM ONLINE" : "DISCONNECTED"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agentsList.map((agent) => {
            const Icon = agent.icon;
            return (
              <div
                key={agent.name}
                className={`border border-slate-700 rounded-lg p-4 transition-all duration-300 ${isOnline ? 'hover:bg-slate-800 opacity-100' : 'opacity-50 grayscale'}`}
              >
                <div className="flex items-start space-x-3">
                  <div className={`${agent.bgColor} ${agent.color} w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-bold text-slate-200">{agent.name}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{isOnline ? agent.activity : 'Waiting for connection...'}</p>
                    
                    {isOnline && (
                      <div className="mt-3 flex items-center space-x-2">
                        <div className="h-1 w-full bg-slate-700 rounded-full overflow-hidden">
                            <div className={`h-full ${agent.color.replace('text-', 'bg-')} animate-[progress_2s_ease-in-out_infinite]`} style={{width: '60%'}}></div>
                        </div>
                        <span className="text-[10px] text-slate-400">Active</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}