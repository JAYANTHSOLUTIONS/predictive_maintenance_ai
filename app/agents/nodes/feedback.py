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

def feedback_node(state: AgentState) -> AgentState:
    print("⭐ [Feedback] Service completed. Requesting customer review...")
    
    # Only run if a booking was actually made
    if state.get("customer_decision") != "BOOKED":
        return state

    owner = state["vehicle_metadata"].get("owner")
    
    prompt = f"""
    You are a Customer Experience AI.
    The customer {owner} just had their truck serviced after our urgent alert.
    
    Write a short, warm 'Post-Service Follow-up' script (Voice Style).
    Ask if the vehicle is running smoothly and request a satisfaction rating (1-5).
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Store this in state (we will display it in UI)
    state["feedback_request"] = response.content
    print("✅ [Feedback] Follow-up sent.")
    
    return state