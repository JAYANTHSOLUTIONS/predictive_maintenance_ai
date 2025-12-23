import pandas as pd
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Configuration
API_URL = "http://localhost:8000/api/predictive/run"
CSV_FILE = "engine_data.csv"

# 1. Load Data
try:
    df = pd.read_csv(CSV_FILE)
    print(f"📂 Loaded {len(df)} rows from {CSV_FILE}")
except FileNotFoundError:
    print(f"❌ Error: {CSV_FILE} not found.")
    exit()

# 2. Define Fleet
VIRTUAL_FLEET = [
    { "vehicle_id": "V-102", "model": "CityRunner Z1" },
    { "vehicle_id": "V-103", "model": "FreightLiner Pro" },
    { "vehicle_id": "V-104", "model": "HeavyHaul X5" },
    { "vehicle_id": "V-105", "model": "EcoCargo Electric" },
    { "vehicle_id": "V-106", "model": "CityRunner Z1" }
]

def get_critical_payload(vehicle):
    """Generates ONLY Critical/Faulty data."""
    row = df.sample(n=1).iloc[0]
    
    # 🚨 FORCE CRITICAL VALUES
    engine_temp = random.randint(115, 125) # Always Overheating
    oil_psi = random.randint(5, 12)        # Always Low Pressure
    dtc = "P0217"
    
    # Add Battery Voltage (Simulated for 24V Truck System)
    battery_voltage = round(random.uniform(23.5, 25.5), 1)

    return {
        "vehicle_id": vehicle["vehicle_id"],
        "metadata": { "model": vehicle["model"] },
        "engine_temp_c": engine_temp,
        "oil_pressure_psi": oil_psi,
        "rpm": int(row["Engine rpm"]),
        "battery_voltage": battery_voltage, # Added this!
        "dtc_readable": dtc
    }

def send_request(vehicle):
    """Sends ONE request."""
    try:
        data = get_critical_payload(vehicle)
        # Timeout ensures we don't wait forever
        response = requests.post(API_URL, json=data, timeout=10)
        
        # ✅ UPDATED PRINT STATEMENT to show full data
        print(f"🔥 {vehicle['vehicle_id']} (Critical) -> Status {response.status_code} | "
              f"Temp={data['engine_temp_c']}°C | "
              f"Oil={data['oil_pressure_psi']} PSI | "
              f"RPM={data['rpm']} | "
              f"Batt={data['battery_voltage']}V")
        
    except Exception as e:
        print(f"❌ {vehicle['vehicle_id']} Failed: {e}")

# --- MAIN EXECUTION ---
print("🚀 Initializing Virtual Fleet (CRITICAL FAULTS ONLY)...")
start = time.time()

# ⚡ EXECUTE ONCE IN PARALLEL
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(send_request, VIRTUAL_FLEET)

print(f"✨ Critical Alerts sent in {time.time() - start:.2f} seconds.")
print("👋 Exiting simulator.")