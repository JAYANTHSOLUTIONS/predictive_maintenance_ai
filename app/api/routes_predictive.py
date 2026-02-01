import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from database import supabase  # ✅ IMPORTED SUPABASE CLIENT

# ✅ IMPORT YOUR AGENT
try:
    from app.agents.master import master_agent
except ImportError:
    print("⚠️ Warning: Could not import 'master_agent'")
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
            raise HTTPException(status_code=500, detail="AI Agent Graph not loaded.")

        # 1. SETUP TELEMATICS
        telematics_payload = {
            "engine_temp_c": request.engine_temp_c,
            "oil_pressure_psi": request.oil_pressure_psi,
            "rpm": request.rpm,
            "battery_voltage": request.battery_voltage,
            "dtc_readable": request.dtc_readable
        }

        # 2. PREPARE STATE (Same as your mock logic)
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

        # 3. RUN AGENT
        result = master_agent.invoke(initial_state)

        # 4. UEBA LOGGING
        ueba_list = []
        if result.get("ueba_alert_triggered"):
            ueba_list.append({"message": "Anomalous telemetry pattern detected"})

        # --- ✅ ENTERPRISE UPDATE: PERSIST TO SUPABASE ---
        
        # Prepare the row for 'telematics_logs'
        db_log = {
            "vehicle_id": request.vehicle_id,
            "timestamp_utc": datetime.utcnow().isoformat(),
            
            # Map standard columns
            "engine_temp_c": telematics_payload.get("engine_temp_c"),
            "oil_pressure_psi": telematics_payload.get("oil_pressure_psi"),
            "rpm": telematics_payload.get("rpm"),
            "battery_voltage": telematics_payload.get("battery_voltage"),
            
            # Map AI Insights
            "vibration_level": result.get("priority_level", "NORMAL").upper(),
            "active_dtc_codes": result.get("detected_issues", []), # Stored as Array
            
            # Map Full JSON Payload (The 'Brain' Dump)
            "raw_payload": result 
        }

        try:
            # A. Insert Log
            supabase.table("telematics_logs").insert(db_log).execute()
            
            # B. Update Vehicle Risk Score (So the Fleet Dashboard sees it instantly)
            supabase.table("vehicles").update({
                "risk_score": result.get("risk_score", 0),
                # If risk is critical, maybe auto-update status?
                # "status": "alert" if result.get("risk_score", 0) > 80 else "active"
            }).eq("id", request.vehicle_id).execute()
            
            print(f"☁️ [Supabase] Synced AI Analysis for {request.vehicle_id}")
            
        except Exception as db_err:
            # IMPORTANT: Don't crash the API if DB fails, but log it.
            print(f"⚠️ Warning: Cloud sync failed: {db_err}")

        # 5. RETURN RESPONSE
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