import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Brain, Eye, Calendar, ShieldCheck, MessageSquare, Wrench } from 'lucide-react';


const agents = [
  { name: 'Master Agent', status: 'active', icon: Brain, color: 'text-purple-600', bgColor: 'bg-purple-100' },
  { name: 'Monitoring Agent', status: 'scanning', icon: Eye, color: 'text-blue-600', bgColor: 'bg-blue-100', activity: 'Scanning Live Data' },
  { name: 'Diagnosis Agent', status: 'active', icon: Wrench, color: 'text-green-600', bgColor: 'bg-green-100', activity: 'Analyzing Vehicle Health' },
  { name: 'Scheduling Agent', status: 'optimizing', icon: Calendar, color: 'text-orange-600', bgColor: 'bg-orange-100', activity: 'Optimizing Slots' },
  { name: 'Customer Engagement Agent', status: 'active', icon: MessageSquare, color: 'text-pink-600', bgColor: 'bg-pink-100', activity: 'Managing Interactions' },
  { name: 'Security Agent (UEBA)', status: 'monitoring', icon: ShieldCheck, color: 'text-red-600', bgColor: 'bg-red-100', activity: 'Monitoring Behavior' },
];

export function AgentStatusWidget() {
  return (
    <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            <span>AI Agent Orchestration Status</span>
          </div>
          <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
            All Systems Operational
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => {
            const Icon = agent.icon;
            return (
              <div
                key={agent.name}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <div className={`${agent.bgColor} ${agent.color} w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm mb-1">{agent.name}</h3>
                    {agent.activity && (
                      <p className="text-xs text-slate-400">{agent.activity}</p>
                    )}
                    <div className="mt-2 flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-xs text-green-400 capitalize">{agent.status}</span>
                    </div>
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
