import os
import json
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# 1. Request Model
class BookingRequest(BaseModel):
    vehicle_id: str
    service_date: str  # YYYY-MM-DD
    notes: str

# 2. File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "data_samples")

@router.post("/create")
async def create_booking(request: BookingRequest):
    """
    1. Generates a Booking ID.
    2. Updates the vehicle's AI Log to say 'Service Booked'.
    """
    log_path = os.path.join(LOG_DIR, f"run_log_{request.vehicle_id}.json")
    
    # Check if AI has run for this vehicle
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="No AI diagnosis found. Run diagnostics first.")

    try:
        # Load existing log
        with open(log_path, "r") as f:
            log_data = json.load(f)

        # Generate Booking Details
        booking_id = f"BK-{uuid.uuid4().hex[:6].upper()}"
        
        # Update the Log (This changes the status in your Fleet Table!)
        log_data["customer_decision"] = "accept"
        log_data["booking_id"] = booking_id
        log_data["scheduled_date"] = request.service_date
        log_data["service_notes"] = request.notes
        
        # Save back to file
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=4)

        return {
            "status": "success",
            "booking_id": booking_id,
            "message": f"Service confirmed for {request.service_date}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))