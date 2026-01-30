import json
import os
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from database import supabase  # ✅ IMPORTED SUPABASE CLIENT

# ✅ CORRECT IMPORT FROM MASTER
try:
    from app.agents.master import master_agent
except ImportError:
    print("⚠️ Warning: Could not import 'master_agent' from 'app.agents.master'")
    master_agent = None

router = APIRouter()

# --- MODELS (UNCHANGED) ---
class PredictiveRequest(BaseModel):
    vehicle_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    engine_temp_c: Optional[int] = 90
    oil_pressure_psi: Optional[float] = 40.0
    rpm: Optional[int] = 1500
    battery_voltage: Optional[float] = 24.0
    dtc_readable: Optional[str] = "None"

class AnalyzeResponse(BaseModel):
    vehicle_id: str
    risk_score: int
    risk_level: str
    diagnosis: str
    customer_script: Optional[str] = None
    booking_id: Optional[str] = None
    manufacturing_insights: Optional[str] = None
    ueba_alerts: Optional[List[Dict[str, Any]]] = []

# --- ENDPOINT ---
@router.post("/run", response_model=AnalyzeResponse)
async def predict_failure(request: PredictiveRequest):
    try:
        print(f"📡 [API] Received Analysis Request for: {request.vehicle_id}")

        if not master_agent:
            raise HTTPException(status_code=500, detail="AI Agent Graph not loaded on Server.")

        # 1. SETUP TELEMATICS (UNCHANGED)
        if request.vehicle_id == "V-101":
            telematics_payload = {"engine_temp_c": 85, "oil_pressure_psi": 45, "rpm": 1200, "battery_voltage": 24.2, "dtc_readable": "None"}
        else:
            telematics_payload = {
                "engine_temp_c": request.engine_temp_c,
                "oil_pressure_psi": request.oil_pressure_psi,
                "rpm": request.rpm,
                "battery_voltage": request.battery_voltage,
                "dtc_readable": request.dtc_readable
            }

        # 2. PREPARE STATE (UNCHANGED)
        initial_state = {
            "vehicle_id": request.vehicle_id,
            "vehicle_metadata": request.metadata,
            "telematics_data": telematics_payload,
            "detected_issues": [],
            "risk_score": 0,
            "diagnosis_report": "",
            "recommended_action": "Wait",
            "priority_level": "Low",
            "voice_transcript": [],
            "manufacturing_recommendations": "",
            "ueba_alert_triggered": False,
            "customer_script": "",
            "customer_decision": "PENDING",
            "selected_slot": None,
            "booking_id": None,
            "error_message": None,
            "feedback_request": None
        }

        # 3. RUN AGENT (UNCHANGED)
        result = master_agent.invoke(initial_state)

        # 4. UEBA & LOGGING (ALTERED FOR SUPABASE)
        ueba_list = []
        if result.get("ueba_alert_triggered"):
            ueba_list.append({"message": "Anomalous telemetry pattern detected"})

        # ✅ NEW: BUILD SUPABASE PAYLOAD
        db_log = {
            "vehicle_id": result.get("vehicle_id"),
            "timestamp_utc": "now()",  # Postgres timestamp
            "engine_temp_c": telematics_payload.get("engine_temp_c"),
            "oil_pressure_psi": telematics_payload.get("oil_pressure_psi"),
            "rpm": telematics_payload.get("rpm"),
            "battery_voltage": telematics_payload.get("battery_voltage"),
            "vibration_level": result.get("priority_level", "NORMAL").upper(),
            "active_dtc_codes": result.get("detected_issues", []),
            "raw_payload": result  # Preserve the full AI JSON output
        }

        # ✅ NEW: INSERT LOG TO CLOUD
        try:
            supabase.table("telematics_logs").insert(db_log).execute()
            
            # ✅ NEW: UPDATE MAIN VEHICLE RISK SCORE
            supabase.table("vehicles").update({
                "risk_score": result.get("risk_score", 0)
            }).eq("id", request.vehicle_id).execute()
            
            print(f"☁️ [Supabase] Log and Risk Score synced for {request.vehicle_id}")
        except Exception as db_err:
            print(f"⚠️ Warning: Cloud sync failed but AI finished: {db_err}")

        # 5. RETURN RESPONSE (UNCHANGED)
        return AnalyzeResponse(
            vehicle_id=result["vehicle_id"],
            risk_score=result.get("risk_score", 0),
            risk_level=result.get("priority_level", "UNKNOWN").upper(), 
            diagnosis=result.get("diagnosis_report", "No diagnosis generated."),
            customer_script=result.get("customer_script"),
            booking_id=result.get("booking_id"),
            manufacturing_insights=result.get("manufacturing_recommendations"),
            ueba_alerts=ueba_list
        )

    except Exception as e:
        print(f"❌ Error in prediction endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))