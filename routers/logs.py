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
    # FIX: We are now passing 'log_data' instead of the old 'parsed_logs'
    ai_response = analyze_threats_with_ai(log_data)
    print("DEBUG 3: AI response received.")
    
    # 3. Extract data from the AI's response
    if hasattr(ai_response, "model_dump"):
        ai_report = ai_response.model_dump()
    elif hasattr(ai_response, "dict"):
        ai_report = ai_response.dict()
    elif isinstance(ai_response, str):
        ai_report = json.loads(ai_response)
    else:
        ai_report = ai_response
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