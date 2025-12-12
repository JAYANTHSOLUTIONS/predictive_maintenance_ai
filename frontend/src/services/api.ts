import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// --- 1. DEFINITIONS ---

// For the Gauges
export interface TelematicsData {
  vehicle_id: string;
  engine_temp_c: number;
  oil_pressure_psi: number;
  rpm: number;
  battery_voltage: number;
  active_dtc_codes: string[];
}

// For the AI Report
export interface AnalysisResult {
  vehicle_id: string;
  risk_score: number;
  risk_level: string;
  diagnosis: string;
  customer_script?: string;
  booking_id?: string;
  manufacturing_insights?: string;
  ueba_alerts: Array<{ message: string; agent: string }>;
}

// For the Fleet Table (MISSING BEFORE)
export interface VehicleSummary {
  vin: string;
  model: string;
  location: string;
  telematics: string;
  predictedFailure: string;
  probability: number;
  action: string;
}

// --- 2. THE API BRIDGE ---

export const api = {
  // Get Live Telematics (Gauges)
  getTelematics: async (vehicleId: string): Promise<TelematicsData | null> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/telematics/${vehicleId}`);
      return response.data;
    } catch (error) {
      console.error("Failed to fetch telematics:", error);
      return null;
    }
  },

  // Run AI Analysis (Button Click)
  runPrediction: async (vehicleId: string): Promise<AnalysisResult | null> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/predictive/run`, {
        vehicle_id: vehicleId
      });
      return response.data;
    } catch (error) {
      console.error("AI Prediction failed:", error);
      throw error;
    }
  },

  // Get Fleet Overview (MISSING BEFORE)
  getFleetStatus: async (): Promise<VehicleSummary[]> => {
    try {
      // Note: We need to create this endpoint in Python next if it's not there yet.
      // If Python throws 404, this returns an empty list so React won't crash.
      const response = await axios.get(`${API_BASE_URL}/fleet/status`);
      return response.data;
    } catch (e) {
      console.warn("Fleet endpoint not ready yet, returning empty list.");
      return [];
    }
  }
};