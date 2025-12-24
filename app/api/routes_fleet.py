import os
import json
import glob
from fastapi import APIRouter
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# --- 0. LOAD ENVIRONMENT ---
load_dotenv() 

router = APIRouter()

# --- 1. DATA MODELS ---
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
    # ✅ NEW FIELDS (Crucial for your new Table)
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
# Adjust path to find the root folder from app/api/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data_samples")

# Fetch from ENV or use Default
LOG_DIR = os.getenv("DATA_SAMPLES_DIR", DEFAULT_DATA_DIR)
DATA_FILE = os.path.join(LOG_DIR, "collected_data.json")

# --- 3. HELPER: MOCK GEOCODING ---
def resolve_location(gps_data):
    """Maps lat/lon to a city name for the table display."""
    if not gps_data:
        return "Unknown"
    
    lat = gps_data.get("lat", 0)
    lon = gps_data.get("lon", 0)

    if 28.0 <= lat <= 29.0: return "Delhi, NCR"
    if 18.0 <= lat <= 20.0: return "Mumbai, MH"
    if 12.0 <= lat <= 13.5 and 77.0 <= lon <= 78.0: return "Bangalore, KA"
    if 12.0 <= lat <= 13.5 and 80.0 <= lon <= 81.0: return "Chennai, TN"
    if 30.0 <= lat <= 32.0: return "Shimla, HP"
    
    return f"{lat:.2f}, {lon:.2f}"

# --- 4. ENDPOINTS ---

@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    Returns the fleet list merged with AI Voice Logs AND Live Telemetry.
    """
    # A. Load Base Fleet (Static Data)
    vehicles = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                vehicles = data.get("vehicles", {})
        except Exception:
            vehicles = {}

    summary_list = []

    # B. SCAN AI LOGS (Dynamic Data from Simulator)
    ai_updates = {}
    if os.path.exists(LOG_DIR):
        log_pattern = os.path.join(LOG_DIR, "run_log_*.json")
        found_logs = glob.glob(log_pattern)

        for log_path in found_logs:
            try:
                with open(log_path, "r") as f:
                    log_data = json.load(f)
                    v_id = log_data.get("vehicle_id")
                    if v_id:
                        ai_updates[v_id] = log_data
            except Exception as e:
                print(f"❌ Error reading log {log_path}: {e}")

    # C. BUILD RESPONSE
    for v_id, v_data in vehicles.items():
        # Defaults
        failure = "System Healthy"
        prob = 0
        action = "Monitoring"
        s_date = None
        transcript = None
        
        # ✅ NEW DEFAULTS FOR TELEMETRY
        temp = 0
        oil = 0.0
        batt = 24.0 # Default for trucks
        
        # 1. Get Real Location
        real_location = resolve_location(v_data.get("telematics", {}).get("gps_location"))

        # 2. OVERWRITE WITH AI DATA if available
        if v_id in ai_updates:
            ai_data = ai_updates[v_id]
            
            # Update Risk & Failure
            prob = ai_data.get("risk_score", 0)
            issues = ai_data.get("detected_issues", [])
            
            if issues: 
                failure = issues[0] if isinstance(issues, list) else str(issues)
            elif ai_data.get("diagnosis"):
                 failure = "Critical Anomaly Detected"

            # ✅ EXTRACT LIVE TELEMETRY (This is what you were missing!)
            tele = ai_data.get("telematics_data", {})
            temp = tele.get("engine_temp_c", 0)
            oil = tele.get("oil_pressure_psi", 0.0)
            batt = tele.get("battery_voltage", 24.5)

            # Map Transcript
            raw_transcript = ai_data.get("voice_transcript")
            if raw_transcript and isinstance(raw_transcript, list):
                transcript = [
                    {"role": t.get("role", "assistant"), "content": t.get("content", "")} 
                    for t in raw_transcript
                ]

            # Update Action
            if ai_data.get("booking_id"):
                action = "Service Booked"
            elif prob > 80:
                action = "Critical Alert"

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
            # ✅ PASS NEW DATA
            engine_temp=temp,
            oil_pressure=oil,
            battery_voltage=batt
        ))
    
    return summary_list

@router.get("/activity", response_model=List[ActivityLog])
async def get_agent_activity():
    """
    Scans all run_logs to generate a timeline of Agent actions for the Dashboard.
    """
    activities = []
    
    if not os.path.exists(LOG_DIR):
        return []

    # Get all logs and sort by modification time (newest first)
    log_files = glob.glob(os.path.join(LOG_DIR, "run_log_*.json"))
    log_files.sort(key=os.path.getmtime, reverse=True)

    for filepath in log_files:
        filename = os.path.basename(filepath)
        vehicle_id = filename.replace("run_log_", "").replace(".json", "")
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                
                # 1. Diagnosis Agent Log
                if data.get("diagnosis"):
                    issues = data.get('detected_issues', [])
                    if issues and "None" not in issues:
                        activities.append(ActivityLog(
                            id=f"{vehicle_id}-diag",
                            time="Just now", 
                            agent="Diagnosis Agent",
                            vehicle_id=vehicle_id,
                            message=f"Identified issue: {issues[0]}",
                            type="info"
                        ))

                # 2. Risk Agent Log
                risk_score = data.get("risk_score", 0)
                if risk_score > 50:
                     activities.append(ActivityLog(
                        id=f"{vehicle_id}-risk",
                        time="Just now",
                        agent="Risk Guardian",
                        vehicle_id=vehicle_id,
                        message=f"Escalated high risk profile ({risk_score}%)",
                        type="alert" if risk_score > 80 else "warning"
                    ))
                
                # 3. Voice Agent Log
                if data.get("voice_transcript"):
                     activities.append(ActivityLog(
                        id=f"{vehicle_id}-voice",
                        time="Just now",
                        agent="Voice Bot",
                        vehicle_id=vehicle_id,
                        message="Outbound call completed. Appointment negotiated.",
                        type="info"
                    ))

                # 4. Scheduler Agent Log
                if data.get("booking_id"):
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