from langgraph.graph import StateGraph, END, START
from app.agents.state import AgentState

# --- IMPORT WORKER NODES (With Safety Checks) ---
# We wrap these in try/except so the app doesn't crash if a file is missing
try:
    from app.agents.nodes.data_analysis import data_analysis_node
except ImportError:
    def data_analysis_node(state): return state

from app.agents.nodes.diagnosis import diagnosis_node
from app.agents.nodes.customer_engagement import customer_node

try:
    from app.agents.nodes.scheduling import scheduling_node
except ImportError:
    # Fallback if function is named 'scheduler_node' instead
    try:
        from app.agents.nodes.scheduling import scheduler_node as scheduling_node
    except ImportError:
        def scheduling_node(state): return state

try:
    from app.agents.nodes.feedback import feedback_node
except ImportError:
    # If feedback.py doesn't exist yet, just pass through
    def feedback_node(state): 
        print("⚠️ Feedback Node Skipped (File missing)")
        return state

try:
    from app.agents.nodes.manufacturing_insights import manufacturing_node
except ImportError:
    try:
        from app.agents.nodes.manufacturing import manufacturing_node
    except ImportError:
        def manufacturing_node(state): return state

def build_graph():
    """
    Constructs the Agent Workflow Graph.
    """
    # 1. Initialize the Graph
    workflow = StateGraph(AgentState)

    # 2. Add Nodes (The Workers)
    workflow.add_node("data_analysis", data_analysis_node)
    workflow.add_node("diagnosis", diagnosis_node)
    workflow.add_node("customer_engagement", customer_node)
    workflow.add_node("scheduling", scheduling_node)
    workflow.add_node("feedback", feedback_node)            # <--- YOUR NEW NODE
    workflow.add_node("manufacturing", manufacturing_node)

    # 3. Define Edges (The Logic Flow)
    # Start -> Analysis
    workflow.add_edge(START, "data_analysis")

    # Analysis -> Diagnosis
    workflow.add_edge("data_analysis", "diagnosis")

    # Diagnosis -> Customer
    workflow.add_edge("diagnosis", "customer_engagement")

    # Customer -> Scheduler
    workflow.add_edge("customer_engagement", "scheduling")

    # Scheduler -> Feedback
    workflow.add_edge("scheduling", "feedback")             # <--- YOUR NEW FLOW

    # Feedback -> Manufacturing (CAPA)
    workflow.add_edge("feedback", "manufacturing")          # <--- YOUR NEW FLOW

    # Manufacturing -> END
    workflow.add_edge("manufacturing", END)

    # 4. Compile the brain
    return workflow.compile()

# ✅ THIS IS THE FIX:
# We renamed 'agent_app' to 'master_agent' so routes_predictive.py can find it!
master_agent = build_graph()

def run_predictive_flow(vehicle_id: str):
    """
    The main entry point for the API/UI to call.
    """
    print(f"\n🚀 STARTING FULL AGENT FLOW FOR: {vehicle_id}")
    
    # Initialize State
    initial_state = {
        "vehicle_id": vehicle_id,
        "risk_score": 0,
        "detected_issues": [],
        "ueba_alert_triggered": False,
        "telematics_data": {} # Ensure this is initialized
    }

    # Run the Graph
    final_state = master_agent.invoke(initial_state)
    
    return final_state