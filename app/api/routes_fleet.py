import os
import json
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

# ✅ IMPORT THE SCHEDULER SERVICE TO ACCESS REAL-TIME MEMORY
from app.agents.nodes.scheduling import SchedulerService

router = APIRouter()

# --- 1. DATA MODELS ---

class VehicleSummary(BaseModel):
    vin: str
    model: str
    location: str
    telematics: str
    predictedFailure: str
    probability: int
    action: str
    scheduled_date: Optional[str] = None

class ActivityLog(BaseModel):
    id: str
    time: str
    agent: str 
    vehicle_id: str
    message: str
    type: str   # "info", "warning", "alert"

# --- 2. FILE PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data_samples", "collected_data.json")
LOG_DIR = os.path.join(BASE_DIR, "data_samples")

# --- 3. HELPER: MOCK GEOCODING ---
def resolve_location(gps_data):
    """
    Maps lat/lon to a city name for the table display.
    """
    if not gps_data:
        return "Unknown"
    
    lat = gps_data.get("lat", 0)
    lon = gps_data.get("lon", 0)

    # Simple coordinate matching (approximate ranges)
    if 28.0 <= lat <= 29.0: return "Delhi, NCR"
    if 18.0 <= lat <= 20.0: return "Mumbai, MH"
    if 12.0 <= lat <= 13.5 and 77.0 <= lon <= 78.0: return "Bangalore, KA"
    if 12.0 <= lat <= 13.5 and 80.0 <= lon <= 81.0: return "Chennai, TN"
    if 22.0 <= lat <= 23.0: return "Kolkata, WB"
    if 17.0 <= lat <= 18.0: return "Hyderabad, TS"
    if 23.0 <= lat <= 24.0: return "Ahmedabad, GJ"
    if 30.0 <= lat <= 32.0: return "Shimla, HP"
    
    # Fallback if no match
    return f"{lat:.2f}, {lon:.2f}"

# --- 4. ENDPOINTS ---

@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    Returns the fleet list merged with AI logs AND real-time memory.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        
        vehicles = data.get("vehicles", {})
        summary_list = []

        # ✅ 1. GET REAL-TIME BOOKINGS FROM MEMORY
        # Convert list to a dictionary for fast lookup: { "VIN-123": BookingObject }
        live_bookings = {b['vin']: b for b in SchedulerService.get_all_bookings()}

        for v_id, v_data in vehicles.items():
            # Defaults
            failure = "System Healthy"
            prob = 0
            action = "Monitoring"
            s_date = None
            
            # Get Real Location from Data
            telematics = v_data.get("telematics", {})
            real_location = resolve_location(telematics.get("gps_location"))

            # ✅ 2. CHECK MEMORY FIRST (Priority over disk files)
            # If the Agent just booked it, this will run immediately
            if v_id in live_bookings:
                booking = live_bookings[v_id]
                failure = booking.get("service_type", "Scheduled Maintenance")
                prob = 99 # It's booked, so issue is confirmed
                action = "Service Booked"
                s_date = f"{booking['slot_date']} {booking['slot_time']}"

            # 3. IF NOT IN MEMORY, CHECK LOG FILES (Fallback logic)
            else:
                log_path = os.path.join(LOG_DIR, f"run_log_{v_id}.json")
                if os.path.exists(log_path):
                    try:
                        with open(log_path, "r") as log_f:
                            ai_result = json.load(log_f)
                            prob = ai_result.get("risk_score", 0)
                            
                            # Failure
                            issues = ai_result.get("detected_issues", [])
                            if issues: failure = issues[0]
                            elif prob > 50: failure = "Unknown Anomaly"
                            
                            # Action & Date
                            decision = ai_result.get("customer_decision")
                            
                            if decision == "accept" or ai_result.get("booking_id"):
                                action = "Service Booked"
                                s_date = ai_result.get("selected_slot") or ai_result.get("scheduled_date")
                            elif decision == "reject":
                                action = "Customer Contacted"
                            elif prob > 70:
                                action = "Alert Sent"
                    except Exception:
                        pass

            summary_list.append(VehicleSummary(
                vin=v_id,
                model=v_data.get("metadata", {}).get("model", "Unknown Model"),
                location=real_location, 
                telematics="Live",
                predictedFailure=failure,
                probability=prob,
                action=action,
                scheduled_date=s_date
            ))
        
        return summary_list
    except Exception as e:
        print(f"Error reading fleet: {e}")
        return []

@router.get("/activity", response_model=List[ActivityLog])
async def get_agent_activity():
    """
    Scans all run_logs to generate a timeline of Agent actions for the Dashboard.
    """
    activities = []
    
    # ✅ 1. READ FROM MEMORY (The "Just Now" events)
    # This ensures the dashboard updates instantly when you click "Run AI"
    real_bookings = SchedulerService.get_all_bookings()
    for b in real_bookings:
         activities.append(ActivityLog(
            id=f"{b['vin']}-live",
            time="Just now", 
            agent="Scheduling Bot",
            vehicle_id=b['vin'],
            message=f"Confirmed service: {b['service_type']} at {b['slot_time']}",
            type="info"
        ))
    
    # 2. READ FROM FILES (Historical events)
    if os.path.exists(LOG_DIR):
        for filename in os.listdir(LOG_DIR):
            if filename.startswith("run_log_") and filename.endswith(".json"):
                vehicle_id = filename.replace("run_log_", "").replace(".json", "")
                filepath = os.path.join(LOG_DIR, filename)
                
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        
                        # Diagnosis Agent Log
                        if data.get("diagnosis"): # Assuming key is diagnosis_report or similar check
                            activities.append(ActivityLog(
                                id=f"{vehicle_id}-diag",
                                time="Today", 
                                agent="Diagnosis Agent",
                                vehicle_id=vehicle_id,
                                message=f"Identified issue: {data.get('detected_issues', ['Unknown'])[0]}",
                                type="info"
                            ))

                        # Risk Agent Log
                        risk_score = data.get("risk_score", 0)
                        if risk_score > 50:
                             activities.append(ActivityLog(
                                id=f"{vehicle_id}-risk",
                                time="Today",
                                agent="Risk Guardian",
                                vehicle_id=vehicle_id,
                                message=f"Escalated high risk profile ({risk_score}%)",
                                type="alert" if risk_score > 80 else "warning"
                            ))
                        
                        # Scheduler Agent Log (From file history)
                        if data.get("booking_id") and vehicle_id not in [b['vin'] for b in real_bookings]:
                             activities.append(ActivityLog(
                                id=f"{vehicle_id}-book",
                                time="Scheduled",
                                agent="Scheduling Bot",
                                vehicle_id=vehicle_id,
                                message=f"Confirmed service appointment {data.get('booking_id')}",
                                type="info"
                            ))

                except Exception:
                    continue

    return activities