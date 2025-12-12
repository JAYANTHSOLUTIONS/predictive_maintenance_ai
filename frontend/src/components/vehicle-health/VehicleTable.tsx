import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
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

interface VehicleTableProps {
  onSelectVehicle: (vin: string) => void;
  selectedVehicle: string | null;
}

const vehicles = [
  {
    vin: 'MH04XY1234',
    model: 'Sedan X Pro',
    location: 'Mumbai, MH',
    telematics: 'Live',
    predictedFailure: 'Transmission Slip',
    probability: 92,
    action: 'Service Booked',
  },
  {
    vin: 'DL12AB5678',
    model: 'SUV Elite',
    location: 'Delhi NCR',
    telematics: 'Live',
    predictedFailure: 'Battery Voltage Critical',
    probability: 88,
    action: 'Customer Contacted',
  },
  {
    vin: 'KA09CD9012',
    model: 'Hatchback Plus',
    location: 'Bangalore, KA',
    telematics: 'Live',
    predictedFailure: 'Engine Vibration Abnormal',
    probability: 76,
    action: 'Pending Review',
  },
  {
    vin: 'TN07EF3456',
    model: 'Sedan X Pro',
    location: 'Chennai, TN',
    telematics: 'Live',
    predictedFailure: 'Brake Pad Wear',
    probability: 94,
    action: 'Service Booked',
  },
  {
    vin: 'MH01GH7890',
    model: 'SUV Elite',
    location: 'Pune, MH',
    telematics: 'Offline',
    predictedFailure: 'Connection Lost',
    probability: 0,
    action: 'Investigating',
  },
  {
    vin: 'AP05IJ2345',
    model: 'Hatchback Plus',
    location: 'Hyderabad, TS',
    telematics: 'Live',
    predictedFailure: 'Coolant Temperature High',
    probability: 81,
    action: 'Customer Contacted',
  },
  {
    vin: 'GJ06KL6789',
    model: 'Sedan X Pro',
    location: 'Ahmedabad, GJ',
    telematics: 'Live',
    predictedFailure: 'Tire Pressure Low',
    probability: 67,
    action: 'Alert Sent',
  },
  {
    vin: 'RJ14MN0123',
    model: 'SUV Elite',
    location: 'Jaipur, RJ',
    telematics: 'Live',
    predictedFailure: 'Oil Change Due',
    probability: 99,
    action: 'Service Booked',
  },
];

export function VehicleTable({ onSelectVehicle, selectedVehicle }: VehicleTableProps) {
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
            <Button variant="outline" size="icon">
              <Filter className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="icon">
              <Download className="w-4 h-4" />
            </Button>
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
              {vehicles.map((vehicle) => (
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
                      <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                        Offline
                      </Badge>
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
                            vehicle.probability >= 85
                              ? 'bg-red-500'
                              : vehicle.probability >= 70
                              ? 'bg-amber-500'
                              : 'bg-green-500'
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
                        vehicle.action === 'Service Booked'
                          ? 'bg-green-100 text-green-700'
                          : vehicle.action === 'Customer Contacted'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-amber-100 text-amber-700'
                      }
                    >
                      {vehicle.action}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
