import paho.mqtt.client as mqtt
import json
import os
import random
import time

# --- CONFIGURATION ---
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "hackathon/truck/v101/telematics"

# FILE PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data_samples", "collected_data.json")

# --- DATA SIMULATION ENGINE ---
def enrich_telematics(real_temp, real_oil):
    # 1. RPM Logic
    if real_temp > 105:
        sim_rpm = random.randint(3500, 4500)
    elif real_oil < 20:
        sim_rpm = random.randint(400, 900)
    else:
        sim_rpm = random.randint(1200, 2200)

    # 2. Vibration Sensor
    if sim_rpm > 4000 or real_oil < 15:
        sim_vibration = "HIGH"
        vib_hz = random.uniform(50.5, 80.0)
    else:
        sim_vibration = "NORMAL"
        vib_hz = random.uniform(10.0, 25.0)

    # 3. Battery Voltage
    if sim_rpm < 600:
        sim_voltage = round(random.uniform(21.5, 23.0), 1)
    else:
        sim_voltage = round(random.uniform(24.1, 25.5), 1)

    return {
        "rpm": sim_rpm,
        "vibration_level": sim_vibration,
        "vibration_hz": round(vib_hz, 2),
        "battery_voltage": sim_voltage,
        "fuel_level_percent": random.randint(40, 65),
        "gps_location": {"lat": 28.7041, "lon": 77.1025},
        "tire_pressure_bar": [7.1, 7.0, 6.9, 7.1]
    }

# --- MQTT HANDLERS ---
def on_connect(client, userdata, flags, rc):
    print(f"📡 Connected to MQTT! Listening for Wokwi Data...")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        real_temp = payload.get("engine_temp_c", 0)
        real_oil = payload.get("oil_pressure_psi", 0)
        real_codes = payload.get("active_dtc_codes", [])

        rich_data = enrich_telematics(real_temp, real_oil)

        final_telematics = {
            "engine_temp_c": real_temp,
            "oil_pressure_psi": real_oil,
            "active_dtc_codes": real_codes,
            **rich_data
        }

        # --- UPDATED PRINT STATEMENT ---
        print(f"📥 LIVE: Temp={real_temp}°C | Oil={real_oil} PSI | RPM={rich_data['rpm']} | Batt={rich_data['battery_voltage']}V")

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                db = json.load(f)
        else:
            db = {"vehicles": {}}

        if "vehicles" not in db: db["vehicles"] = {}
        if "V-101" not in db["vehicles"]: 
            db["vehicles"]["V-101"] = {
                "metadata": {"model": "HeavyHaul X5", "owner": "Logistics Corp"},
                "telematics": {}
            }
            
        db["vehicles"]["V-101"]["telematics"] = final_telematics
        
        with open(DATA_FILE, "w") as f:
            json.dump(db, f, indent=2)
            
    except Exception as e:
        print(f"❌ Error: {e}")

# --- START LISTENER ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("🔌 Smart Bridge Starting...")
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()