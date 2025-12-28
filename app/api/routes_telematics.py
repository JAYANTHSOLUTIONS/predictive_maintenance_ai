import os
import json
from fastapi import APIRouter

# Keep this import for fallback
try:
    from app.data.repositories import TelematicsRepo 
except ImportError:
    TelematicsRepo = None

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
    
    # 1. CHECK LIVE SIMULATOR LOGS (Now enabled for ALL vehicles)
    json_path = os.path.join(LOG_DIR, f"run_log_{vehicle_id}.json")
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
                tele = data.get("telematics_data", {})
                
                # ✅ DEBUG: Print to confirm we are reading the file
                print(f"📂 [Telematics API] Reading JSON for {vehicle_id}: Temp={tele.get('engine_temp_c')}")

                return {
                    "vehicle_id": vehicle_id,
                    
                    # ✅ FIX: Map JSON keys ('_c') to Frontend expected keys (standard)
                    "engine_temp": tele.get("engine_temp_c", 90),       # Frontend expects 'engine_temp'
                    "engine_temp_c": tele.get("engine_temp_c", 90),     # Backup
                    
                    "oil_pressure": tele.get("oil_pressure_psi", 40),   # Frontend expects 'oil_pressure'
                    "oil_pressure_psi": tele.get("oil_pressure_psi", 40),
                    
                    "rpm": tele.get("rpm", 1000),
                    "battery_voltage": tele.get("battery_voltage", 24.0),
                    "fuel_level": tele.get("fuel_level_percent", 50),
                    
                    "dtc_readable": tele.get("dtc_readable", "System Healthy"),
                    "status": "Online (AI Monitored)"
                }
        except Exception as e:
            print(f"⚠️ Error reading log for {vehicle_id}: {e}")

    # 2. FALLBACK TO REPO (If file doesn't exist)
    print(f"💾 [Telematics API] JSON not found for {vehicle_id}. Using Repo.")
    if TelematicsRepo:
        data = TelematicsRepo.get_latest_telematics(vehicle_id)
        if data:
            if "battery_voltage" not in data:
                data["battery_voltage"] = 24.1
            return data

    # 3. IF TOTALLY MISSING
    return {
        "vehicle_id": vehicle_id,
        "engine_temp": 0,
        "oil_pressure": 0,
        "rpm": 0,
        "battery_voltage": 24.0,
        "dtc_readable": "No Connection"
    }