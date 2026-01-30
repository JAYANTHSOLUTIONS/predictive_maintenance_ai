import os
from fastapi import APIRouter
from database import supabase  # ✅ IMPORTED SUPABASE CLIENT

# Keep this import for fallback (UNCHANGED)
try:
    from app.data.repositories import TelematicsRepo 
except ImportError:
    TelematicsRepo = None

router = APIRouter()

@router.get("/{vehicle_id}")
async def get_vehicle_stats(vehicle_id: str):
    """
    Fetches the latest live IoT data for the dashboard gauges from Supabase.
    Priority: Supabase Cloud Logs -> Static Database (Repo) -> Default Mock
    """
    
    # 1. ✅ CLOUD ROUTE: FETCH LATEST LOG FROM SUPABASE
    try:
        # Querying the telematics_logs table for the absolute latest entry
        response = supabase.table("telematics_logs") \
            .select("*") \
            .eq("vehicle_id", vehicle_id) \
            .order("timestamp_utc", desc=True) \
            .limit(1) \
            .execute()

        if response.data:
            latest = response.data[0]
            
            # Extract values from DB columns
            current_temp = latest.get("engine_temp_c")
            current_oil = latest.get("oil_pressure_psi")

            # ✅ DEBUG: This will show you exactly what is being sent to the Dashboard
            print(f"☁️ [Telematics API] Dashboard Update for {vehicle_id}: Temp={current_temp}, Oil={current_oil}")

            return {
                "vehicle_id": vehicle_id,
                
                # ✅ MAPPING: Ensure these keys match your frontend gauges exactly
                "engine_temp": current_temp if current_temp is not None else 90,       
                "engine_temp_c": current_temp if current_temp is not None else 90,     
                
                "oil_pressure": current_oil if current_oil is not None else 40.0,   
                "oil_pressure_psi": current_oil if current_oil is not None else 40.0,
                
                "rpm": latest.get("rpm", 1000),
                "battery_voltage": latest.get("battery_voltage", 24.0),
                "fuel_level": latest.get("fuel_level_percent", 50),
                
                # Pull first code from the DTC array
                "dtc_readable": latest.get("active_dtc_codes", ["System Healthy"])[0] if latest.get("active_dtc_codes") else "System Healthy",
                "status": "Online (Cloud Sync)"
            }
            
    except Exception as e:
        print(f"⚠️ Supabase Routing Error for {vehicle_id}: {e}")

    # 2. FALLBACK TO REPO (UNCHANGED)
    if TelematicsRepo:
        data = TelematicsRepo.get_latest_telematics(vehicle_id)
        if data:
            print(f"💾 [Telematics API] Falling back to Static Repo for {vehicle_id}")
            if "battery_voltage" not in data:
                data["battery_voltage"] = 24.1
            return data

    # 3. FINAL DEFAULT (IF NO DATA EXISTS)
    return {
        "vehicle_id": vehicle_id,
        "engine_temp": 0,
        "oil_pressure": 0,
        "rpm": 0,
        "battery_voltage": 24.0,
        "dtc_readable": "No Connection"
    }