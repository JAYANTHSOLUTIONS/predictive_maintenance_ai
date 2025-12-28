import os
import json
import glob
import uuid
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# ✅ FIX: Correct Import from your existing 'nodes/scheduling.py' file
from app.agents.nodes.scheduling import SchedulerService 

# --- 0. LOAD ENVIRONMENT ---
load_dotenv() 

router = APIRouter()

# --- 1. DATA MODELS ---
class BookingRequest(BaseModel):
    vehicle_id: str
    service_date: str
    notes: str

class VoiceLogEntry(BaseModel):
    role: str
    content: str

class VehicleSummary(BaseModel):
    vin: str
    model: str
    location: str
    telematics: str
    predictedFailure: str
    probability: int
    action: str
    scheduled_date: Optional[str] = None
    voice_transcript: Optional[List[VoiceLogEntry]] = None
    engine_temp: Optional[int] = 0
    oil_pressure: Optional[float] = 0.0
    battery_voltage: Optional[float] = 0.0

class ActivityLog(BaseModel):
    id: str
    time: str
    agent: str 
    vehicle_id: str
    message: str
    type: str   # "info", "warning", "alert"

# --- 2. FILE PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data_samples")
LOG_DIR = os.path.join(BASE_DIR, "data_samples")
DATA_FILE = os.path.join(LOG_DIR, "collected_data.json")

# --- 3. HELPER: MOCK GEOCODING ---
def resolve_location(gps_data):
    if not gps_data: return "Unknown"
    lat, lon = gps_data.get("lat", 0), gps_data.get("lon", 0)
    if 28.0 <= lat <= 29.0: return "Delhi, NCR"
    if 18.0 <= lat <= 20.0: return "Mumbai, MH"
    if 12.0 <= lat <= 13.5 and 77.0 <= lon <= 78.0: return "Bangalore, KA"
    if 12.0 <= lat <= 13.5 and 80.0 <= lon <= 81.0: return "Chennai, TN"
    return f"{lat:.2f}, {lon:.2f}"

# --- 4. ENDPOINTS ---

