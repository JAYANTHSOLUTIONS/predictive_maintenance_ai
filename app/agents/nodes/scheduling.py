from app.agents.state import AgentState
from app.ueba.middleware import secure_call
from datetime import datetime, timedelta

# ==========================================
# 💾 MOCK DATABASE (Global Memory)
# ==========================================
# Stores all confirmed bookings to prevent double-booking.
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
    def find_next_available_slot(target_date_str):
        """
        Loops through standard work hours (09:00 - 17:00) 
        to find a slot that isn't already in BOOKINGS_DB.
        """
        # Define working hours (09:00 to 17:00)
        possible_slots = [f"{h:02d}:00" for h in range(9, 18)]
        
        # Filter DB for bookings strictly on this specific date
        taken_times = {b['slot_time'] for b in BOOKINGS_DB if b['slot_date'] == target_date_str}
        
        # Find first slot NOT in taken_times
        for slot in possible_slots:
            if slot not in taken_times:
                return slot
        
        return None # No slots available today

    @staticmethod
    def book_slot(vehicle_id: str, priority: str):
        """
        Determines slot based on priority, CHECKS AVAILABILITY, and saves to Mock DB.
        """
        print(f"📅 [System] Calculating slot for {vehicle_id} (Priority: {priority})...")
        
        # 1. Determine Initial Target Date based on Priority
        now = datetime.now()
        
        # For DEMO purposes, let's try to book everything for TOMORROW
        # This makes it easier to see the conflict logic working on the calendar
        target_date = now + timedelta(days=1)
        
        # (Optional: Use real logic if you prefer)
        # if priority == "Critical":
        #     target_date = now + timedelta(days=1)
        # elif priority == "High":
        #     target_date = now + timedelta(days=3)
        # else:
        #     target_date = now + timedelta(days=7)

        service_note = f"Repair ({priority})"
        formatted_date = target_date.strftime("%Y-%m-%d")

        # 2. SMART LOGIC: Find a Real Available Time (Collision Detection)
        available_time = SchedulerService.find_next_available_slot(formatted_date)
        
        # Fallback if fully booked: Push to next day and reset to 09:00
        if not available_time:
            print(f"⚠️ [System] Date {formatted_date} is full! Checking next day...")
            target_date = target_date + timedelta(days=1)
            formatted_date = target_date.strftime("%Y-%m-%d")
            available_time = "09:00" # Reset to morning for the new day

        full_slot_str = f"{formatted_date} {available_time}"

        # 3. Create Booking Record
        # We use a timestamp-based ID to ensure uniqueness
        new_booking = {
            "booking_id": f"BK-{int(now.timestamp())}", 
            "vin": vehicle_id,
            "slot_date": formatted_date,
            "slot_time": available_time,
            "service_type": service_note,
            "priority": priority,
            "status": "CONFIRMED",
            "timestamp": now.isoformat()
        }
        
        # 4. Save to Mock DB
        BOOKINGS_DB.append(new_booking)
        print(f"💾 [DB] Booking saved: {new_booking['booking_id']} | {full_slot_str}")
        
        # 5. Return result
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
    
    # --- 🚨 BYPASS LOGIC ENABLED 🚨 ---
    # We allow auto-booking for ALL priorities for the demo.
    # To restore strict logic, uncomment the block below:
    
    # if priority == "Critical":
    #    print("🚨 [Scheduler] Critical issue detected. Auto-authorizing booking.")
    # elif state.get("customer_decision") != "BOOKED":
    #    print("⏸️ Booking skipped by customer.")
    #    return state

    print(f"⚡ [Demo Mode] Auto-booking enabled for {priority} priority.")

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