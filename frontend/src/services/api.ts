import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// ==========================================
// 1. INTERFACES (Matched to Python Backend)
// ==========================================

export interface TelematicsData {
    vehicle_id: string;
    engine_temp_c: number;
    oil_pressure_psi: number;
    rpm: number;
    active_dtc_codes?: string[] | string; // Backend might send string "None" or list
}

export interface VoiceLogEntry {
    role: string;    // Matches Python: "system", "user", "assistant"
    content: string; // Matches Python content
}

// returned by /api/predictive/run
export interface AnalysisResult {
    vehicle_id: string;
    risk_score: number;
    diagnosis_report?: string; // Backend uses 'diagnosis_report'
    customer_script?: string;
    booking_id?: string;
    detected_issues?: string[];
    
    // Voice Data
    voice_transcript?: VoiceLogEntry[];
    scheduled_date?: string;
}

// returned by /api/fleet/status
export interface VehicleSummary {
    vin: string;
    model: string;
    location: string;
    telematics: string;
    predictedFailure: string;
    probability: number;
    action: string;
    scheduled_date?: string | null;
    voice_transcript?: VoiceLogEntry[] | null;
}

export interface ActivityLog {
    id: string;
    time: string;
    agent: string;
    vehicle_id: string;
    message: string;
    type: 'info' | 'warning' | 'alert';
}

export interface BookingResponse {
    status: string;
    booking_id: string;
    message: string;
}

// ==========================================
// 2. API SERVICE
// ==========================================

export const api = {
    // 📡 Get Live Telematics (Simulated or Real)
    getTelematics: async (vehicleId: string): Promise<TelematicsData | null> => {
        try {
            const response = await axios.get(`${API_BASE_URL}/telematics/${vehicleId}`);
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch telematics for ${vehicleId}`, error);
            return null;
        }
    },

    // 🧠 Trigger AI Analysis (The Agent Chain)
    runPrediction: async (vehicleId: string): Promise<AnalysisResult | null> => {
        try {
            const response = await axios.post(`${API_BASE_URL}/predictive/run`, {
                vehicle_id: vehicleId
            });
            return response.data;
        } catch (error) {
            console.error("AI Prediction failed:", error);
            return null;
        }
    },

    // 📋 Get Fleet Dashboard Data (Main Table)
    getFleetStatus: async (): Promise<VehicleSummary[]> => {
        try {
            const response = await axios.get(`${API_BASE_URL}/fleet/status`);
            return response.data;
        } catch (error) {
            console.error("Failed to load fleet status", error);
            return [];
        }
    },

    // 📜 Get Interaction Log (Voice/Chat Transcript)
    // NOTE: We fetch the fleet status and find the specific vehicle
    // because the transcript is embedded in the summary.
    getInteractionLog: async (vin: string): Promise<AnalysisResult | null> => {
        try {
            const fleet = await api.getFleetStatus();
            const vehicle = fleet.find(v => v.vin === vin);
            
            if (vehicle) {
                // Map VehicleSummary to AnalysisResult format for the modal
                return {
                    vehicle_id: vehicle.vin,
                    risk_score: vehicle.probability,
                    diagnosis_report: vehicle.predictedFailure,
                    voice_transcript: vehicle.voice_transcript || []
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    },

    // 🕒 Get Activity Timeline
    getAgentActivity: async (): Promise<ActivityLog[]> => {
        try {
            const response = await axios.get(`${API_BASE_URL}/fleet/activity`);
            return response.data;
        } catch (error) {
            return [];
        }
    },

    // 📅 Schedule Repair Manually (Optional)
    scheduleRepair: async (vehicleId: string, date: string, notes: string): Promise<BookingResponse> => {
        try {
            // Note: This endpoint might need to be created in backend if not exists, 
            // but usually the Agent handles this.
            return { status: "success", booking_id: "MANUAL-001", message: "Slot requested" };
        } catch (error) {
            throw error;
        }
    }
};