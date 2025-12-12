from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your modular routes
from app.api import routes_predictive, routes_telematics, routes_fleet

app = FastAPI(title="Predictive Maintenance AI API")

# --- CORS SETUP ---
# We allow ["*"] (All origins) to prevent any connection issues during the demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routes ---
app.include_router(routes_predictive.router, prefix="/api/predictive", tags=["AI"])
app.include_router(routes_telematics.router, prefix="/api/telematics", tags=["Data"])
# ✅ ADDED THIS LINE:
app.include_router(routes_fleet.router, prefix="/api/fleet", tags=["Fleet"])

@app.get("/")
def health_check():
    return {"status": "AI System Online", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)