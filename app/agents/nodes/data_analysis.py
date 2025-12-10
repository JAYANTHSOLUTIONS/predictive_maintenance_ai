from app.agents.state import AgentState
from app.data.repositories import TelematicsRepo, VehicleRepo
from app.domain.risk_rules import calculate_risk_score

# IMPORT UEBA
from app.ueba.middleware import secure_call

def data_analysis_node(state: AgentState) -> AgentState:
    v_id = state["vehicle_id"]
    agent_name = "DataAnalysisAgent" # Identity
    
    print(f"🔍 [Analyzer] Requesting secure access for {v_id}...")

    try:
        # 1. Secure Fetch: Vehicle Data
        # We wrap the Repo call inside secure_call
        vehicle = secure_call(
            agent_name, 
            "VehicleRepo", 
            VehicleRepo.get_vehicle_details, 
            v_id
        )

        # 2. Secure Fetch: Telematics
        telematics = secure_call(
            agent_name, 
            "TelematicsRepo", 
            TelematicsRepo.get_latest_telematics, 
            v_id
        )

        if not vehicle or not telematics:
            state["error_message"] = f"Vehicle {v_id} not found."
            return state

        state["vehicle_metadata"] = vehicle
        state["telematics_data"] = telematics

        # 3. Calculate Risk (Internal logic doesn't need UEBA, only external data access)
        risk_assessment = calculate_risk_score(telematics)
        
        state["risk_score"] = risk_assessment["score"]
        state["risk_level"] = risk_assessment["level"]
        state["detected_issues"] = risk_assessment["reasons"]
        
        return state

    except PermissionError as e:
        state["error_message"] = str(e)
        state["ueba_alert_triggered"] = True
        return state