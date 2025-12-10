from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
# Import the LLM we configured in tests/test_key.py
# (We assume you moved the LLM initialization to app/config/settings.py or similar, 
# but for now, we'll init it here for simplicity)
import os
from dotenv import load_dotenv

# CHECK: Are you using Mistral (OpenRouter) or Google?
# Uncomment the one you are using below.

# --- OPTION A: MISTRAL (OpenRouter) ---
from langchain_openai import ChatOpenAI
load_dotenv()
llm = ChatOpenAI(
    model="mistralai/devstral-2512:free", # Or your specific model
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

# --- OPTION B: GOOGLE (Gemini) ---
# from langchain_google_genai import ChatGoogleGenerativeAI
# load_dotenv()
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")


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
    
    TASK:
    1. Explain technically what is failing.
    2. Recommend the specific repair needed.
    3. Set priority (Low/Medium/High/Critical).
    
    Output format:
    Report: [Your explanation]
    Action: [Specific repair]
    Priority: [Level]
    """

    # 3. Call the LLM
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content

    # 4. Save to State
    # (In a real app, we'd use Structured Output/JSON mode to parse this reliably)
    state["diagnosis_report"] = content
    
    # Simple keyword extraction for the sake of the demo
    if "Critical" in content:
        state["priority_level"] = "Critical"
    elif "High" in content:
        state["priority_level"] = "High"
    else:
        state["priority_level"] = "Medium"

    return state