import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ✅ IMPORT THE AGENT GRAPH DIRECTLY
# We use master_agent.invoke() so we can inject the live Simulator data
from app.agents.master import master_agent

router = APIRouter()

# --- 1. SETUP PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "data_samples")
os.makedirs(LOG_DIR, exist_ok=True)

# --- 2. FLEXIBLE INPUT MODEL ---
# This works for BOTH V-101 (ID only) and Simulator (Full Data)
class PredictiveRequest(BaseModel):
    vehicle_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # ✅ Made Optional for V-101 compatibility
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

# --- 3. ENDPOINT ---
@router.post("/run", response_model=AnalyzeResponse)
async def predict_failure(request: PredictiveRequest):
    """
    Handles both manual V-101 checks and live Simulator streams.
    """
    try:
        print(f"📡 API received request for: {request.vehicle_id}")

        # --- LOGIC SPLIT ---
        # 1. SETUP TELEMATICS DATA
        if request.vehicle_id == "V-101":
            # 🛠️ V-101 LOGIC: Use Defaults (Healthy/Test Mode)
            telematics_payload = {
                "engine_temp_c": 85,
                "oil_pressure_psi": 45,
                "rpm": 1200,
                "battery_voltage": 24.2,
                "dtc_readable": "None"
            }
        else:
            # 🚛 OTHER VEHICLES: Use Live Simulator Data
            telematics_payload = {
                "engine_temp_c": request.engine_temp_c,
                "oil_pressure_psi": request.oil_pressure_psi,
                "rpm": request.rpm,
                "battery_voltage": request.battery_voltage,
                "dtc_readable": request.dtc_readable
            }

        # 2. PREPARE AGENT STATE
        initial_state = {
            "vehicle_id": request.vehicle_id,
            "vehicle_metadata": request.metadata,
            "telematics_data": telematics_payload, # ✅ Injected here
            "detected_issues": [],
            "risk_score": 0,
            "diagnosis_report": "",
            "recommended_action": "Wait",
            "priority_level": "Low",
            "voice_transcript": [],
            "manufacturing_recommendations": "",
            "ueba_alert_triggered": False
        }

        # 3. RUN THE AI BRAIN
        result = master_agent.invoke(initial_state)

        # 4. UEBA LOGIC (Security Check)
        ueba_list = []
        if result.get("ueba_alert_triggered"):
            ueba_list.append({"message": "Anomalous telemetry pattern detected (Spoofing Risk)"})

        # 5. SAVE TO JSON (For Dashboard)
        log_path = os.path.join(LOG_DIR, f"run_log_{request.vehicle_id}.json")
        
        log_data = {
            "vehicle_id": result.get("vehicle_id"),
            "risk_score": result.get("risk_score", 0),
            "detected_issues": result.get("detected_issues", []),
            "diagnosis": result.get("diagnosis_report"),
            "telematics_data": telematics_payload, # ✅ Save the data we used
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

        # 6. RETURN RESPONSE
        return AnalyzeResponse(
            vehicle_id=result["vehicle_id"],
            risk_score=result.get("risk_score", 0),
            risk_level=result.get("priority_level", "UNKNOWN"), 
            diagnosis=result.get("diagnosis_report", "No diagnosis generated."),
            customer_script=result.get("customer_script"),
            booking_id=result.get("booking_id"),
            manufacturing_insights=result.get("manufacturing_recommendations"),
            ueba_alerts=ueba_list
        )

    except Exception as e:
        print(f"❌ Error in prediction endpoint: {e}")
        # Print detailed traceback in terminal for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))