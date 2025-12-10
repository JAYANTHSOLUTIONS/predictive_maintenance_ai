import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

load_dotenv()

llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

def manufacturing_node(state: AgentState) -> AgentState:
    print("🏭 [Manufacturing] Analyzing failure for fleet-wide patterns...")
    
    # Only run if there is a real issue
    if state["risk_score"] < 40:
        state["manufacturing_recommendations"] = "No design changes needed."
        return state

    diagnosis = state["diagnosis_report"]
    model = state["vehicle_metadata"].get("model")

    prompt = f"""
    You are a Quality Engineering AI at the {model} factory.
    A vehicle has failed in the field.
    
    Diagnosis: {diagnosis}
    
    TASK:
    Suggest a 'Root Cause Design Improvement' to prevent this in future models.
    Focus on material changes, sensor placement, or software logic.
    
    Output format:
    Design Flaw: [What failed]
    Engineering Fix: [Technical solution]
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    state["manufacturing_recommendations"] = response.content
    
    print("✅ [Manufacturing] CAPA Report Generated.")
    return state