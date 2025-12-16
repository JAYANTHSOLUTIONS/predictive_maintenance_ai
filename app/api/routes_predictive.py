import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# ✅ Correct Import: Points to your master.py orchestrator
from app.agents.master import run_predictive_flow

router = APIRouter()

# --- 1. SETUP PATHS (Crucial for Dashboard Sync) ---
# This ensures we save files where 'routes_fleet.py' can find them
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "data_samples")
os.makedirs(LOG_DIR, exist_ok=True)

# --- 2. MODELS ---
class AnalyzeRequest(BaseModel):
    vehicle_id: str

class AnalyzeResponse(BaseModel):
    vehicle_id: str
    risk_score: int
    risk_level: str
    diagnosis: str
    customer_script: Optional[str] = None
    booking_id: Optional[str] = None
    manufacturing_insights: Optional[str] = None
    ueba_alerts: List[Dict[str, Any]] = []

# --- 3. ENDPOINT ---
@router.post("/run", response_model=AnalyzeResponse)
async def predict_failure(request: AnalyzeRequest):
    """
    Triggers the Multi-Agent Workflow AND saves the result for the dashboard.
    """
    try:
        print(f"📡 API received request for: {request.vehicle_id}")
        
        # A. Run the Agent Brain (This triggers scheduling.py logic)
        result = run_predictive_flow(request.vehicle_id)
        
        # B. SAVE TO JSON (The Bridge to the Dashboard)
        # We must save this file so routes_fleet.py can read the new booking!
        log_path = os.path.join(LOG_DIR, f"run_log_{result['vehicle_id']}.json")
        
        log_data = {
            "vehicle_id": result.get("vehicle_id"),
            "risk_score": result.get("risk_score", 0),
            "detected_issues": result.get("detected_issues", []),
            "diagnosis": result.get("diagnosis_report"),
            "customer_decision": result.get("customer_decision"),
            
            # These fields come from scheduling.py
            "booking_id": result.get("booking_id"),
            "scheduled_date": result.get("selected_slot"), 
            
            "manufacturing_recommendations": result.get("manufacturing_recommendations"),
            "timestamp": "Just now"
        }

        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=4)
        print(f"💾 [System] Saved run log to {log_path}")

        # C. Return JSON to React (Immediate "Popup" Response)
        return AnalyzeResponse(
            vehicle_id=result["vehicle_id"],
            risk_score=result.get("risk_score", 0),
            # Map 'priority_level' from state to 'risk_level' for the UI
            risk_level=result.get("priority_level", "UNKNOWN"), 
            diagnosis=result.get("diagnosis_report", "No diagnosis generated."),
            customer_script=result.get("customer_script"),
            booking_id=result.get("booking_id"),
            manufacturing_insights=result.get("manufacturing_recommendations"),
            ueba_alerts=result.get("ueba_alerts", [])
        )

    except Exception as e:
        print(f"❌ Error in prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))