from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
import os
from dotenv import load_dotenv

# --- LLM SETUP ---
from langchain_openai import ChatOpenAI
load_dotenv()

# ✅ UPDATED: Switched to Gemini 2.0 Flash (Free & Reliable)
# This fixes the 404 "No endpoints found" error from DeepSeek
llm = ChatOpenAI(
    model="google/gemini-2.0-flash-exp:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
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
    issues = "\n".join(state["detected_issues"])
    telematics = state["telematics_data"]
    
    # ✅ PROMPT: Forces structured Markdown output
    prompt = f"""
    You are a Senior Fleet Mechanic AI. 
    Analyze this truck's status:
    
    Vehicle: {state['vehicle_metadata'].get('model')}
    Issues Detected:
    {issues}
    
    Telematics:
    - Oil Pressure: {telematics.get('oil_pressure_psi')} psi
    - Engine Temp: {telematics.get('engine_temp_c')} C
    - Active Codes: {telematics.get('dtc_readable')}
    
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
        print(f"❌ LLM Error: {e}")
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