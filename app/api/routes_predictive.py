from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Import your Master Agent
from app.agents.master import run_predictive_flow

router = APIRouter()

# --- Request & Response Models ---
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

# --- The Endpoint ---
@router.post("/run", response_model=AnalyzeResponse)
async def predict_failure(request: AnalyzeRequest):
    """
    Triggers the Multi-Agent Workflow for a specific vehicle.
    """
    try:
        print(f"📡 API received request for: {request.vehicle_id}")
        
        # 1. Run the Agent Brain
        result = run_predictive_flow(request.vehicle_id)
        
        # 2. Return JSON to React
        return AnalyzeResponse(
            vehicle_id=result["vehicle_id"],
            risk_score=result.get("risk_score", 0),
            risk_level=result.get("risk_level", "UNKNOWN"),
            diagnosis=result.get("diagnosis_report", "No diagnosis generated."),
            customer_script=result.get("customer_script"),
            booking_id=result.get("booking_id"),
            manufacturing_insights=result.get("manufacturing_recommendations"),
            ueba_alerts=result.get("ueba_alerts", [])
        )
    except Exception as e:
        print(f"❌ Error in prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))