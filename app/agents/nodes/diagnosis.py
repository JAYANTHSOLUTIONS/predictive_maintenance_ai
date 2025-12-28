from langchain_core.messages import HumanMessage
from app.agents.state import AgentState
import os
from dotenv import load_dotenv

# --- LLM SETUP ---
from langchain_openai import ChatOpenAI
load_dotenv()

# ✅ IMPORT KNOWLEDGE BASE UTILITY
try:
    from app.utils.knowledge import find_diagnosis_steps
except ImportError:
    print("⚠️ Warning: app.utils.knowledge not found. RAG disabled.")
    def find_diagnosis_steps(x): return []

# ✅ SETUP: Fetch Key from Environment & Use Groq
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file")

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key
)

def diagnosis_node(state: AgentState) -> AgentState:
    """
    Worker 2: Uses LLM to explain the issue and recommend action.
    """
    v_id = state.get("vehicle_id", "Unknown")
    print(f"🧠 [Diagnosis] LLM analyzing failure patterns for {v_id}...")
    
    # ---------------------------------------------------------
    # 🚨 DEMO MODE CHANGE: DISABLED HEALTH CHECK
    # ---------------------------------------------------------
    # if state.get("risk_score", 0) < 20:
    #     state["diagnosis_report"] = "Vehicle is healthy. No issues detected."
    #     state["recommended_action"] = "Monitor"
    #     state["priority_level"] = "Low"
    #     return state
    # ---------------------------------------------------------

    # 2. Prepare prompt for the AI
    detected = state.get("detected_issues", [])
    if isinstance(detected, list):
        issues = "\n".join(detected)
    else:
        issues = str(detected)
    
    # If simulated data is clean, force a dummy issue for the report to look interesting
    if not issues or issues == "None":
        issues = "Minor sensor drift detected (Simulated)"

    telematics = state.get("telematics_data", {})
    
    # --- 🔍 RAG LOGIC: RETRIEVE KNOWLEDGE FROM JSON ---
    expert_advice = ""
    search_terms = []
    
    if "Temp" in issues or telematics.get('engine_temp_c', 0) > 100:
        search_terms.append("overheating")
    if "Oil" in issues or telematics.get('oil_pressure_psi', 50) < 20:
        search_terms.append("oil")
    
    for term in search_terms:
        steps = find_diagnosis_steps(term)
        if steps:
            expert_advice += f"\n--- MANUAL ENTRY FOR '{term.upper()}' ---\n"
            for s in steps[:3]: 
                expert_advice += f"Part: {s['part']}\nSteps: {s['steps']}\n"

    if not expert_advice:
        expert_advice = "General maintenance check recommended."

    # ✅ PROMPT
    prompt = f"""
    You are a Senior Fleet Mechanic AI. 
    Analyze this truck's status based on the Telematics and the Service Manual provided.
    
    Vehicle: {state['vehicle_metadata'].get('model', 'Unknown Model')}
    Issues Detected: {issues}
    
    Telematics:
    - Oil Pressure: {telematics.get('oil_pressure_psi', 'N/A')} psi
    - Engine Temp: {telematics.get('engine_temp_c', 'N/A')} C
    
    📘 OFFICIAL SERVICE MANUAL GUIDELINES:
    {expert_advice}
    
    IMPORTANT: Format your response EXACTLY like this template. Use Markdown headers.
    
    ### 🚨 Issue Summary
    * **[Code/Issue]**: {issues}
    
    ### 📉 Root Cause Analysis
    * **Primary Cause:** [One sentence explanation]
    
    ### 🛠️ Immediate Action Plan
    1. [Step 1]
    2. [Step 2]
    
    ### ⚠️ Risk Assessment
    * **Severity:** [Critical/High/Medium]
    """

    # 3. Call the LLM
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
    except Exception as e:
        print(f"❌ Diagnosis Agent LLM Error: {e}")
        content = "Error generating diagnosis."
        state["priority_level"] = "Medium"

    # 4. Save to State
    state["diagnosis_report"] = content
    
    # ---------------------------------------------------------
    # 🔍 UPDATED PRIORITY CHECK LOGIC
    # We check for "Severity: Critical" specifically to avoid matching the header.
    # ---------------------------------------------------------
    if "Severity: Critical" in content or "Severity:** Critical" in content:
        state["priority_level"] = "Critical"
    elif "Severity: High" in content or "Severity:** High" in content:
        state["priority_level"] = "High"
    else:
        state["priority_level"] = "Medium"

    print(f"📊 [Diagnosis] Priority set to: {state['priority_level']}")

    return state