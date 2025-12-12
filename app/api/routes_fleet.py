import os
import json
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

# Response Model (Matches React Table)
class VehicleSummary(BaseModel):
    vin: str
    model: str
    location: str
    telematics: str
    predictedFailure: str
    probability: int
    action: str

# 1. DEFINE PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data_samples", "collected_data.json")
LOG_DIR = os.path.join(BASE_DIR, "data_samples") # Where run_log_V-101.json lives

@router.get("/status", response_model=List[VehicleSummary])
async def get_fleet_status():
    """
    Aggregates data from:
    1. collected_data.json (The Fleet List)
    2. run_log_{id}.json (The Latest AI Analysis for each truck)
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
            # --- DEFAULT VALUES (If AI hasn't run yet) ---
            failure = "System Healthy"
            prob = 0
            action = "Monitoring"
            
            # --- CHECK FOR AI LOGS ---
            # We look for a file named "run_log_V-101.json"
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
                            failure = issues[0]  # Take the top issue
                        elif prob > 50:
                            failure = "Unknown Anomaly"
                        
                        # 3. Get Action Status
                        decision = ai_result.get("customer_decision")
                        if decision == "accept":
                            action = "Service Booked"
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
                location="Delhi, IN", # Mock location
                telematics="Live",
                predictedFailure=failure,
                probability=prob,
                action=action
            ))
        
        return summary_list

    except Exception as e:
        print(f"Error reading fleet: {e}")
        return []