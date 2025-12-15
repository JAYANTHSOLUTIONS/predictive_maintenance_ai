from typing import TypedDict, List, Optional, Dict, Any

class AgentState(TypedDict):
    # --- 1. Inputs ---
    vehicle_id: str
    
    # --- 2. Data Layer (Populated by DataAnalysisAgent) ---
    vehicle_metadata: Optional[Dict[str, Any]]
    telematics_data: Optional[Dict[str, Any]]
    
    # --- 3. Analysis Layer (Populated by DataAnalysisAgent) ---
    risk_score: int
    risk_level: str          # LOW, MEDIUM, HIGH, CRITICAL
    detected_issues: List[str]
    
    # --- 4. Diagnosis Layer (Populated by DiagnosisAgent) ---
    diagnosis_report: str
    recommended_action: str
    priority_level: str
    
    # --- 5. Customer Layer (Populated by CustomerAgent) ---
    customer_script: str
    customer_decision: str   # "BOOKED", "DEFERRED", "REJECTED"
    
    # --- 6. Scheduling Layer (Populated by SchedulingAgent) ---
    booking_id: Optional[str]
    selected_slot: Optional[str]
    
    # --- 7. Manufacturing & Feedback Layer (Populated by New Nodes) ---
    feedback_request: Optional[str]
    manufacturing_recommendations: Optional[str]

    # --- 8. System Flags ---
    error_message: Optional[str]
    ueba_alert_triggered: bool