from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import json

from services.parser import parse_auth_log
from services.ai_engine import analyze_threats_with_ai
from database import get_db
import db_models

router = APIRouter()

# Changed from 'async def' to 'def' so FastAPI safely threads the heavy workload
@router.post("/upload")
def upload_log(file: UploadFile = File(...), db: Session = Depends(get_db)):
    print("\n--- NEW UPLOAD STARTED ---")
    print("DEBUG 1: Endpoint triggered.")
    
    # 1. Read the uploaded log file synchronously
    content = file.file.read()
    log_data = content.decode("utf-8")
    print("DEBUG 2: File read successfully.")
    
    # 2. Send the RAW logs directly to Groq/Llama3 for universal analysis
    ai_response = analyze_threats_with_ai(log_data)
    print("DEBUG 3: AI response received.")
    
    # 3. Extract data from the AI's response safely
    try:
        # Check if the AI returned a completely blank string
        if not ai_response or str(ai_response).strip() == "":
            raise ValueError("The AI API returned an empty response.")
        
        # Safely parse the response based on its type
        if hasattr(ai_response, "model_dump"):
            ai_report = ai_response.model_dump()
        elif hasattr(ai_response, "dict"):
            ai_report = ai_response.dict()
        elif isinstance(ai_response, str):
            ai_report = json.loads(ai_response)
        else:
            ai_report = json.loads(str(ai_response))
            
    except Exception as e:
        print(f"Backend Parsing Error in logs.py: {e}")
        # Fallback data so the database save succeeds and the server never crashes
        ai_report = {
            "incident_title": "API Filter Error",
            "severity": "UNKNOWN",
            "mitre_attack_technique": "N/A",
            "explanation": "The AI API returned an empty or invalid response. This usually happens when the API provider's strict security filters block the raw attack payload found in the log.",
            "remediation_steps": "The app is secure, but the AI refused to read this specific payload. Try uploading a different log file."
        }
        
    print("DEBUG 4: Data cleanly structured.")
    
    # 4. Save the report to our SQLite Database
    new_incident = db_models.Incident(
        filename=file.filename,
        incident_title=ai_report.get("incident_title", "Unknown Threat"),
        severity=ai_report.get("severity", "UNKNOWN"),
        mitre_attack_technique=ai_report.get("mitre_attack_technique", "N/A"),
        explanation=ai_report.get("explanation", "No explanation provided."),
        remediation_steps=ai_report.get("remediation_steps", "No remediation steps provided.")
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    print("DEBUG 5: Saved permanently to Database.")
    
    # 5. Return the report explicitly formatted
    response_data = {
        "filename": file.filename,
        "status": "Analyzed and Saved to Database",
        "ai_analysis": ai_report
    }
    print("DEBUG 6: Sending payload back to React UI.\n")
    return JSONResponse(content=jsonable_encoder(response_data))

@router.get("/history")
def get_incident_history(db: Session = Depends(get_db)):
    past_incidents = db.query(db_models.Incident).all()
    return {"status": "success", "total": len(past_incidents), "data": past_incidents}