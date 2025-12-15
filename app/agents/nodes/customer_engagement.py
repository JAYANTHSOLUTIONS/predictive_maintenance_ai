import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

load_dotenv()

# Initialize LLM
# ✅ UPDATED: Switched to Gemini 2.0 Flash (Free & Reliable)
# DeepSeek V3.2 is paid, so we use Gemini Free to ensure your demo works.
llm = ChatOpenAI(
    model="google/gemini-2.0-flash-exp:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

def customer_node(state: AgentState) -> AgentState:
    print("🗣️ [Customer] Drafting notification...")
    
    # Get details
    owner = state["vehicle_metadata"].get("owner", "Customer")
    model = state["vehicle_metadata"].get("model", "Vehicle")
    diagnosis = state.get("diagnosis_report", "Maintenance Required")
    priority = state.get("priority_level", "Medium")

    # Prompt the AI to write a message
    prompt = f"""
    You are a Service Advisor at a Truck Dealership.
    Write a short, professional text message to {owner}.
    
    Topic: Their {model} needs urgent repair.
    Diagnosis Summary: {diagnosis}
    Priority: {priority}
    
    Constraint: Keep it under 50 words. Ask them to confirm a booking for tomorrow.
    """

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        state["customer_script"] = response.content
    except Exception as e:
        print(f"❌ Customer Agent LLM Error: {e}")
        # Fallback to prevent crash
        state["customer_script"] = f"Urgent: Your {model} requires service. Please contact us to book an appointment."

    # Simulating the customer saying "YES" because it's Critical
    print(f"📞 [Customer] Message sent to {owner}. Waiting for reply...")
    state["customer_decision"] = "BOOKED" 
    
    return state