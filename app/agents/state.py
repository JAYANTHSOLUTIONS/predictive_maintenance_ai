from typing import TypedDict, List, Optional, Dict, Any

class AgentState(TypedDict):
    # --- 1. CORE INPUTS ---
    vehicle_id: str
    vehicle_metadata: Optional[Dict[str, Any]]
    telematics_data: Optional[Dict[str, Any]]
    
    # --- 2. ANALYSIS LAYER (Data Analysis) ---
    risk_score: int
    risk_level: str             # LOW, MEDIUM, HIGH, CRITICAL
    detected_issues: List[str]
    
    # --- 3. DIAGNOSIS LAYER (Diagnosis Agent) ---
    diagnosis_report: str
    recommended_action: str
    priority_level: str
    
    # --- 4. CUSTOMER LAYER (Customer Engagement) ---
    customer_script: str
    customer_decision: str      # "BOOKED", "DEFERRED", "REJECTED"
    # ✅ IMPORTANT: Added this because API needs it for the voice logs
    voice_transcript: Optional[List[Dict[str, str]]] 
    
    # --- 5. SCHEDULING LAYER (Scheduling Agent) ---
    selected_slot: Optional[str]
    booking_id: Optional[str]
    
    # --- 6. FEEDBACK & MANUFACTURING (New Features) ---
    manufacturing_recommendations: Optional[str]
    feedback_request: Optional[str]

    # --- 7. SYSTEM FLAGS ---
    error_message: Optional[str]
    ueba_alert_triggered: bool