import { useState, useEffect, useRef, useCallback } from 'react';
import { X, Play, AlertTriangle, CheckCircle, Activity, Thermometer, Droplets, Gauge, Download, Zap } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import ReactMarkdown from 'react-markdown'; 

import { api, TelematicsData, AnalysisResult } from '../../services/api';
import { ServiceBookingModal } from './ServiceBookingModal';

interface VehicleDetailPanelProps {
  vehicleId: string;
  onClose: () => void;
}

export function VehicleDetailPanel({ vehicleId, onClose }: VehicleDetailPanelProps) {
  // --- 1. STATE ---
  const [telematics, setTelematics] = useState<TelematicsData | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]); 
  const [showBooking, setShowBooking] = useState(false);
  
  // Ref to prevent infinite loops during auto-trigger
  const hasAutoRun = useRef(false);

  // --- 2. AI RUNNER ---
  const handleRunAI = useCallback(async (auto = false) => {
    if (loading) return; 
    setLoading(true);
    try {
        const result = await api.runPrediction(vehicleId);
        setAnalysis(result);
        if (auto) hasAutoRun.current = true;
    } catch (e) {
        console.error("AI Error", e);
    }
    setLoading(false);
  }, [vehicleId, loading]);

  // --- 3. DATA FETCHING LOOP (Effect 1: Only Fetches Data) ---
  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      const data = await api.getTelematics(vehicleId);
      
      if (data && isMounted) {
        setTelematics(data);
        
        // Update Chart History
        setChartData(prev => {
          const newPoint = {
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            engineTemp: data.engine_temp_c,
            oilPressure: data.oil_pressure_psi,
            battery: data.battery_voltage || 24.0, // ✅ ADDED BATTERY
            rpm: data.rpm
          };
          // Keep last 15 points for a smooth graph
          return [...prev, newPoint].slice(-15);
        });
      }
    };

    fetchData(); 
    const interval = setInterval(fetchData, 2000); 
    
    return () => {
        isMounted = false;
        clearInterval(interval);
    };
  }, [vehicleId]); // ✅ Only depends on VehicleID (Stable Loop)

  // --- 4. AUTO-TRIGGER LOGIC (Effect 2: Watches Data & Runs AI) ---
  useEffect(() => {
    if (!telematics) return;

    // Check Critical Thresholds
    const isCritical = telematics.engine_temp_c > 98 || telematics.oil_pressure_psi < 20;

    // Logic: If Critical AND No Report Yet AND Not Loading AND Haven't Auto-run yet
    if (isCritical && !analysis && !loading && !hasAutoRun.current) {
        console.log("⚠️ Critical Threshold Met! Auto-Running AI...");
        hasAutoRun.current = true; // Lock immediately
        handleRunAI(true);
    }
  }, [telematics, analysis, loading, handleRunAI]); 


  // --- 5. EXPORT FUNCTION ---
  const handleExport = () => {
    if (!analysis) return;

    const fileContent = `
VEHICLE DIAGNOSTICS REPORT
==========================
Vehicle ID: ${vehicleId}
Date: ${new Date().toLocaleString()}
Risk Level: ${analysis.risk_level} (${analysis.risk_score}%)

------------------------------------------------
AI DIAGNOSIS:
${analysis.diagnosis}

------------------------------------------------
MANUFACTURING INSIGHTS:
${analysis.manufacturing_insights || 'No engineering feedback provided.'}
    `;

    const blob = new Blob([fileContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${vehicleId}_Report_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper: Status Colors
  const getRiskColor = (level?: string) => {
      if (level === 'CRITICAL') return 'bg-red-50 border-red-200 text-red-900';
      if (level === 'HIGH') return 'bg-orange-50 border-orange-200 text-orange-900';
      return 'bg-green-50 border-green-200 text-green-900';
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-3/4 lg:w-1/2 bg-white shadow-2xl z-50 overflow-y-auto border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-300">
      
      {/* --- HEADER --- */}
      <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between sticky top-0 backdrop-blur-sm z-10">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{vehicleId}</h2>
          <div className="flex items-center gap-2 mt-1">
              <span className="text-sm text-slate-500 font-medium">HeavyHaul X5</span>
              <Separator orientation="vertical" className="h-4" />
              <Badge variant={telematics ? "default" : "secondary"} className={telematics ? "bg-green-600" : ""}>
                  {telematics ? "Online" : "Offline"}
              </Badge>
              {hasAutoRun.current && (
                  <Badge variant="destructive" className="animate-pulse">
                      ⚡ AI Auto-Intervention
                  </Badge>
              )}
          </div>
        </div>

        <div className="flex items-center gap-2">
            <Button 
                variant="outline" 
                size="sm" 
                onClick={handleExport}
                disabled={!analysis} 
                className="flex gap-2"
                title={!analysis ? "Run Diagnosis to Enable Export" : "Download Report"}
            >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Export Report</span>
            </Button>

            <Button variant="ghost" size="icon" onClick={onClose} className="hover:bg-slate-200 rounded-full">
                <X className="w-6 h-6 text-slate-500" />
            </Button>
        </div>
      </div>

      <div className="p-6 space-y-6 flex-1">
        
        {/* --- 1. LIVE SENSOR GRID --- */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* TEMP */}
            <Card className={`border-l-4 ${telematics?.engine_temp_c && telematics.engine_temp_c > 98 ? 'border-l-red-500 bg-red-50/50' : 'border-l-slate-300'}`}>
                <CardContent className="p-4 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-2 text-slate-500 mb-1">
                        <Thermometer className="w-4 h-4" /> <span className="text-xs font-semibold uppercase">Temp</span>
                    </div>
                    <span className={`text-2xl font-bold ${telematics?.engine_temp_c && telematics.engine_temp_c > 98 ? 'text-red-600' : 'text-slate-900'}`}>
                        {telematics?.engine_temp_c ?? '--'}°C
                    </span>
                </CardContent>
            </Card>

            {/* OIL */}
            <Card className={`border-l-4 ${telematics?.oil_pressure_psi && telematics.oil_pressure_psi < 20 ? 'border-l-amber-500 bg-amber-50/50' : 'border-l-slate-300'}`}>
                <CardContent className="p-4 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-2 text-slate-500 mb-1">
                        <Droplets className="w-4 h-4" /> <span className="text-xs font-semibold uppercase">Oil</span>
                    </div>
                    <span className={`text-2xl font-bold ${telematics?.oil_pressure_psi && telematics.oil_pressure_psi < 20 ? 'text-amber-600' : 'text-slate-900'}`}>
                        {telematics?.oil_pressure_psi ?? '--'} PSI
                    </span>
                </CardContent>
            </Card>

            {/* BATTERY */}
            <Card className="border-l-4 border-l-yellow-400">
                <CardContent className="p-4 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-2 text-slate-500 mb-1">
                        <Zap className="w-4 h-4 text-yellow-500 fill-yellow-500" /> <span className="text-xs font-semibold uppercase">Battery</span>
                    </div>
                    <span className="text-2xl font-bold text-slate-900">
                        {telematics?.battery_voltage ?? '--'}V
                    </span>
                </CardContent>
            </Card>

            {/* RPM */}
            <Card className="border-l-4 border-l-blue-500">
                <CardContent className="p-4 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-2 text-slate-500 mb-1">
                        <Gauge className="w-4 h-4" /> <span className="text-xs font-semibold uppercase">RPM</span>
                    </div>
                    <span className="text-2xl font-bold text-blue-900">
                        {telematics?.rpm ?? '--'}
                    </span>
                </CardContent>
            </Card>
        </div>

        {/* --- 2. MANUAL TRIGGER --- */}
        {!analysis && (
            <Card className="bg-slate-50 border-dashed border-2 border-slate-300 shadow-none">
                <CardContent className="py-8 flex flex-col items-center text-center">
                    <Activity className="w-12 h-12 text-blue-500/50 animate-pulse mb-4" />
                    <h3 className="text-lg font-semibold text-slate-700">System Monitoring Active</h3>
                    <p className="text-slate-500 text-sm max-w-sm mb-6">
                        AI monitoring is running in the background. If critical thresholds are breached, a diagnostic report will generate automatically.
                    </p>
                    <Button onClick={() => handleRunAI(false)} disabled={loading} className="w-full max-w-xs">
                        {loading ? "Analyzing..." : "Force Manual Diagnosis"} 
                        {!loading && <Play className="w-4 h-4 ml-2" />}
                    </Button>
                </CardContent>
            </Card>
        )}

        {/* --- 3. AI REPORT --- */}
        {analysis && (
          <Card className={`border shadow-sm overflow-hidden ${getRiskColor(analysis.risk_level)}`}>
            <CardHeader className="border-b border-black/5 bg-black/5 pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="bg-white p-1.5 rounded-full shadow-sm">
                        <Activity className="w-5 h-5 text-current" />
                    </div>
                    <CardTitle className="text-lg">AI Diagnostics Report</CardTitle>
                </div>
                <Badge variant={analysis.risk_level === 'CRITICAL' ? "destructive" : "outline"} className="text-sm px-3 py-1">
                  {analysis.risk_level} • {analysis.risk_score}% Risk
                </Badge>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-6 pt-6 bg-white/50">
              
              {/* Diagnosis Section */}
              <div>
                <h4 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-3">Diagnosis Agent Analysis</h4>
                <div className="text-sm text-slate-800 leading-relaxed">
                  <ReactMarkdown 
                      components={{
                          h3: ({children}) => <h3 className="text-base font-bold text-blue-900 mt-5 mb-2 flex items-center gap-2">{children}</h3>,
                          li: ({children}) => <li className="ml-4 list-disc marker:text-slate-400 mb-1 pl-1">{children}</li>,
                          strong: ({children}) => <span className="font-semibold text-slate-900 bg-slate-100 px-1 rounded">{children}</span>,
                          p: ({children}) => <p className="mb-3">{children}</p>
                      }}
                  >
                      {analysis.diagnosis || "No diagnosis details."}
                  </ReactMarkdown>
                </div>
              </div>
              
              {/* Security Alert */}
              {analysis.ueba_alerts && analysis.ueba_alerts.length > 0 && (
                  <div className="bg-red-50 border border-red-200 p-4 rounded-md flex gap-3 items-start">
                      <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <div>
                          <h5 className="font-bold text-red-900 text-sm">Security Alert (UEBA)</h5>
                          <p className="text-red-700 text-sm mt-1">
                              {analysis.ueba_alerts[0]?.message}
                          </p>
                      </div>
                  </div>
              )}
              
              {/* Manufacturing Section */}
              {analysis.manufacturing_insights && (
                  <>
                      <Separator />
                      <div>
                          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-3">🏭 Factory Engineering Feedback</h4>
                          <div className="text-sm text-slate-700 leading-relaxed">
                              <ReactMarkdown
                                  components={{
                                      h3: ({children}) => <h3 className="text-base font-bold text-indigo-900 mt-5 mb-2">{children}</h3>,
                                      li: ({children}) => <li className="ml-4 list-disc marker:text-indigo-400 mb-1 pl-1">{children}</li>,
                                      strong: ({children}) => <span className="font-semibold text-indigo-900 bg-indigo-50 px-1 rounded">{children}</span>,
                                      p: ({children}) => <p className="mb-3">{children}</p>
                                  }}
                              >
                                  {analysis.manufacturing_insights}
                              </ReactMarkdown>
                          </div>
                      </div>
                  </>
              )}
            </CardContent>
          </Card>
        )}

        {/* --- 4. REAL-TIME CHART --- */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Live Telemetry Stream</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[250px] w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="time" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} />
                    
                    {/* Left Axis for Temp/Pressure */}
                    <YAxis yAxisId="left" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} />
                    
                    {/* Right Axis for Battery Voltage */}
                    <YAxis yAxisId="right" orientation="right" domain={[20, 30]} tick={{fontSize: 12, fill: '#eab308'}} tickLine={false} axisLine={false} />

                    <Tooltip 
                        contentStyle={{backgroundColor: '#fff', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} 
                        itemStyle={{fontSize: '12px', fontWeight: 'bold'}}
                    />
                    <Legend />
                    <Line yAxisId="left" type="monotone" dataKey="engineTemp" stroke="#ef4444" name="Temp (°C)" strokeWidth={2} dot={false} />
                    <Line yAxisId="left" type="monotone" dataKey="oilPressure" stroke="#f59e0b" name="Oil (PSI)" strokeWidth={2} dot={false} />
                    <Line yAxisId="right" type="monotone" dataKey="battery" stroke="#eab308" name="Batt (V)" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* --- 5. ACTION BUTTONS --- */}
        {analysis && (
            <div className="sticky bottom-0 bg-white pt-4 pb-0 border-t mt-4 flex gap-3">
              <Button 
                  className={`flex-1 h-12 text-base shadow-lg ${analysis.booking_id ? "bg-slate-100 text-slate-500 hover:bg-slate-100 cursor-not-allowed border border-slate-200" : "bg-green-600 hover:bg-green-700 text-white"}`}
                  onClick={() => !analysis.booking_id && setShowBooking(true)}
                  disabled={!!analysis.booking_id}
              >
                  {analysis.booking_id ? <CheckCircle className="w-5 h-5 mr-2 text-green-600"/> : <CheckCircle className="w-5 h-5 mr-2"/>}
                  {analysis.booking_id ? `Service Confirmed (${analysis.booking_id})` : "Approve & Book Service"}
              </Button>
            </div>
        )}
      </div>

      {/* --- MODAL --- */}
      {showBooking && (
        <ServiceBookingModal 
            vehicleId={vehicleId} 
            onClose={() => setShowBooking(false)} 
            onSuccess={() => handleRunAI(false)} 
        />
      )}
    </div>
  );
}