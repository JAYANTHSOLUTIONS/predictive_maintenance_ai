import os
from fastapi import APIRouter
from database import supabase  # ✅ IMPORTED SUPABASE CLIENT

# Keep this import for fallback/mock data if DB is empty
try:
    from app.data.repositories import TelematicsRepo 
except ImportError:
    TelematicsRepo = None

router = APIRouter()

@router.get("/{vehicle_id}")
async def get_vehicle_stats(vehicle_id: str):
    """
    ENTERPRISE LOGIC: 
    1. Try Fetching Live Cloud Data (Supabase)
    2. Fallback to Local Repository (Mock/Cache)
    3. Return Default Zeros
    """
    
    # 1. ✅ CLOUD ROUTE
    try:
        # Fetch the MOST RECENT log for this vehicle
        response = supabase.table("telematics_logs") \
            .select("*") \
            .eq("vehicle_id", vehicle_id) \
            .order("timestamp_utc", desc=True) \
            .limit(1) \
            .execute()

        if response.data:
            latest = response.data[0]
            
            # Extract standard columns
            current_temp = latest.get("engine_temp_c", 0)
            current_oil = latest.get("oil_pressure_psi", 0.0)
            
            print(f"☁️ [Telematics] Serving Cloud Data for {vehicle_id}")

            return {
                "vehicle_id": vehicle_id,
                
                # Gauge Data
                "engine_temp": current_temp,       
                "engine_temp_c": current_temp,     
                "oil_pressure": current_oil,   
                "oil_pressure_psi": current_oil,
                "rpm": latest.get("rpm", 0),
                "battery_voltage": latest.get("battery_voltage", 0.0),
                "fuel_level": latest.get("fuel_level_percent", 0),
                
                # Diagnostics
                "dtc_readable": latest.get("active_dtc_codes", ["Healthy"])[0] 
                                if latest.get("active_dtc_codes") else "Healthy",
                
                "status": "Online (Cloud Sync)"
            }
            
    except Exception as e:
        print(f"⚠️ Supabase Fetch Error for {vehicle_id}: {e}")

    # 2. FALLBACK TO REPO (Mock Data)
    # This ensures your frontend still works if you haven't populated the DB yet
    if TelematicsRepo:
        data = TelematicsRepo.get_latest_telematics(vehicle_id)
        if data:
            print(f"💾 [Telematics] Using Static Fallback for {vehicle_id}")
            return data

    # 3. IF TOTALLY MISSING
    return {
        "vehicle_id": vehicle_id,
        "engine_temp": 0,
        "oil_pressure": 0,
        "rpm": 0,
        "status": "No Connection"
    }