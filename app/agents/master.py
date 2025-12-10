from langgraph.graph import StateGraph, END
from app.agents.state import AgentState

# Import ALL Worker Nodes
from app.agents.nodes.data_analysis import data_analysis_node
from app.agents.nodes.diagnosis import diagnosis_node
from app.agents.nodes.customer_engagement import customer_node
from app.agents.nodes.scheduling import scheduling_node
from app.agents.nodes.feedback import feedback_node          # <--- NEW IMPORT
from app.agents.nodes.manufacturing_insights import manufacturing_node

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
    workflow.add_node("feedback", feedback_node)             # <--- ADD NODE
    workflow.add_node("manufacturing", manufacturing_node)

    # 3. Define Edges (The Logic Flow)
    # Start -> Analysis
    workflow.set_entry_point("data_analysis")

    # Analysis -> Diagnosis
    workflow.add_edge("data_analysis", "diagnosis")

    # Diagnosis -> Customer
    workflow.add_edge("diagnosis", "customer_engagement")

    # Customer -> Scheduler
    workflow.add_edge("customer_engagement", "scheduling")

    # Scheduler -> Feedback
    workflow.add_edge("scheduling", "feedback")              # <--- CONNECT SCHEDULER TO FEEDBACK

    # Feedback -> Manufacturing (CAPA)
    workflow.add_edge("feedback", "manufacturing")           # <--- CONNECT FEEDBACK TO MANUFACTURING

    # Manufacturing -> END
    workflow.add_edge("manufacturing", END)

    # 4. Compile the brain
    return workflow.compile()

# Initialize the runnable application ONCE
agent_app = build_graph()

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
        "ueba_alert_triggered": False
    }

    # Run the Graph
    final_state = agent_app.invoke(initial_state)
    
    return final_state