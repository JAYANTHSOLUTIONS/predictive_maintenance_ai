import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

# --- 1. LOAD ENVIRONMENT VARIABLES ---
load_dotenv() # This reads the .env file

# --- 2. FETCH KEY FROM ENV ---
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    # Stop the server or warn if the key is missing
    raise ValueError("❌ ERROR: GROQ_API_KEY is missing from .env file!")

# --- 3. SETUP GROQ LLM ---
llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key
)

def customer_node(state: AgentState) -> AgentState:
    print("🗣️ [Customer] Drafting notification...")
    
    # Get details from the graph state
    # Use .get() with defaults to avoid crashes if metadata is missing
    owner = state.get("vehicle_metadata", {}).get("owner", "Customer")
    model = state.get("vehicle_metadata", {}).get("model", "Vehicle")
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
        # Call Groq
        response = llm.invoke([HumanMessage(content=prompt)])
        state["customer_script"] = response.content
    except Exception as e:
        print(f"❌ Customer Agent LLM Error: {e}")
        # Fallback to prevent crash
        state["customer_script"] = f"Urgent: Your {model} requires service. Please contact us to book an appointment."

    # Simulating the customer saying "YES" because it's Critical
    # In a real app, this would be a separate input node/wait state.
    print(f"📞 [Customer] Message sent to {owner}. Waiting for reply...")
    state["customer_decision"] = "BOOKED" 
    
    return state