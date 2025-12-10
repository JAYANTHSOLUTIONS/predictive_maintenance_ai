import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

def customer_node(state: AgentState) -> AgentState:
    print("🗣️ [Customer] Drafting notification...")
    
    # Get details
    owner = state["vehicle_metadata"].get("owner", "Customer")
    model = state["vehicle_metadata"].get("model", "Vehicle")
    diagnosis = state["diagnosis_report"]
    priority = state["priority_level"]

    # Prompt the AI to write a message
    prompt = f"""
    You are a Service Advisor at a Truck Dealership.
    Write a short, professional text message to {owner}.
    
    Topic: Their {model} needs urgent repair.
    Diagnosis Summary: {diagnosis}
    Priority: {priority}
    
    Ask them to confirm a booking for tomorrow.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    state["customer_script"] = response.content
    
    # Simulating the customer saying "YES" because it's Critical
    print(f"📞 [Customer] Message sent to {owner}. Waiting for reply...")
    state["customer_decision"] = "BOOKED" 
    
    return state