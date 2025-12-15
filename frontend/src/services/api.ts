import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// --- 1. DEFINITIONS ---

export interface TelematicsData {
  vehicle_id: string;
  engine_temp_c: number;
  oil_pressure_psi: number;
  rpm: number;
  battery_voltage: number;
  active_dtc_codes: string[];
}

// ✅ UPDATED: Flat Structure to match the expectations of VehicleDetailPanel.tsx
export interface AnalysisResult {
  vehicle_id: string;
  status: string;
  // Mapped from analysis.diagnosis.risk_level
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'; 
  // Mapped from analysis.diagnosis.report
  diagnosis: string; 
  // ADDED: Was missing but used in the component
  risk_score: number; 
  
  // Mapped from analysis.manufacturing.recommendation
  manufacturing_insights: string | null; 
  
  // ADDED: Was missing but used in the component (UEBA alerts for security)
  ueba_alerts: {
    message: string;
    timestamp: string;
  }[]; 
  
  // Mapped from analysis.scheduling.booking_id
  booking_id: string | null; 
}


export interface VehicleSummary {
  vin: string;
  model: string;
  location: string;
  telematics: string;
  predictedFailure: string;
  probability: number;
  action: string;
  scheduled_date?: string;
}

export interface BookingResponse {
  status: string;
  booking_id: string;
  message: string;
}

export interface ActivityLog {
  id: string;
  time: string;
  agent: string;
  vehicle_id: string;
  message: string;
  type: 'info' | 'warning' | 'alert';
}

// --- 2. THE API BRIDGE ---

export const api = {
  // Get Live Telematics
  getTelematics: async (vehicleId: string): Promise<TelematicsData | null> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/telematics/${vehicleId}`);
      return response.data;
    } catch (error) {
      console.error("Failed to fetch telematics:", error);
      return null;
    }
  },

  // ✅ UPDATED: Points to /predictive/analyze and sends customer_decision
  runPrediction: async (vehicleId: string): Promise<AnalysisResult | null> => {
    try {
      // Changed endpoint from '/predictive/run' to '/predictive/analyze'
      const response = await axios.post(`${API_BASE_URL}/predictive/analyze`, {
        vehicle_id: vehicleId,
        customer_decision: "PENDING" // Required by backend pydantic model
      });
      
      // Assuming backend sends flat data now, but added error handling just in case
      // Note: If your backend returns the nested data (diagnosis:{...}, scheduling:{...}), 
      // you will need to map it here before returning to the frontend.
      // E.g., return transformAnalysis(response.data);
      
      return response.data;
    } catch (error) {
      console.error("AI Prediction failed:", error);
      throw error;
    }
  },

  // Get Fleet Overview
  getFleetStatus: async (): Promise<VehicleSummary[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/fleet/status`);
      return response.data;
    } catch (e) {
      return [];
    }
  },

  // Schedule Repair (Manual Override)
  scheduleRepair: async (vehicleId: string, date: string, notes: string): Promise<BookingResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/schedule/create`, {
        vehicle_id: vehicleId,
        service_date: date,
        notes: notes
      });
      return response.data;
    } catch (error) {
      console.error("Booking failed:", error);
      throw error;
    }
  },

  // Get Activity Feed
  getAgentActivity: async (): Promise<ActivityLog[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/fleet/activity`);
      return response.data;
    } catch (e) {
      return [];
    }
  },

  // System Health Check
  getSystemStatus: async () => {
    try {
      const response = await axios.get('http://localhost:8000/'); 
      return response.data;
    } catch (error) {
      return null;
    }
  }
};