@router.post("/create")
async def create_booking(request: BookingRequest):
    log_path = os.path.join(LOG_DIR, f"run_log_{request.vehicle_id}.json")
    
    if not os.path.exists(log_path):
        log_data = {"vehicle_id": request.vehicle_id}
    else:
        with open(log_path, "r") as f:
            log_data = json.load(f)

    try:
        booking_id = f"BK-{uuid.uuid4().hex[:6].upper()}"
        log_data["customer_decision"] = "accept"
        log_data["booking_id"] = booking_id
        log_data["scheduled_date"] = request.service_date
        log_data["service_notes"] = request.notes
        
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=4)

        return {"status": "success", "booking_id": booking_id, "message": f"Confirmed for {request.service_date}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    Returns the fleet list merged with AI Voice Logs AND Live Telemetry AND Memory Bookings.
    """
    # A. Load Base Fleet (Static Data)
    vehicles = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                vehicles = json.load(f).get("vehicles", {})
        except Exception:
            vehicles = {}

    summary_list = []

    # B. SCAN AI LOGS (Files)
    ai_updates = {}
    if os.path.exists(LOG_DIR):
        log_pattern = os.path.join(LOG_DIR, "run_log_*.json")
        found_logs = glob.glob(log_pattern)
        for log_path in found_logs:
            try:
                with open(log_path, "r") as f:
                    log_data = json.load(f)
                    v_id = log_data.get("vehicle_id")
                    if v_id: ai_updates[v_id] = log_data
            except Exception: continue

    # ✅ FIX: Fetch In-Memory Bookings from SchedulerService (Nodes File)
    memory_bookings = SchedulerService.get_all_bookings()
    active_bookings_map = {b['vin']: b for b in memory_bookings}

    # C. BUILD RESPONSE
    for v_id, v_data in vehicles.items():
        base_tele = v_data.get("telematics", {})
        
        temp = base_tele.get("engine_temp", 90)   
        oil = base_tele.get("oil_pressure", 40.0)
        batt = 24.5
        
        failure = "System Healthy"
        prob = 0
        action = "Monitoring"
        s_date = None
        transcript = None
        
        real_location = resolve_location(base_tele.get("gps_location"))

        # --- 1. MERGE FILE DATA (AI Logs) ---
        if v_id in ai_updates:
            ai_data = ai_updates[v_id]
            prob = ai_data.get("risk_score", 0)
            issues = ai_data.get("detected_issues", [])
            
            if issues: 
                failure = issues[0] if isinstance(issues, list) else str(issues)
            elif ai_data.get("diagnosis"):
                 failure = "Critical Anomaly Detected"

            tele = ai_data.get("telematics_data", {})
            if tele:
                temp = tele.get("engine_temp_c", temp)
                oil = tele.get("oil_pressure_psi", oil)
                batt = tele.get("battery_voltage", batt)

            raw_transcript = ai_data.get("voice_transcript")
            if raw_transcript and isinstance(raw_transcript, list):
                transcript = [
                    {"role": t.get("role", "assistant"), "content": t.get("content", "")} 
                    for t in raw_transcript
                ]

            if prob > 80:
                action = "Critical Alert"

        # --- 2. MERGE MEMORY DATA (Real-time Agent Bookings) ---
        if v_id in active_bookings_map:
            booking_info = active_bookings_map[v_id]
            action = "Service Booked"
            s_date = f"{booking_info['slot_date']} {booking_info['slot_time']}"
        
        elif v_id in ai_updates and ai_updates[v_id].get("booking_id"):
             action = "Service Booked"
             s_date = ai_updates[v_id].get("scheduled_date")


        # 3. Create the Summary Object
        summary_list.append(VehicleSummary(
            vin=v_id,
            model=v_data.get("metadata", {}).get("model", "Unknown Model"),
            location=real_location,
            telematics="Live",
            predictedFailure=failure,
            probability=prob,
            action=action,
            scheduled_date=s_date,
            voice_transcript=transcript,
            engine_temp=temp,
            oil_pressure=oil,
            battery_voltage=batt
        ))
    
    return summary_list

@router.get("/activity", response_model=List[ActivityLog])
async def get_agent_activity():
    activities = []
    if not os.path.exists(LOG_DIR): return []

    log_files = glob.glob(os.path.join(LOG_DIR, "run_log_*.json"))
    log_files.sort(key=os.path.getmtime, reverse=True)

    for filepath in log_files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                vehicle_id = data.get("vehicle_id", "Unknown")
                
                if data.get("diagnosis"):
                    issues = data.get('detected_issues', [])
                    if issues and "None" not in issues:
                        activities.append(ActivityLog(
                            id=f"{vehicle_id}-diag",
                            time="Just now", agent="Diagnosis Agent",
                            vehicle_id=vehicle_id,
                            message=f"Identified issue: {issues[0]}", type="info"
                        ))

                risk_score = data.get("risk_score", 0)
                if risk_score > 50:
                      activities.append(ActivityLog(
                        id=f"{vehicle_id}-risk",
                        time="Just now", agent="Risk Guardian",
                        vehicle_id=vehicle_id,
                        message=f"Escalated high risk profile ({risk_score}%)",
                        type="alert" if risk_score > 80 else "warning"
                    ))
                
                if data.get("voice_transcript"):
                      activities.append(ActivityLog(
                        id=f"{vehicle_id}-voice",
                        time="Just now", agent="Voice Bot",
                        vehicle_id=vehicle_id,
                        message="Outbound call completed.", type="info"
                    ))

                if data.get("booking_id"):
                      activities.append(ActivityLog(
                        id=f"{vehicle_id}-book",
                        time="Scheduled", agent="Scheduling Bot",
                        vehicle_id=vehicle_id,
                        message=f"Confirmed service appointment {data.get('booking_id')}", type="info"
                    ))

        except Exception: continue
    
    # ✅ FIX: Also add Memory Bookings to Activity Log
    memory_bookings = SchedulerService.get_all_bookings()
    for b in memory_bookings:
        activities.insert(0, ActivityLog(
             id=f"{b['vin']}-mem-book",
             time="Just now",
             agent="Scheduling Agent",
             vehicle_id=b['vin'],
             message=f"Auto-Booking Confirmed: {b['booking_id']}",
             type="info"
        ))

    return activities