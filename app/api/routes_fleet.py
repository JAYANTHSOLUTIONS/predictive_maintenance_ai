import os
import json
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

# 1. RESPONSE MODEL (Updated with scheduled_date)
class VehicleSummary(BaseModel):
    vin: str
    model: str
    location: str
    telematics: str
    predictedFailure: str
    probability: int
    action: str
    scheduled_date: Optional[str] = None  # <--- NEW FIELD

# 2. PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data_samples", "collected_data.json")
LOG_DIR = os.path.join(BASE_DIR, "data_samples")

@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    Returns the fleet list merged with AI logs and scheduling data.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        # Load the list of vehicles
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        
        vehicles = data.get("vehicles", {})
        summary_list = []

        for v_id, v_data in vehicles.items():
            # --- DEFAULT VALUES ---
            failure = "System Healthy"
            prob = 0
            action = "Monitoring"
            s_date = None # <--- Variable for date
            
            # --- CHECK FOR AI LOGS ---
            log_path = os.path.join(LOG_DIR, f"run_log_{v_id}.json")
            
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r") as log_f:
                        ai_result = json.load(log_f)
                        
                        # 1. Get Probability
                        prob = ai_result.get("risk_score", 0)
                        
                        # 2. Get Predicted Failure
                        issues = ai_result.get("detected_issues", [])
                        if issues:
                            failure = issues[0]
                        elif prob > 50:
                            failure = "Unknown Anomaly"
                        
                        # 3. Get Action Status & Date
                        decision = ai_result.get("customer_decision")
                        if decision == "accept":
                            action = "Service Booked"
                            s_date = ai_result.get("scheduled_date") # <--- READ DATE FROM LOG
                        elif decision == "reject":
                            action = "Customer Contacted"
                        elif prob > 70:
                            action = "Alert Sent"
                            
                except Exception as e:
                    print(f"Error reading log for {v_id}: {e}")

            # --- BUILD SUMMARY ---
            summary_list.append(VehicleSummary(
                vin=v_id,
                model=v_data.get("metadata", {}).get("model", "HeavyHaul X5"),
                location="Delhi, IN",
                telematics="Live",
                predictedFailure=failure,
                probability=prob,
                action=action,
                scheduled_date=s_date # <--- PASS TO FRONTEND
            ))
        
        return summary_list

    except Exception as e:
        print(f"Error reading fleet: {e}")
        return []