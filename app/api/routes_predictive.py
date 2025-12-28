import json
import os
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ✅ CORRECT IMPORT FROM MASTER
try:
    from app.agents.master import master_agent
except ImportError:
    print("⚠️ Warning: Could not import 'master_agent' from 'app.agents.master'")
    master_agent = None

router = APIRouter()

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "data_samples")
os.makedirs(LOG_DIR, exist_ok=True)

# --- MODELS ---
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

        # 1. SETUP TELEMATICS
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

        # 2. PREPARE STATE
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
            # ✅ Add missing optional fields to prevent validation error
            "customer_script": "",
            "customer_decision": "PENDING",
            "selected_slot": None,
            "booking_id": None,
            "error_message": None,
            "feedback_request": None
        }

        # 3. RUN AGENT
        result = master_agent.invoke(initial_state)

        # 4. UEBA & LOGGING
        ueba_list = []
        if result.get("ueba_alert_triggered"):
            ueba_list.append({"message": "Anomalous telemetry pattern detected"})

        log_path = os.path.join(LOG_DIR, f"run_log_{request.vehicle_id}.json")
        log_data = {
            "vehicle_id": result.get("vehicle_id"),
            "risk_score": result.get("risk_score", 0),
            "detected_issues": result.get("detected_issues", []),
            "diagnosis": result.get("diagnosis_report"),
            "telematics_data": telematics_payload,
            "customer_decision": result.get("customer_decision"),
            "booking_id": result.get("booking_id"),
            "scheduled_date": result.get("selected_slot"),
            "voice_transcript": result.get("voice_transcript"),
            "manufacturing_recommendations": result.get("manufacturing_recommendations"),
            "ueba_alerts": ueba_list,
            "timestamp": "Just now"
        }

        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=4)
        print(f"💾 [System] Saved run log to {log_path}")

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