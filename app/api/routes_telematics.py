from fastapi import APIRouter, HTTPException
from app.data.repositories import TelematicsRepo

router = APIRouter()

@router.get("/{vehicle_id}")
async def get_vehicle_stats(vehicle_id: str):
    """
    Fetches the latest live IoT data for the dashboard gauges.
    """
    data = TelematicsRepo.get_latest_telematics(vehicle_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    return data