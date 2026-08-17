from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import logs
import db_models # <-- Updated name here
from database import engine

# This physically creates the secpilot.db file when the server boots
db_models.Base.metadata.create_all(bind=engine) # <-- Updated name here

app = FastAPI(title="AI SOC Analyst", version="1.0")

# Security Rule: Allow local React ONLY for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)
# Connect our router
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])

@app.get("/")
def read_root():
    return {"message": "SecPilot AI SOC Backend is running safely!"}