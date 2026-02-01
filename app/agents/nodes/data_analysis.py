from app.agents.state import AgentState
from app.domain.risk_rules import calculate_risk_score
from database import supabase # ✅ Direct DB Access

def data_analysis_node(state: AgentState) -> AgentState:
    v_id = state["vehicle_id"]
    print(f"🔍 [Analyzer] Querying Supabase for {v_id}...")

    try:
        # 1. FETCH METADATA (Owners & Vehicle Info)
        # We join with the 'owners' table to get contact info for the Customer Agent
        vehicle_response = supabase.table("vehicles") \
            .select("*, owners(full_name, phone_number)") \
            .eq("id", v_id) \
            .execute()

        if not vehicle_response.data:
            state["error_message"] = f"Vehicle {v_id} not found in DB."
            return state

        vehicle_data = vehicle_response.data[0]
        
        # Flatten Owner Data for easier access by Customer Agent
        owner_info = vehicle_data.get("owners", {})
        vehicle_data["owner"] = owner_info.get("full_name", "Valued Customer")
        vehicle_data["phone"] = owner_info.get("phone_number", "")

        state["vehicle_metadata"] = vehicle_data
        state["vin"] = vehicle_data.get("vin") # Critical for logs

        # 2. FETCH TELEMATICS (Latest Sensor Data)
        telematics_response = supabase.table("telematics_logs") \
            .select("*") \
            .eq("vehicle_id", v_id) \
            .order("timestamp_utc", desc=True) \
            .limit(1) \
            .execute()

        if telematics_response.data:
            t_data = telematics_response.data[0]
            state["telematics_data"] = t_data
            
            # 3. CALCULATE RISK (Using Live DB Data)
            # Pass the Dict directly to your logic rule engine
            risk_assessment = calculate_risk_score(t_data)
            
            state["risk_score"] = risk_assessment["score"]
            state["risk_level"] = risk_assessment["level"]
            state["detected_issues"] = risk_assessment["reasons"]
        else:
            # Fallback if vehicle exists but has no logs yet
            state["risk_score"] = 0
            state["risk_level"] = "LOW"
            state["detected_issues"] = ["No Data Available"]

        return state

    except Exception as e:
        print(f"❌ DB Connection Error: {e}")
        state["error_message"] = str(e)
        state["ueba_alert_triggered"] = True
        return state