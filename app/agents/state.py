from typing import TypedDict, List, Optional, Dict, Any

class AgentState(TypedDict):
    # Inputs
    vehicle_id: str
    vehicle_id: str
    vehicle_metadata: Optional[Dict[str, Any]]
    telematics_data: Optional[Dict[str, Any]]
    risk_score: int
    risk_level: str
    detected_issues: List[str]
    diagnosis_report: str
    recommended_action: str
    priority_level: str
    customer_script: str
    customer_decision: str
    booking_id: Optional[str]
    error_message: Optional[str]
    ueba_alert_triggered: bool
    
    # Data Layer (Populated by DataAnalysisAgent)
    vehicle_metadata: Optional[Dict[str, Any]]
    telematics_data: Optional[Dict[str, Any]]
    
    # Analysis Layer (Populated by DataAnalysisAgent)
    risk_score: int
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    detected_issues: List[str]
    
    # Diagnosis Layer (Populated by DiagnosisAgent)
    diagnosis_report: str
    recommended_action: str
    priority_level: str
    
    # Customer Layer (Populated by CustomerAgent)
    customer_script: str
    customer_decision: str # "BOOKED", "DEFERRED", "REJECTED"
    
    # Scheduling Layer (Populated by SchedulingAgent)
    selected_slot: str
    booking_id: Optional[str]
    
    # System Flags
    error_message: Optional[str]
    ueba_alert_triggered: bool

    manufacturing_recommendations: str
    feedback_request: str