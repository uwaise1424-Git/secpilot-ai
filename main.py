from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import logs

app = FastAPI(title="AI SOC Analyst", version="1.0")

# Security Rule: Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Your Vite frontend URL
    allow_credentials=True,
    allow_methods=["*"], # Allow all types of requests (GET, POST, etc.)
    allow_headers=["*"],
)

# Connect our router
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])

@app.get("/")
def read_root():
    return {"message": "SecPilot AI SOC Backend is running safely!"}