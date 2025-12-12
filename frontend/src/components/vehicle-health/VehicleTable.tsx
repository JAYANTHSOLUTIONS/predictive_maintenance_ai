import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'; // Check path ../../ui
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import { Search, Download, Filter } from 'lucide-react';

// ✅ IMPORT THE API BRIDGE
import { api, VehicleSummary } from '../../services/api';

interface VehicleTableProps {
  onSelectVehicle: (vin: string) => void;
  selectedVehicle: string | null;
}

export function VehicleTable({ onSelectVehicle, selectedVehicle }: VehicleTableProps) {
  // 1. STATE: Store the list of vehicles here
  const [vehicles, setVehicles] = useState<VehicleSummary[]>([]);
  const [loading, setLoading] = useState(true);

  // 2. FETCH: Ask Python for the Fleet Status
  useEffect(() => {
    const loadFleet = async () => {
      try {
        const data = await api.getFleetStatus();
        setVehicles(data);
      } catch (err) {
        console.error("Failed to load fleet", err);
      } finally {
        setLoading(false);
      }
    };

    loadFleet();
    // Optional: Refresh every 5 seconds to see status changes live
    const interval = setInterval(loadFleet, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Vehicle Fleet Overview</CardTitle>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input placeholder="Search VIN..." className="pl-9 w-64" />
            </div>
            <Button variant="outline" size="icon"><Filter className="w-4 h-4" /></Button>
            <Button variant="outline" size="icon"><Download className="w-4 h-4" /></Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>VIN</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Last Location</TableHead>
                <TableHead>Telematics</TableHead>
                <TableHead>Predicted Failure</TableHead>
                <TableHead>Probability</TableHead>
                <TableHead>Action Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                  <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">Loading Fleet Data...</TableCell>
                  </TableRow>
              ) : vehicles.length === 0 ? (
                  <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-slate-500">
                          No active vehicles found. Run the Python backend.
                      </TableCell>
                  </TableRow>
              ) : (
                  vehicles.map((vehicle) => (
                    <TableRow
                      key={vehicle.vin}
                      className={`cursor-pointer hover:bg-slate-50 ${selectedVehicle === vehicle.vin ? 'bg-blue-50' : ''}`}
                      onClick={() => onSelectVehicle(vehicle.vin)}
                    >
                      <TableCell className="font-mono text-sm">{vehicle.vin}</TableCell>
                      <TableCell>{vehicle.model}</TableCell>
                      <TableCell>{vehicle.location}</TableCell>
                      <TableCell>
                        {vehicle.telematics === 'Live' ? (
                          <Badge variant="secondary" className="bg-green-100 text-green-700">
                            <div className="w-1.5 h-1.5 bg-green-600 rounded-full mr-1.5 animate-pulse" />
                            Live
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="bg-slate-100 text-slate-700">Offline</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <span className={vehicle.probability >= 85 ? 'text-red-600' : vehicle.probability >= 70 ? 'text-amber-600' : ''}>
                          {vehicle.predictedFailure}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <div className="w-full max-w-[100px] bg-slate-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                vehicle.probability >= 85 ? 'bg-red-500' : vehicle.probability >= 70 ? 'bg-amber-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${vehicle.probability}%` }}
                            />
                          </div>
                          <span className="text-sm">{vehicle.probability}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="secondary"
                          className={
                            vehicle.action === 'Service Booked' ? 'bg-green-100 text-green-700' : 
                            vehicle.action === 'Customer Contacted' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'
                          }
                        >
                          {vehicle.action}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}