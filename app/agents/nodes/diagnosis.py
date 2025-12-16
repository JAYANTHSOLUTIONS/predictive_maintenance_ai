from langchain_core.messages import HumanMessage
from app.agents.state import AgentState
import os
from dotenv import load_dotenv

# --- LLM SETUP ---
from langchain_openai import ChatOpenAI
load_dotenv()

# ✅ UPDATED: Fetch Key from Environment & Use Groq
# This reads 'GROQ_API_KEY' from your .env file
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
    print("🧠 [Diagnosis] LLM analyzing failure patterns...")
    
    # 1. Check if there is anything to diagnose
    if state.get("risk_score", 0) < 20:
        state["diagnosis_report"] = "Vehicle is healthy. No issues detected."
        state["recommended_action"] = "Monitor"
        state["priority_level"] = "Low"
        return state

    # 2. Prepare prompt for the AI
    # Handle list or string for detected_issues
    detected = state.get("detected_issues", [])
    if isinstance(detected, list):
        issues = "\n".join(detected)
    else:
        issues = str(detected)

    telematics = state.get("telematics_data", {})
    
    # ✅ PROMPT: Forces structured Markdown output
    prompt = f"""
    You are a Senior Fleet Mechanic AI. 
    Analyze this truck's status:
    
    Vehicle: {state['vehicle_metadata'].get('model', 'Unknown Model')}
    Issues Detected:
    {issues}
    
    Telematics:
    - Oil Pressure: {telematics.get('oil_pressure_psi', 'N/A')} psi
    - Engine Temp: {telematics.get('engine_temp_c', 'N/A')} C
    - Active Codes: {telematics.get('dtc_readable', 'None')}
    
    IMPORTANT: Format your response EXACTLY like this template. Use Markdown headers and bullets.
    
    ### 🚨 Critical Faults
    * **[Code/Issue]**: [Short description]
    
    ### 📉 Root Cause Analysis
    * **Primary Cause:** [One sentence explanation]
    * **Secondary Factors:** [One sentence explanation]
    
    ### 🛠️ Immediate Action Plan
    1. [First Step]
    2. [Second Step]
    3. [Third Step]
    
    ### ⚠️ Risk Assessment
    * **Severity:** [Critical/High/Medium]
    * **Consequence:** [What happens if ignored?]
    """

    # 3. Call the LLM
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
    except Exception as e:
        print(f"❌ Diagnosis Agent LLM Error: {e}")
        # Fallback to prevent crash
        content = "Error generating diagnosis. Please check system logs."
        state["priority_level"] = "Medium"

    # 4. Save to State
    state["diagnosis_report"] = content
    
    # Simple keyword extraction for priority setting
    if "Critical" in content:
        state["priority_level"] = "Critical"
    elif "High" in content:
        state["priority_level"] = "High"
    else:
        state["priority_level"] = "Medium"

    return state