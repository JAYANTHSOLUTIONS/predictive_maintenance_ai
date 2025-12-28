from langgraph.graph import StateGraph, END, START
from app.agents.state import AgentState

# ==========================================
# 1. IMPORT AGENT NODES (Corrected Paths: .nodes)
# ==========================================

# 1. Data Analysis Node
try:
    from app.agents.nodes.data_analysis import data_analysis_node
except ImportError:
    print("⚠️ [Master] 'nodes/data_analysis.py' not found. Using dummy.")
    def data_analysis_node(state): 
        state["risk_score"] = 85
        state["risk_level"] = "HIGH"
        state["detected_issues"] = ["Oil Pressure Low"]
        return state

# 2. Diagnosis Node (CRITICAL)
try:
    # ✅ FIX: Added .nodes in the path
    from app.agents.nodes.diagnosis import diagnosis_node
except ImportError:
    # Print exact error to help debugging
    import traceback
    traceback.print_exc()
    raise ImportError("❌ CRITICAL ERROR: 'app/agents/nodes/diagnosis.py' is missing!")

# 3. Customer Engagement Node
try:
    from app.agents.nodes.customer_engagement import customer_node
except ImportError:
    print("⚠️ [Master] 'nodes/customer_engagement.py' not found. Using dummy.")
    def customer_node(state): return state

# 4. Scheduling Node
try:
    from app.agents.nodes.scheduling import scheduling_node
except ImportError:
    # Try alternate name if first fails
    try:
        from app.agents.nodes.scheduling import scheduler_node as scheduling_node
    except ImportError:
        print("⚠️ [Master] 'nodes/scheduling.py' not found. Using dummy.")
        def scheduling_node(state): return state

# 5. Feedback & Manufacturing (Optional)
try:
    from app.agents.nodes.feedback import feedback_node
except ImportError:
    def feedback_node(state): return state

try:
    from app.agents.nodes.manufacturing import manufacturing_node
except ImportError:
    def manufacturing_node(state): return state


# ==========================================
# 2. BUILD THE GRAPH
# ==========================================
def build_graph():
    """
    Constructs the Agent Workflow Graph.
    """
    workflow = StateGraph(AgentState)

    # --- ADD NODES ---
    workflow.add_node("data_analysis", data_analysis_node)
    workflow.add_node("diagnosis", diagnosis_node)
    workflow.add_node("customer_engagement", customer_node)
    workflow.add_node("scheduling", scheduling_node)
    workflow.add_node("feedback", feedback_node)
    workflow.add_node("manufacturing", manufacturing_node)

    # --- DEFINE EDGES ---
    
    # Start -> Analysis
    workflow.add_edge(START, "data_analysis")

    # Analysis -> Diagnosis
    workflow.add_edge("data_analysis", "diagnosis")

    # Diagnosis -> Customer
    workflow.add_edge("diagnosis", "customer_engagement")

    # Customer -> Scheduler
    workflow.add_edge("customer_engagement", "scheduling")

    # Scheduler -> Feedback
    workflow.add_edge("scheduling", "feedback")

    # Feedback -> Manufacturing
    workflow.add_edge("feedback", "manufacturing")

    # Manufacturing -> End
    workflow.add_edge("manufacturing", END)

    return workflow.compile()

# ==========================================
# 3. EXPORT
# ==========================================
master_agent = build_graph()