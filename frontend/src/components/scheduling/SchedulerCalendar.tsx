import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'; // Fixed Import
import { Badge } from '../ui/badge'; // Fixed Import
import { Button } from '../ui/button'; // Fixed Import
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, RefreshCw } from 'lucide-react';

// ✅ Import API to get Real Data
import { api } from '../../services/api';

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

const timeSlots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'];

export function SchedulerCalendar() {
  const [selectedDate, setSelectedDate] = useState(new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }));
  const [bays, setBays] = useState<ServiceBay[]>([]);
  const [loading, setLoading] = useState(true);

  // ✅ FETCH REAL DATA & MERGE WITH MOCK DATA
  useEffect(() => {
    const loadSchedule = async () => {
      setLoading(true);
      
      // 1. Get Real Bookings from Python
      const fleet = await api.getFleetStatus();
      const realBookings = fleet.filter(v => v.action === 'Service Booked');

      // 2. Define Mock Base Schedule (The "Busy" Shop)
      const baseSchedule: ServiceBay[] = [
        {
          id: 'bay-1', name: 'Bay 1 (Heavy)',
          appointments: [
             // We will inject real bookings here
          ],
        },
        {
          id: 'bay-2', name: 'Bay 2 (Electrical)',
          appointments: [
            { id: '4', time: '09:00', duration: 1, vin: 'TN07EF3456', service: 'Brake Pad Replacement', status: 'auto-scheduled', customer: 'Lakshmi Iyer' },
            { id: '5', time: '11:00', duration: 2, vin: 'MH01GH7890', service: 'Coolant System Check', status: 'conflict', customer: 'Vikram Singh' },
          ],
        },
        {
          id: 'bay-3', name: 'Bay 3 (General)',
          appointments: [
            { id: '7', time: '10:00', duration: 3, vin: 'GJ06KL6789', service: 'Full Service', status: 'auto-scheduled', customer: 'Deepak Shah' },
          ],
        },
        {
          id: 'bay-4', name: 'Bay 4 (Express)',
          appointments: [
            { id: '9', time: '09:00', duration: 1.5, vin: 'WB08OP4567', service: 'AC Service', status: 'manual', customer: 'Sourav Das' },
          ],
        },
      ];

      // 3. Inject Real Vehicles into Bay 1
      realBookings.forEach((vehicle, index) => {
          baseSchedule[0].appointments.push({
              id: `real-${vehicle.vin}`,
              time: index === 0 ? '09:00' : '14:00', // Slot logic
              duration: 2,
              vin: vehicle.vin,
              service: vehicle.predictedFailure || 'General Repair',
              status: 'auto-scheduled',
              customer: 'Priority Client'
          });
      });

      setBays(baseSchedule);
      setLoading(false);
    };

    loadSchedule();
  }, []);

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
              <Button variant="outline" size="icon"><ChevronLeft className="w-4 h-4" /></Button>
              <div className="flex items-center space-x-2 px-3 min-w-[160px] justify-center font-mono">
                <CalendarIcon className="w-4 h-4 text-slate-600" />
                <span>{selectedDate}</span>
              </div>
              <Button variant="outline" size="icon"><ChevronRight className="w-4 h-4" /></Button>
            </div>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center space-x-4 mt-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span>Auto-Scheduled</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span>Manual</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-amber-500 rounded-full" />
            <span>Conflict</span>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {loading ? (
            <div className="flex items-center justify-center h-40 text-slate-500">
                <RefreshCw className="w-6 h-6 animate-spin mr-2"/> Syncing with AI Dispatcher...
            </div>
        ) : (
            <div className="border rounded-lg overflow-hidden">
            {/* Header Row */}
            <div className="grid grid-cols-5 bg-slate-50">
                <div className="p-3 border-r border-b font-medium text-slate-500 text-sm">Time</div>
                {bays.map((bay) => (
                <div key={bay.id} className="p-3 border-r border-b text-center font-bold text-slate-700">
                    {bay.name}
                </div>
                ))}
            </div>

            {/* Time Slots */}
            {timeSlots.map((timeSlot) => (
                <div key={timeSlot} className="grid grid-cols-5 border-b hover:bg-slate-50/50 transition-colors">
                <div className="p-3 border-r text-sm text-slate-500 font-mono">{timeSlot}</div>
                {bays.map((bay) => {
                    const appointment = getAppointmentAtTime(bay, timeSlot);
                    return (
                    <div key={bay.id} className="p-1 border-r min-h-[80px] relative">
                        {appointment && (
                        <div
                            className={`rounded-md p-2 text-xs h-full shadow-sm border ${
                            appointment.status === 'auto-scheduled' ? 'bg-green-50 border-green-200 text-green-900' :
                            appointment.status === 'manual' ? 'bg-blue-50 border-blue-200 text-blue-900' :
                            'bg-amber-50 border-amber-200 text-amber-900'
                            }`}
                        >
                            <div className="flex items-center justify-between mb-1">
                            <span className="font-bold">{appointment.vin}</span>
                            <Badge variant="secondary" className="text-[10px] h-5 px-1 bg-white/50">
                                {appointment.duration}h
                            </Badge>
                            </div>
                            <p className="font-medium leading-tight mb-1">{appointment.service}</p>
                            <p className="opacity-70 truncate">{appointment.customer}</p>
                        </div>
                        )}
                    </div>
                    );
                })}
                </div>
            ))}
            </div>
        )}
      </CardContent>
    </Card>
  );
}