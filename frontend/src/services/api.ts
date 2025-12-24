import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// ==========================================
// 1. INTERFACES
// ==========================================

export interface TelematicsData {
    vehicle_id: string;
    engine_temp_c: number;
    oil_pressure_psi: number;
    rpm: number;
    battery_voltage?: number;
    active_dtc_codes?: string[] | string;
}

export interface VoiceLogEntry {
    role: string;
    content: string;
}

// ✅ FIXED: Updated to match VehicleDetailPanel.tsx requirements
export interface AnalysisResult {
    vehicle_id: string;
    risk_score: number;
    
    // These were missing or named differently:
    risk_level: string;               // Was missing
    diagnosis: string;                // Was 'diagnosis_report'
    manufacturing_insights?: string;  // Was missing
    ueba_alerts?: { message: string }[]; // Was missing
    
    customer_script?: string;
    booking_id?: string;
    detected_issues?: string[];
    voice_transcript?: VoiceLogEntry[];
    scheduled_date?: string;
}

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
    engine_temp?: number;
    oil_pressure?: number;
    battery_voltage?: number;
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
    getTelematics: async (vehicleId: string): Promise<TelematicsData | null> => {
        try {
            const response = await axios.get(`${API_BASE_URL}/telematics/${vehicleId}`);
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch telematics for ${vehicleId}`, error);
            return null;
        }
    },

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

    getFleetStatus: async (): Promise<VehicleSummary[]> => {
        try {
            const response = await axios.get(`${API_BASE_URL}/fleet/status`);
            return response.data;
        } catch (error) {
            console.error("Failed to load fleet status", error);
            return [];
        }
    },

    getInteractionLog: async (vin: string): Promise<AnalysisResult | null> => {
        try {
            const fleet = await api.getFleetStatus();
            const vehicle = fleet.find(v => v.vin === vin);
            if (vehicle) {
                // Map summary back to analysis format for consistency
                return {
                    vehicle_id: vehicle.vin,
                    risk_score: vehicle.probability,
                    risk_level: vehicle.probability > 80 ? 'CRITICAL' : 'MEDIUM', // Mock for summary
                    diagnosis: vehicle.predictedFailure,
                    voice_transcript: vehicle.voice_transcript || []
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    },

    getAgentActivity: async (): Promise<ActivityLog[]> => {
        try {
            const response = await axios.get(`${API_BASE_URL}/fleet/activity`);
            return response.data;
        } catch (error) {
            return [];
        }
    },

    scheduleRepair: async (vehicleId: string, date: string, notes: string): Promise<BookingResponse> => {
        return { status: "success", booking_id: "MANUAL-001", message: "Slot requested" };
    }
};