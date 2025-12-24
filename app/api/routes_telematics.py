import os
import json
from fastapi import APIRouter, HTTPException
# Keep this import for fallback
from app.data.repositories import TelematicsRepo 

router = APIRouter()

# --- SETUP PATH TO LOGS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "data_samples")

@router.get("/{vehicle_id}")
async def get_vehicle_stats(vehicle_id: str):
    """
    Fetches the latest live IoT data for the dashboard gauges.
    Priority: Live Simulator Logs (JSON) -> Static Database (Repo)
    """
    
    # 1. CHECK LIVE SIMULATOR LOGS (Priority for V-102+, BUT EXCLUDE V-101)
    # We explicitly skip this block for V-101 so it always falls through to the Repo.
    if vehicle_id != "V-101":
        json_path = os.path.join(LOG_DIR, f"run_log_{vehicle_id}.json")
        
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                    tele = data.get("telematics_data", {})
                    
                    # Return standardized format for Frontend
                    return {
                        "vehicle_id": vehicle_id,
                        "engine_temp_c": tele.get("engine_temp_c", 0),
                        "oil_pressure_psi": tele.get("oil_pressure_psi", 0.0),
                        "rpm": tele.get("rpm", 0),
                        # ✅ Return Battery so the new card works
                        "battery_voltage": tele.get("battery_voltage", 24.0),
                        "dtc_readable": tele.get("dtc_readable", "None")
                    }
            except Exception as e:
                print(f"⚠️ Error reading log for {vehicle_id}: {e}")

    # 2. FALLBACK TO REPO (This runs for V-101 OR if log is missing)
    data = TelematicsRepo.get_latest_telematics(vehicle_id)
    
    if data:
        # Ensure fallback data also has the fields we need
        if "battery_voltage" not in data:
            data["battery_voltage"] = 24.1
        return data

    # 3. IF TOTALLY MISSING (Prevent Frontend Crash)
    print(f"❌ Vehicle {vehicle_id} not found anywhere. Returning dummy data.")
    return {
        "vehicle_id": vehicle_id,
        "engine_temp_c": 0,
        "oil_pressure_psi": 0,
        "rpm": 0,
        "battery_voltage": 0,
        "dtc_readable": "No Connection"
    }