import { useState, useEffect } from 'react';
import { X, Play, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// ✅ FIXED IMPORTS: Now importing the Interfaces along with 'api'
import { api, TelematicsData, AnalysisResult } from '../../services/api';

interface VehicleDetailPanelProps {
  vehicleId: string;
  onClose: () => void;
}

export function VehicleDetailPanel({ vehicleId, onClose }: VehicleDetailPanelProps) {
  // 1. STATE MANAGEMENT
  const [telematics, setTelematics] = useState<TelematicsData | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]); 

  // 2. LIVE DATA FETCHING & GRAPH UPDATE
  useEffect(() => {
    const fetchData = async () => {
      const data = await api.getTelematics(vehicleId);
      if (data) {
        setTelematics(data);
        
        // Add new point to graph
        setChartData(prev => {
          const newPoint = {
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            engineTemp: data.engine_temp_c,
            oilPressure: data.oil_pressure_psi,
            rpm: data.rpm
          };
          // Keep only last 10 points to keep graph clean
          const newHistory = [...prev, newPoint];
          return newHistory.slice(-10);
        });
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [vehicleId]);

  // 3. AI DIAGNOSIS ACTION
  const handleRunAI = async () => {
    setLoading(true);
    try {
        const result = await api.runPrediction(vehicleId);
        setAnalysis(result);
    } catch (e) {
        console.error("AI Error", e);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-2/3 lg:w-1/2 bg-white shadow-2xl z-50 overflow-y-auto border-l border-slate-200">
      <div className="p-6">
        
        {/* HEADER */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-1">Vehicle Detail</h2>
            <div className="flex items-center gap-2">
                <span className="text-slate-600 font-mono bg-slate-100 px-2 py-1 rounded">{vehicleId}</span>
                <Badge variant={telematics ? "default" : "secondary"}>
                    {telematics ? "🟢 Live IoT Connected" : "⚫ Offline"}
                </Badge>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="space-y-6">
          
          {/* VEHICLE INFO */}
          <Card>
            <CardHeader>
              <CardTitle>Vehicle Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-slate-500">Model</p>
                <p className="font-medium">HeavyHaul X5</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">Last Service</p>
                <p className="font-medium">15 Nov 2025</p>
              </div>
            </CardContent>
          </Card>

          {/* AI ACTION BUTTON */}
          {!analysis && (
              <Card className="bg-blue-50 border-blue-100">
                  <CardContent className="pt-6">
                      <div className="text-center">
                          <h3 className="text-lg font-semibold text-blue-900 mb-2">Ready for Diagnostics</h3>
                          <p className="text-blue-700 mb-4 text-sm">Analyze real-time sensor data to detect anomalies.</p>
                          <Button onClick={handleRunAI} disabled={loading} className="w-full">
                            {loading ? "Running Neural Network..." : "Run AI Diagnostics"} 
                            {!loading && <Play className="w-4 h-4 ml-2" />}
                          </Button>
                      </div>
                  </CardContent>
              </Card>
          )}

          {/* AI RESULTS (Only show if analysis exists) */}
          {analysis && (
            <Card className={analysis.risk_level === 'CRITICAL' ? "border-red-200 bg-red-50" : "border-green-200 bg-green-50"}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>AI Diagnostics Report</CardTitle>
                  <Badge variant={analysis.risk_level === 'CRITICAL' ? "destructive" : "default"}>
                    {analysis.risk_level} - {analysis.risk_score}% Risk
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-1">Diagnosis Agent Analysis</h3>
                  <p className="text-sm text-slate-700 whitespace-pre-line">
                    {analysis.diagnosis}
                  </p>
                </div>
                
                {/* UEBA Security Alert */}
                {analysis.ueba_alerts.length > 0 && (
                    <div className="bg-red-900/10 border border-red-500/50 p-3 rounded text-red-800 text-sm">
                        <div className="font-bold flex items-center gap-2">
                             <AlertTriangle className="w-4 h-4"/> Security Alert (UEBA)
                        </div>
                        {analysis.ueba_alerts[0].message}
                    </div>
                )}
                
                {/* Manufacturing Insights */}
                {analysis.manufacturing_insights && (
                    <>
                        <Separator className="bg-slate-300"/>
                        <div>
                            <h3 className="font-semibold mb-1">🏭 Factory Engineering Feedback</h3>
                            <p className="text-sm text-slate-700">{analysis.manufacturing_insights}</p>
                        </div>
                    </>
                )}
              </CardContent>
            </Card>
          )}

          {/* LIVE SENSOR GRAPHS */}
          <Card>
            <CardHeader>
              <CardTitle>Real-Time Telematics (Live Stream)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="engineTemp" stroke="#ef4444" name="Temp (°C)" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="oilPressure" stroke="#f59e0b" name="Oil (PSI)" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
              </div>
              
              {/* LIVE METRIC CARDS */}
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                  <p className="text-xs text-slate-600">Engine Temp</p>
                  <p className="text-2xl font-bold text-red-600">{telematics?.engine_temp_c ?? '--'}°C</p>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
                  <p className="text-xs text-slate-600">Oil Pressure</p>
                  <p className="text-2xl font-bold text-amber-600">{telematics?.oil_pressure_psi ?? '--'} PSI</p>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                  <p className="text-xs text-slate-600">RPM</p>
                  <p className="text-2xl font-bold text-blue-600">{telematics?.rpm ?? '--'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          {analysis && (
              <div className="flex space-x-3 pb-6">
                <Button className="flex-1 bg-green-600 hover:bg-green-700">
                    <CheckCircle className="w-4 h-4 mr-2"/> 
                    {analysis.booking_id ? "Service Confirmed" : "Book Service"}
                </Button>
                <Button variant="outline" className="flex-1">Contact Owner</Button>
              </div>
          )}
        </div>
      </div>
    </div>
  );
}