import sys
import os
import json
import random
import time

# ✅ STEP 1: SOLVE IMPORT ERROR
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    import paho.mqtt.client as mqtt
    from database import supabase 
except ImportError as e:
    print(f"❌ Initialization Error: {e}")
    sys.exit(1)

# --- CONFIGURATION ---
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "hackathon/truck/v101/telematics"

# --- DATA SIMULATION ENGINE ---
def enrich_telematics(real_temp, real_oil):
    if real_temp > 105:
        sim_rpm = random.randint(3500, 4500)
    elif real_oil < 20:
        sim_rpm = random.randint(400, 900)
    else:
        sim_rpm = random.randint(1200, 2200)

    if sim_rpm > 4000 or real_oil < 15:
        sim_vibration = "HIGH"
        vib_hz = random.uniform(50.5, 80.0)
    else:
        sim_vibration = "NORMAL"
        vib_hz = random.uniform(10.0, 25.0)

    sim_voltage = round(random.uniform(21.5, 23.0), 1) if sim_rpm < 600 else round(random.uniform(24.1, 25.5), 1)

    return {
        "rpm": sim_rpm,
        "vibration_level": sim_vibration,
        "vibration_hz": round(vib_hz, 2),
        "battery_voltage": sim_voltage,
        "fuel_level_percent": random.randint(40, 65),
        "gps_location": {"lat": 28.7041, "lon": 77.1025}
    }

# --- MQTT HANDLERS ---
def on_connect(client, userdata, flags, rc):
    print(f"📡 Connected to MQTT! Listening for Wokwi Data...")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        v_id = payload.get("vehicle_id", "V-101")
        real_temp = payload.get("engine_temp_c", 0)
        real_oil = payload.get("oil_pressure_psi", 0)
        real_codes = payload.get("active_dtc_codes", [])

        # Enrich the raw data
        rich_data = enrich_telematics(real_temp, real_oil)

        # ✅ STEP 2: BUILD DB PAYLOAD
        db_payload = {
            "vehicle_id": v_id,
            "timestamp_utc": "now()",
            "engine_temp_c": real_temp,
            "oil_pressure_psi": real_oil,
            "rpm": rich_data["rpm"],
            "battery_voltage": rich_data["battery_voltage"],
            "vibration_level": rich_data["vibration_level"],
            "vibration_hz": rich_data["vibration_hz"],
            "fuel_level_percent": rich_data["fuel_level_percent"],
            "gps_lat": rich_data["gps_location"]["lat"],
            "gps_lon": rich_data["gps_location"]["lon"],
            "active_dtc_codes": real_codes,
            "raw_payload": {**payload, **rich_data} 
        }

        # ✅ STEP 3: PUSH TO SUPABASE
        supabase.table("telematics_logs").insert(db_payload).execute()
        
        # ✅ STEP 4: UPDATED PRINT (Now showing Oil Pressure)
        print(f"📥 CLOUD SYNC [{v_id}]: Temp={real_temp}°C | Oil={real_oil} PSI | RPM={rich_data['rpm']} | Status=OK")

    except Exception as e:
        print(f"❌ Bridge Error: {e}")

# --- START LISTENER ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("🔌 Smart Cloud Bridge Starting...")
try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge stopped.")