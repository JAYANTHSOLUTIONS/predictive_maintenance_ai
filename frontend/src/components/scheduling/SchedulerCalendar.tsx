import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { cn } from '../ui/utils';

interface ServiceBay {
  id: string;
  name: string;
  appointments: Appointment[];
}

interface Appointment {
  id: string;
  time: string;
  duration: number;
  vin: string;
  service: string;
  status: 'auto-scheduled' | 'manual' | 'conflict';
  customer: string;
}

const serviceBays: ServiceBay[] = [
  {
    id: 'bay-1',
    name: 'Bay 1',
    appointments: [
      { id: '1', time: '09:00', duration: 2, vin: 'MH04XY1234', service: 'Transmission Repair', status: 'auto-scheduled', customer: 'Rajesh Kumar' },
      { id: '2', time: '11:30', duration: 1.5, vin: 'DL12AB5678', service: 'Battery Replacement', status: 'auto-scheduled', customer: 'Priya Sharma' },
      { id: '3', time: '14:00', duration: 1, vin: 'KA09CD9012', service: 'Engine Diagnostic', status: 'manual', customer: 'Amit Patel' },
    ],
  },
  {
    id: 'bay-2',
    name: 'Bay 2',
    appointments: [
      { id: '4', time: '09:30', duration: 1, vin: 'TN07EF3456', service: 'Brake Pad Replacement', status: 'auto-scheduled', customer: 'Lakshmi Iyer' },
      { id: '5', time: '11:00', duration: 2, vin: 'MH01GH7890', service: 'Coolant System Check', status: 'conflict', customer: 'Vikram Singh' },
      { id: '6', time: '15:00', duration: 1.5, vin: 'AP05IJ2345', service: 'Oil Change', status: 'auto-scheduled', customer: 'Anita Reddy' },
    ],
  },
  {
    id: 'bay-3',
    name: 'Bay 3',
    appointments: [
      { id: '7', time: '10:00', duration: 3, vin: 'GJ06KL6789', service: 'Full Service', status: 'auto-scheduled', customer: 'Deepak Shah' },
      { id: '8', time: '13:30', duration: 1, vin: 'RJ14MN0123', service: 'Tire Rotation', status: 'auto-scheduled', customer: 'Neha Gupta' },
    ],
  },
  {
    id: 'bay-4',
    name: 'Bay 4',
    appointments: [
      { id: '9', time: '09:00', duration: 1.5, vin: 'WB08OP4567', service: 'AC Service', status: 'manual', customer: 'Sourav Das' },
      { id: '10', time: '11:00', duration: 2, vin: 'UP16QR8901', service: 'Suspension Check', status: 'auto-scheduled', customer: 'Kavita Verma' },
    ],
  },
];

const timeSlots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'];

export function SchedulerCalendar() {
  const [selectedDate, setSelectedDate] = useState('December 14, 2025');

  const getAppointmentAtTime = (bay: ServiceBay, timeSlot: string) => {
    return bay.appointments.find((apt) => apt.time === timeSlot);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Service Bay Scheduler</CardTitle>
            <p className="text-sm text-slate-600 mt-1">Mumbai Central Service Center</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="icon">
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <div className="flex items-center space-x-2 px-3">
                <CalendarIcon className="w-4 h-4 text-slate-600" />
                <span>{selectedDate}</span>
              </div>
              <Button variant="outline" size="icon">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-4 mt-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded" />
            <span>Auto-Scheduled</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded" />
            <span>Manual</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-amber-500 rounded" />
            <span>Needs Review</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="border rounded-lg overflow-hidden">
          <div className="grid grid-cols-5 bg-slate-50">
            <div className="p-3 border-r border-b">Time</div>
            {serviceBays.map((bay) => (
              <div key={bay.id} className="p-3 border-r border-b text-center">
                {bay.name}
              </div>
            ))}
          </div>
          {timeSlots.map((timeSlot) => (
            <div key={timeSlot} className="grid grid-cols-5 border-b hover:bg-slate-50">
              <div className="p-3 border-r text-sm text-slate-600">{timeSlot}</div>
              {serviceBays.map((bay) => {
                const appointment = getAppointmentAtTime(bay, timeSlot);
                return (
                  <div key={bay.id} className="p-2 border-r min-h-[80px]">
                    {appointment && (
                      <div
                        className={cn(
                          'rounded-lg p-2 text-xs h-full',
                          appointment.status === 'auto-scheduled' && 'bg-green-100 border border-green-300',
                          appointment.status === 'manual' && 'bg-blue-100 border border-blue-300',
                          appointment.status === 'conflict' && 'bg-amber-100 border border-amber-300'
                        )}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-mono">{appointment.vin}</span>
                          <Badge
                            variant="secondary"
                            className={cn(
                              'text-xs px-1 py-0',
                              appointment.status === 'auto-scheduled' && 'bg-green-200 text-green-800',
                              appointment.status === 'manual' && 'bg-blue-200 text-blue-800',
                              appointment.status === 'conflict' && 'bg-amber-200 text-amber-800'
                            )}
                          >
                            {appointment.duration}h
                          </Badge>
                        </div>
                        <p className="mb-1">{appointment.service}</p>
                        <p className="text-slate-600">{appointment.customer}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <p className="text-xs text-slate-600">Auto-Scheduled Today</p>
            <p className="text-2xl text-green-600">8</p>
            <p className="text-xs text-green-600 mt-1">80% of total</p>
          </div>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <p className="text-xs text-slate-600">Needs Review</p>
            <p className="text-2xl text-amber-600">1</p>
            <p className="text-xs text-amber-600 mt-1">Capacity conflict</p>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-slate-600">Bay Utilization</p>
            <p className="text-2xl text-blue-600">78%</p>
            <p className="text-xs text-blue-600 mt-1">Optimal range</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
