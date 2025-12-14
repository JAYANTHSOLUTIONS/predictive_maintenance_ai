import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { MapPin, ZoomIn, ZoomOut, Navigation, Layers, Filter } from 'lucide-react';
import { Button } from '../ui/button';

// Mock Data: Cluster of vehicles in India
const vehicleClusters = [
  { id: 1, city: 'Mumbai', lat: 19.076, lng: 72.877, count: 2845, healthy: 2620, warning: 180, critical: 45 },
  { id: 2, city: 'Delhi', lat: 28.704, lng: 77.102, count: 3120, healthy: 2890, warning: 195, critical: 35 },
  { id: 3, city: 'Bangalore', lat: 12.971, lng: 77.594, count: 2650, healthy: 2450, warning: 165, critical: 35 },
  { id: 4, city: 'Chennai', lat: 13.082, lng: 80.270, count: 1980, healthy: 1810, warning: 140, critical: 30 },
  { id: 5, city: 'Hyderabad', lat: 17.385, lng: 78.486, count: 1450, healthy: 1320, warning: 105, critical: 25 },
  { id: 6, city: 'Pune', lat: 18.520, lng: 73.856, count: 1230, healthy: 1140, warning: 75, critical: 15 },
];

export function FleetMap() {
  const [hoveredCluster, setHoveredCluster] = useState<number | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'WARNING'>('ALL');

  // Simple Zoom Logic
  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.5, 3));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.5, 1));

  // Filter Logic
  const getClusterColor = (cluster: any) => {
    if (filter === 'CRITICAL' && cluster.critical > 0) return 'bg-red-600 border-red-200';
    if (filter === 'WARNING' && cluster.warning > 0) return 'bg-yellow-500 border-yellow-200';
    // Default color logic
    if (cluster.critical > 20) return 'bg-red-600 border-white';
    if (cluster.warning > 100) return 'bg-yellow-500 border-white';
    return 'bg-blue-600 border-white';
  };

  const isVisible = (cluster: any) => {
    if (filter === 'CRITICAL') return cluster.critical > 0;
    if (filter === 'WARNING') return cluster.warning > 0;
    return true;
  };

  return (
    <Card className="h-[500px] flex flex-col overflow-hidden border-slate-200 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between py-4 px-6 bg-white border-b z-10">
        <div>
            <CardTitle className="text-lg flex items-center">
            <Navigation className="w-5 h-5 mr-2 text-blue-600" />
            Live Fleet Operations
            </CardTitle>
            <p className="text-xs text-slate-500 mt-1">Geospatial Telemetry (India Region)</p>
        </div>
        
        {/* Map Controls */}
        <div className="flex space-x-2">
            <div className="flex bg-slate-100 rounded-lg p-1">
                <Button 
                    variant={filter === 'ALL' ? 'default' : 'ghost'} 
                    size="sm" 
                    className="h-7 text-xs"
                    onClick={() => setFilter('ALL')}
                >
                    All
                </Button>
                <Button 
                    variant={filter === 'CRITICAL' ? 'destructive' : 'ghost'} 
                    size="sm" 
                    className="h-7 text-xs"
                    onClick={() => setFilter('CRITICAL')}
                >
                    Critical
                </Button>
            </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 p-0 relative bg-slate-900 overflow-hidden group">
        
        {/* --- MAP VISUALIZATION LAYER --- */}
        <div 
            className="absolute inset-0 transition-transform duration-500 ease-in-out"
            style={{ transform: `scale(${zoomLevel})` }}
        >
            {/* 1. Map Background (Dark Tech Grid) */}
            <div className="absolute inset-0 bg-slate-900">
                {/* India Map Image Overlay */}
                <img 
                  src="https://upload.wikimedia.org/wikipedia/commons/1/1f/India_map_en.svg" 
                  alt="India Map" 
                  className="absolute inset-0 w-full h-full object-contain opacity-20 grayscale invert"
                  style={{ padding: '20px' }}
                />

                {/* Tech Grid Overlay */}
                <svg className="w-full h-full opacity-20 relative z-10">
                    <defs>
                    <pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#64748b" strokeWidth="0.5" />
                    </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid-pattern)" />
                </svg>
            </div>

            {/* 2. Vehicle Clusters (Pins) */}
            {vehicleClusters.map((cluster) => (
            <div
                key={cluster.id}
                className={`absolute cursor-pointer transition-all duration-300 z-20 ${isVisible(cluster) ? 'opacity-100 scale-100' : 'opacity-20 scale-75 blur-[1px]'}`}
                style={{
                    // Approximate Projection for India within the container
                    left: `${((cluster.lng - 68) / (97 - 68)) * 100}%`,
                    top: `${100 - ((cluster.lat - 8) / (35 - 8)) * 100}%`,
                }}
                onMouseEnter={() => setHoveredCluster(cluster.id)}
                onMouseLeave={() => setHoveredCluster(null)}
            >
                <div className="relative -translate-x-1/2 -translate-y-1/2 group">
                    <div className={`w-4 h-4 rounded-full border-2 shadow-[0_0_15px_rgba(59,130,246,0.5)] ${getClusterColor(cluster)}`} />
                    {isVisible(cluster) && (
                        <div className={`absolute inset-0 w-4 h-4 rounded-full animate-ping opacity-75 ${getClusterColor(cluster).split(' ')[0]}`} />
                    )}
                    <div className="absolute top-6 left-1/2 -translate-x-1/2 text-[10px] font-mono text-slate-400 whitespace-nowrap bg-slate-900/80 px-2 py-0.5 rounded-full backdrop-blur-sm border border-slate-700">
                        {cluster.city}
                    </div>
                </div>

                {/* Hover Tooltip */}
                {hoveredCluster === cluster.id && (
                <div className="absolute left-6 bottom-6 bg-slate-800 border border-slate-700 text-white rounded-lg shadow-2xl p-4 w-64 z-50 animate-in fade-in zoom-in-95 duration-200">
                    <div className="flex justify-between items-start mb-3">
                        <div>
                            <h4 className="font-bold text-sm">{cluster.city} Operations</h4>
                            <div className="text-xs text-slate-400">Lat: {cluster.lat}, Lng: {cluster.lng}</div>
                        </div>
                        <Badge variant="outline" className="border-slate-600 text-slate-300">Hub #{cluster.id}</Badge>
                    </div>
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs items-center p-1.5 bg-slate-700/50 rounded">
                            <span className="text-slate-300">Total Fleet</span>
                            <span className="font-mono font-bold">{cluster.count}</span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-center pt-2">
                            <div>
                                <div className="text-[10px] text-slate-400 uppercase">Healthy</div>
                                <div className="text-sm font-bold text-green-400">{cluster.healthy}</div>
                            </div>
                            <div>
                                <div className="text-[10px] text-slate-400 uppercase">Warning</div>
                                <div className="text-sm font-bold text-yellow-400">{cluster.warning}</div>
                            </div>
                            <div>
                                <div className="text-[10px] text-slate-400 uppercase">Critical</div>
                                <div className="text-sm font-bold text-red-400">{cluster.critical}</div>
                            </div>
                        </div>
                    </div>
                </div>
                )}
            </div>
            ))}
        </div>

        {/* Map Controls */}
        <div className="absolute bottom-6 right-6 flex flex-col space-y-2 z-30">
            <Button variant="secondary" size="icon" className="h-8 w-8 shadow-lg bg-white/90 backdrop-blur" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4 text-slate-700" />
            </Button>
            <Button variant="secondary" size="icon" className="h-8 w-8 shadow-lg bg-white/90 backdrop-blur" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4 text-slate-700" />
            </Button>
        </div>
      </CardContent>
    </Card>
  );
}