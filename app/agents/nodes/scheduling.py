from app.agents.state import AgentState
from app.ueba.middleware import secure_call
from datetime import datetime, timedelta

# ==========================================
# 💾 MOCK DATABASE (Global Memory)
# ==========================================
# This list acts as your database for the Hackathon.
# It persists as long as the python server is running.
BOOKINGS_DB = []

# ==========================================
# 🛠️ SERVICE LOGIC
# ==========================================
class SchedulerService:
    @staticmethod
    def get_all_bookings():
        """
        Helper method for the API to fetch data for the Frontend.
        """
        return BOOKINGS_DB

    @staticmethod
    def book_slot(vehicle_id: str, priority: str):
        """
        Determines slot based on priority AND saves to Mock DB.
        """
        print(f"📅 [System] Calculating slot for {vehicle_id} (Priority: {priority})...")
        
        # 1. LOGIC: Calculate the Date
        now = datetime.now()
        
        if priority == "Critical":
            slot_time = now + timedelta(days=1)
            service_note = "URGENT BAY ACCESS"
        elif priority == "High":
            slot_time = now + timedelta(days=3)
            service_note = "Standard Priority Repair"
        else:
            slot_time = now + timedelta(days=7)
            service_note = "Routine Maintenance"

        # Format time for the Calendar UI (e.g., "09:00")
        # In a real app, you'd check available slots here.
        formatted_time = "09:00" 
        formatted_date = slot_time.strftime("%Y-%m-%d")
        full_slot_str = f"{formatted_date} {formatted_time}"

        # 2. CREATE BOOKING RECORD (The Data Object)
        new_booking = {
            "booking_id": f"BK-{now.strftime('%M%S')}",
            "vin": vehicle_id,
            "slot_date": formatted_date,
            "slot_time": formatted_time,
            "service_type": service_note,
            "priority": priority,
            "status": "CONFIRMED",
            "timestamp": now.isoformat()
        }
        
        # 3. SAVE TO MOCK DB (This makes it show up on Frontend!)
        BOOKINGS_DB.append(new_booking)
        print(f"💾 [DB] Booking saved: {new_booking['booking_id']} for {vehicle_id}")
        
        # 4. Return result to the Agent Node
        return {
            "booking_id": new_booking["booking_id"],
            "slot": full_slot_str,
            "type": service_note
        }

# ==========================================
# 🤖 AGENT NODE
# ==========================================
def scheduling_node(state: AgentState) -> AgentState:
    print("🗓️ [Scheduler] Finding repair slot...")
    
    # Get Priority safely
    priority = state.get("priority_level", "Medium")
    
    # LOGIC CHECK: Auto-book if Critical, otherwise wait for customer
    if priority == "Critical":
        print("🚨 [Scheduler] Critical issue detected. Auto-authorizing booking.")
    elif state.get("customer_decision") != "BOOKED":
        print("⏸️ Booking skipped by customer.")
        return state

    agent_name = "SchedulingAgent"
    v_id = state.get("vehicle_id", "Unknown-ID")

    try:
        # Securely call the booking service
        booking_result = secure_call(
            agent_name,
            "SchedulerService",
            SchedulerService.book_slot,
            v_id,
            priority
        )
        
        # EXTRACT DATA
        state["booking_id"] = booking_result["booking_id"]
        state["selected_slot"] = booking_result["slot"]
        
        print(f"✅ [Scheduler] CONFIRMED! Date: {booking_result['slot']} (ID: {booking_result['booking_id']})")
        
    except PermissionError as e:
        state["error_message"] = str(e)
        print(f"⛔ [UEBA] BLOCKED: {e}")

    return state