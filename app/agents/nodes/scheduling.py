from app.agents.state import AgentState
from app.ueba.middleware import secure_call

# Mock Service
class SchedulerService:
    @staticmethod
    def book_slot(vehicle_id: str, priority: str):
        # In a real app, this would SQL INSERT into a Booking Table
        print(f"📅 [System] Allocating emergency bay for {vehicle_id}...")
        return "SLOT-9988-URGENT"

def scheduling_node(state: AgentState) -> AgentState:
    print("🗓️ [Scheduler] Finding repair slot...")
    
    # Only book if customer agreed
    if state.get("customer_decision") != "BOOKED":
        print("⏸️ Booking skipped by customer.")
        return state

    agent_name = "SchedulingAgent"
    v_id = state["vehicle_id"]
    priority = state["priority_level"]

    try:
        # Securely call the booking service
        booking_id = secure_call(
            agent_name,
            "SchedulerService",
            SchedulerService.book_slot,
            v_id,
            priority
        )
        
        state["booking_id"] = booking_id
        state["selected_slot"] = "Tomorrow 08:00 AM"
        print(f"✅ [Scheduler] CONFIRMED! ID: {booking_id}")
        
    except PermissionError as e:
        state["error_message"] = str(e)
        print(f"⛔ [UEBA] BLOCKED: {e}")

    return state