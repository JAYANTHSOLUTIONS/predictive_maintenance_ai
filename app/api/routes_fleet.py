import uuid
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database import supabase  # ✅ Supabase Client

router = APIRouter()

# --- 1. DATA MODELS ---

# ✅ NEW: Owner Details Model
class OwnerInfo(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    organization_name: Optional[str] = None

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
    
    # ✅ UPDATE: Added Owner Field (Nested Object)
    owners: Optional[OwnerInfo] = None 

class ActivityLog(BaseModel):
    id: str
    time: str
    agent: str 
    vehicle_id: str
    message: str
    type: str   # "info", "warning", "alert"

# --- 2. HELPER: GEOCODING ---
def resolve_location(lat, lon):
    if not lat or not lon: return "Unknown"
    if 28.0 <= lat <= 29.0: return "Delhi, NCR"
    if 18.0 <= lat <= 20.0: return "Mumbai, MH"
    if 12.0 <= lat <= 13.5 and 77.0 <= lon <= 78.0: return "Bangalore, KA"
    if 12.0 <= lat <= 13.5 and 80.0 <= lon <= 81.0: return "Chennai, TN"
    if 10.5 <= lat <= 11.5: return "Coimbatore, TN" 
    if 9.5 <= lat <= 10.5: return "Madurai, TN"
    return f"{lat:.2f}, {lon:.2f}"

# --- 3. ENDPOINTS ---

@router.post("/create")
async def create_booking(request: BookingRequest):
    """
    Updates the 'vehicles' table directly.
    """
    try:
        booking_id = f"BK-{uuid.uuid4().hex[:6].upper()}"
        
        response = supabase.table("vehicles").update({
            "status": "scheduled",
            "next_service_due": request.service_date,
        }).eq("id", request.vehicle_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Vehicle ID not found")

        return {
            "status": "success", 
            "booking_id": booking_id, 
            "message": f"Confirmed for {request.service_date}"
        }
    except Exception as e:
        print(f"❌ DB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    Joins 'vehicles', 'owners', and 'telematics_logs' to get the latest state.
    """
    try:
        # 1. Get all vehicles WITH Owner details
        # ✅ UPGRADE: .select("*, owners(*)") performs the JOIN
        vehicles_response = supabase.table("vehicles") \
            .select("*, owners(*)") \
            .execute()
        
        summary_list = []

        for vehicle in vehicles_response.data:
            v_id = vehicle['id']
            
            # 2. Get Latest Log for this vehicle
            log_response = supabase.table("telematics_logs") \
                .select("*") \
                .eq("vehicle_id", v_id) \
                .order("timestamp_utc", desc=True) \
                .limit(1) \
                .execute()
            
            latest_log = log_response.data[0] if log_response.data else {}
            raw_ai = latest_log.get("raw_payload", {})
            
            # --- MAP DB COLUMNS ---
            temp = latest_log.get("engine_temp_c", 0)   
            oil = latest_log.get("oil_pressure_psi", 0.0)
            batt = latest_log.get("battery_voltage", 0.0)
            
            # Issues
            db_dtcs = latest_log.get("active_dtc_codes", [])
            failure = db_dtcs[0] if db_dtcs else "System Healthy"
            if failure == "System Healthy":
                failure = raw_ai.get("detected_issues", ["System Healthy"])[0]

            prob = raw_ai.get("risk_score", 0) 
            
            # Status & Action
            db_status = vehicle.get("status", "active")
            s_date = vehicle.get("next_service_due")

            if db_status == "scheduled":
                action = "Service Booked"
            elif prob > 80:
                action = "Critical Alert"
            else:
                action = "Monitoring"
            
            # Location
            real_location = resolve_location(
                latest_log.get("gps_lat"), 
                latest_log.get("gps_lon")
            )

            # Transcripts
            transcript = None
            raw_transcript = raw_ai.get("voice_transcript")
            if raw_transcript and isinstance(raw_transcript, list):
                transcript = [
                    {"role": t.get("role", "assistant"), "content": t.get("content", "")} 
                    for t in raw_transcript
                ]
            
            # ✅ Extract Owner Data safely
            owner_data = vehicle.get("owners")

            summary_list.append(VehicleSummary(
                vin=v_id,
                model=vehicle.get("model_name", "Unknown Model"),
                location=real_location,
                telematics="Live" if latest_log else "Offline",
                predictedFailure=failure,
                probability=prob,
                action=action,
                scheduled_date=str(s_date) if s_date else None,
                voice_transcript=transcript,
                engine_temp=temp,
                oil_pressure=oil,
                battery_voltage=batt,
                owners=owner_data  # ✅ Passing the nested owner object
            ))
        
        return summary_list
    except Exception as e:
        print(f"❌ Error fetching fleet status: {e}")
        return []

@router.get("/activity", response_model=List[ActivityLog])
async def get_agent_activity():
    """
    Reads from 'telematics_logs' for history.
    """
    try:
        response = supabase.table("telematics_logs") \
            .select("*") \
            .order("timestamp_utc", desc=True) \
            .limit(20) \
            .execute()

        activities = []
        for log in response.data:
            v_id = log["vehicle_id"]
            raw = log.get("raw_payload", {})
            ts = log.get("timestamp_utc", "Just now")
            
            # 1. Fault Detected
            if log.get("active_dtc_codes"):
                activities.append(ActivityLog(
                    id=f"{v_id}-diag-{log['log_id']}",
                    time=ts, 
                    agent="Diagnosis Agent",
                    vehicle_id=v_id,
                    message=f"Identified issue: {log['active_dtc_codes'][0]}", 
                    type="info"
                ))

            # 2. High Risk
            risk = raw.get("risk_score", 0)
            if risk > 50:
                activities.append(ActivityLog(
                    id=f"{v_id}-risk-{log['log_id']}",
                    time=ts, 
                    agent="Risk Guardian",
                    vehicle_id=v_id,
                    message=f"Escalated high risk profile ({risk}%)",
                    type="alert" if risk > 80 else "warning"
                ))
            
            # 3. Booking Confirmation (Derived from raw payload if available)
            if raw.get("booking_id"):
                 activities.append(ActivityLog(
                    id=f"{v_id}-book-{log['log_id']}",
                    time=ts, 
                    agent="Scheduling Agent",
                    vehicle_id=v_id,
                    message=f"Auto-Booking Confirmed: {raw.get('booking_id')}",
                    type="info"
                ))
        
        return activities
    except Exception as e:
        print(f"❌ Error fetching activity: {e}")
        return []