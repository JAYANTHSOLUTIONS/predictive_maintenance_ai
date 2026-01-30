import os
import json
import uuid
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
from database import supabase  # ✅ IMPORTED SUPABASE CLIENT

# ✅ KEEP: Import from your existing 'nodes/scheduling.py' file
from app.agents.nodes.scheduling import SchedulerService 

# --- 0. LOAD ENVIRONMENT ---
load_dotenv() 

router = APIRouter()

# --- 1. DATA MODELS (UNCHANGED) ---
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

# --- 3. HELPER: MOCK GEOCODING (UNCHANGED) ---
def resolve_location(gps_data):
    if not gps_data: return "Unknown"
    # Logic to handle both dict (GPS) and flat columns (DB)
    lat = gps_data.get("lat") or gps_data.get("gps_lat", 0)
    lon = gps_data.get("lon") or gps_data.get("gps_lon", 0)
    
    if 28.0 <= lat <= 29.0: return "Delhi, NCR"
    if 18.0 <= lat <= 20.0: return "Mumbai, MH"
    if 12.0 <= lat <= 13.5 and 77.0 <= lon <= 78.0: return "Bangalore, KA"
    if 12.0 <= lat <= 13.5 and 80.0 <= lon <= 81.0: return "Chennai, TN"
    return f"{lat:.2f}, {lon:.2f}"

# --- 4. ENDPOINTS ---

@router.post("/create")
async def create_booking(request: BookingRequest):
    """
    REPLACED: Local JSON update with Supabase Table update.
    """
    try:
        booking_id = f"BK-{uuid.uuid4().hex[:6].upper()}"
        
        # ✅ UPDATE SUPABASE: Change status and set service date
        supabase.table("vehicles").update({
            "status": "scheduled",
            "next_service_due": request.service_date
        }).eq("id", request.vehicle_id).execute()

        return {"status": "success", "booking_id": booking_id, "message": f"Confirmed for {request.service_date}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    REPLACED: Local JSON globbing with Supabase Relational Query.
    """
    try:
        # ✅ FETCH FROM CLOUD: Get all vehicles + their most recent log entry
        response = supabase.table("vehicles") \
            .select("*, telematics_logs(*)") \
            .order("timestamp_utc", foreign_table="telematics_logs", desc=True) \
            .limit(1, foreign_table="telematics_logs") \
            .execute()

        summary_list = []

        # ✅ KEEP: Fetch In-Memory Bookings from SchedulerService
        memory_bookings = SchedulerService.get_all_bookings()
        active_bookings_map = {b['vin']: b for b in memory_bookings}

        # ✅ BUILD RESPONSE using DB results
        for row in response.data:
            v_id = row['id']
            logs = row.get("telematics_logs", [])
            latest_log = logs[0] if logs else {}
            
            # Extract Telematics
            temp = latest_log.get("engine_temp_c", 90)   
            oil = latest_log.get("oil_pressure_psi", 40.0)
            batt = latest_log.get("battery_voltage", 24.5)
            
            # Extract AI Diagnosis from raw_payload (the agent's output)
            raw_ai = latest_log.get("raw_payload", {})
            failure = "System Healthy"
            prob = row.get("risk_score", 0) 
            action = row.get("status", "monitoring").capitalize()
            s_date = row.get("next_service_due")
            transcript = None
            
            # Use original resolve_location with DB flat columns
            real_location = resolve_location({
                "lat": latest_log.get("gps_lat"), 
                "lon": latest_log.get("gps_lon")
            })

            # Handle DTCs and transcripts stored in the log
            if logs:
                issues = latest_log.get("active_dtc_codes", [])
                if issues: 
                    failure = issues[0]
                
                raw_transcript = raw_ai.get("voice_transcript")
                if raw_transcript and isinstance(raw_transcript, list):
                    transcript = [
                        {"role": t.get("role", "assistant"), "content": t.get("content", "")} 
                        for t in raw_transcript
                    ]
                
                if raw_ai.get("risk_score", 0) > 80:
                    action = "Critical Alert"

            # --- KEEP: MERGE MEMORY DATA (Real-time Agent Bookings) ---
            if v_id in active_bookings_map:
                booking_info = active_bookings_map[v_id]
                action = "Service Booked"
                s_date = f"{booking_info['slot_date']} {booking_info['slot_time']}"

            summary_list.append(VehicleSummary(
                vin=v_id,
                model=row.get("model_name", "Unknown Model"),
                location=real_location,
                telematics="Live" if logs else "Offline",
                predictedFailure=failure,
                probability=prob,
                action=action,
                scheduled_date=str(s_date) if s_date else None,
                voice_transcript=transcript,
                engine_temp=temp,
                oil_pressure=oil,
                battery_voltage=batt
            ))
        
        return summary_list
    except Exception as e:
        print(f"ERROR: {e}")
        return []

@router.get("/activity", response_model=List[ActivityLog])
async def get_agent_activity():
    """
    REPLACED: run_log_*.json scanning with Supabase Telematics Log query.
    """
    # ✅ FETCH FROM CLOUD: Get latest 15 logs that contain diagnostic data
    response = supabase.table("telematics_logs") \
        .select("*") \
        .order("timestamp_utc", desc=True) \
        .limit(15) \
        .execute()

    activities = []
    for log in response.data:
        v_id = log["vehicle_id"]
        raw = log.get("raw_payload", {})
        
        # Identified issues
        if log.get("active_dtc_codes"):
            activities.append(ActivityLog(
                id=f"{v_id}-diag-{uuid.uuid4().hex[:4]}",
                time="Just now", agent="Diagnosis Agent",
                vehicle_id=v_id,
                message=f"Identified issue: {log['active_dtc_codes'][0]}", type="info"
            ))

        # Risk Score escalations
        risk = raw.get("risk_score", 0)
        if risk > 50:
            activities.append(ActivityLog(
                id=f"{v_id}-risk-{uuid.uuid4().hex[:4]}",
                time="Just now", agent="Risk Guardian",
                vehicle_id=v_id,
                message=f"Escalated high risk profile ({risk}%)",
                type="alert" if risk > 80 else "warning"
            ))
    
    # ✅ KEEP: Also add Memory Bookings to Activity Log
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