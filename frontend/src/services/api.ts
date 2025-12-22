import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// --- 1. DEFINITIONS (UPDATED) ---

export interface TelematicsData {
    vehicle_id: string;
    engine_temp_c: number;
    oil_pressure_psi: number;
    rpm: number;
    battery_voltage: number;
    active_dtc_codes: string[];
}

// 💥 UPDATED INTERFACE to include voice agent log fields
export interface AnalysisResult {
    vehicle_id: string;
    risk_score: number;
    risk_level: string;
    diagnosis: string;
    customer_script?: string;
    booking_id?: string;
    manufacturing_insights?: string;
    ueba_alerts: Array<{ message: string; agent: string }>;
    
    // --- NEW FIELDS ADDED FROM VOICE AGENT STATE ---
    audio_available?: boolean;
    audio_url?: string; // The public HTTP path (e.g., /audio/voice_recording_V-101.mp3)
    voice_transcript?: Array<{ id: number, speaker: string, text: string, time: string }>;
    scheduled_date?: string; // Updated from the agent flow
    vin?: string; // Explicitly passed back by the agent flow
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

// --- 2. THE API BRIDGE (UPDATED) ---

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

    // Run AI Analysis (Existing - now returns the enriched AnalysisResult)
    runPrediction: async (vehicleId: string): Promise<AnalysisResult | null> => {
        try {
            const response = await axios.post(`${API_BASE_URL}/predictive/run`, {
                vehicle_id: vehicleId
            });
            // The backend predictive/run endpoint should now return the full AnalysisResult 
            // including the voice log details.
            return response.data;
        } catch (error) {
            console.error("AI Prediction failed:", error);
            throw error;
        }
    },

    // 💥 NEW FUNCTION: Get Detailed Interaction Log 
    // This is the cleanest way to open the modal with the full data set.
    getInteractionLog: async (vin: string): Promise<AnalysisResult | null> => {
        try {
            // Assuming your backend has an endpoint to retrieve the last run log by VIN/ID.
            // If the predictive/run endpoint is the only source, this endpoint might be: 
            // GET /api/predictive/log/{vin}
            const response = await axios.get(`${API_BASE_URL}/predictive/log/${vin}`);
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch log for ${vin}:`, error);
            return null;
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

    // Schedule Repair
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

    // FIXED: System Health Check (Points to ROOT, bypassing /api)
    getSystemStatus: async () => {
        try {
            // Direct call to root to check if server is alive
            const response = await axios.get('http://localhost:8000/'); 
            return response.data;
        } catch (error) {
            return null;
        }
    }
};