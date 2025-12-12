import { X } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface VehicleDetailPanelProps {
  vehicleId: string;
  onClose: () => void;
}

// Mock sensor data
const sensorData = [
  { time: '10:00', engineTemp: 85, rpm: 1200, vibration: 0.8 },
  { time: '10:15', engineTemp: 88, rpm: 1800, vibration: 1.2 },
  { time: '10:30', engineTemp: 92, rpm: 2400, vibration: 1.8 },
  { time: '10:45', engineTemp: 95, rpm: 2800, vibration: 2.5 },
  { time: '11:00', engineTemp: 98, rpm: 3200, vibration: 3.2 },
  { time: '11:15', engineTemp: 101, rpm: 3600, vibration: 3.8 },
  { time: '11:30', engineTemp: 105, rpm: 4000, vibration: 4.5 },
  { time: '11:45', engineTemp: 103, rpm: 2800, vibration: 3.1 },
];

const diagnosticLogs = [
  { code: 'P0700', description: 'Transmission Control System Malfunction', severity: 'Critical', timestamp: '2025-12-12 11:42:15' },
  { code: 'P0730', description: 'Incorrect Gear Ratio', severity: 'Warning', timestamp: '2025-12-12 11:35:08' },
  { code: 'P0715', description: 'Input/Turbine Speed Sensor Circuit Malfunction', severity: 'Warning', timestamp: '2025-12-12 11:28:42' },
];

export function VehicleDetailPanel({ vehicleId, onClose }: VehicleDetailPanelProps) {
  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-2/3 lg:w-1/2 bg-white shadow-2xl z-50 overflow-y-auto">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl mb-1">Vehicle Detail</h2>
            <p className="text-slate-600 font-mono">{vehicleId}</p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="space-y-6">
          {/* Vehicle Info */}
          <Card>
            <CardHeader>
              <CardTitle>Vehicle Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-slate-600">Model</p>
                <p>Sedan X Pro</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Manufacturing Year</p>
                <p>2023</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Owner</p>
                <p>Rajesh Kumar</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Current Location</p>
                <p>Mumbai, MH</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Total Mileage</p>
                <p>42,350 km</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Last Service</p>
                <p>15 Nov 2025</p>
              </div>
            </CardContent>
          </Card>

          {/* AI Diagnostics */}
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>AI Diagnostics - Predicted Failure</CardTitle>
                <Badge variant="destructive">Critical - 92% Probability</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="mb-2">Diagnosis Agent Analysis</h3>
                <p className="text-sm text-slate-700">
                  <strong>Issue Detected:</strong> Transmission Slip - Likely cause is worn clutch plates or low transmission fluid pressure.
                </p>
              </div>
              <Separator />
              <div>
                <h3 className="mb-2">Historical Pattern Analysis</h3>
                <p className="text-sm text-slate-700">
                  Similar transmission issues detected in 23 vehicles of the same model batch (Batch #445, Q3 2023 production).
                  Pattern correlates with high-temperature operating conditions in tier-2 cities.
                </p>
              </div>
              <Separator />
              <div>
                <h3 className="mb-2">Error Codes Referenced</h3>
                <div className="space-y-2">
                  {diagnosticLogs.map((log, index) => (
                    <div key={index} className="flex items-start justify-between text-sm bg-white rounded p-2">
                      <div className="flex-1">
                        <span className="font-mono text-blue-600">{log.code}</span>
                        <p className="text-slate-600 text-xs mt-0.5">{log.description}</p>
                      </div>
                      <Badge
                        variant="secondary"
                        className={log.severity === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}
                      >
                        {log.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-white rounded-lg p-3 mt-4">
                <p className="text-sm">
                  <strong>Recommended Action:</strong> Schedule immediate service appointment for transmission inspection and fluid pressure test.
                  Estimated repair time: 4-6 hours.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Real-time Sensor Graphs */}
          <Card>
            <CardHeader>
              <CardTitle>Real-Time Sensor Data</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sensorData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="engineTemp" stroke="#ef4444" name="Engine Temp (°C)" strokeWidth={2} />
                  <Line type="monotone" dataKey="rpm" stroke="#3b82f6" name="RPM (×1000)" strokeWidth={2} />
                  <Line type="monotone" dataKey="vibration" stroke="#f59e0b" name="Vibration (mm/s)" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-xs text-slate-600">Engine Temperature</p>
                  <p className="text-2xl text-red-600">105°C</p>
                  <p className="text-xs text-red-600 mt-1">Above Normal</p>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-xs text-slate-600">Current RPM</p>
                  <p className="text-2xl text-blue-600">2,800</p>
                  <p className="text-xs text-blue-600 mt-1">Normal Range</p>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <p className="text-xs text-slate-600">Vibration Level</p>
                  <p className="text-2xl text-amber-600">4.5 mm/s</p>
                  <p className="text-xs text-amber-600 mt-1">Elevated</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <Button className="flex-1">Schedule Service</Button>
            <Button variant="outline" className="flex-1">Contact Owner</Button>
            <Button variant="outline">Export Report</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
