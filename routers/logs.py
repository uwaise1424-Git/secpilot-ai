from fastapi import APIRouter, UploadFile, File
from services.parser import parse_auth_log
from services.ai_engine import analyze_threats_with_ai
from models.schemas import UploadResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_log(file: UploadFile = File(...)):
    # Read and decode the uploaded file
    content = await file.read()
    decoded_content = content.decode("utf-8")
    
    # Step 1: Parse the raw logs
    parsed_logs = parse_auth_log(decoded_content)
    
    # Step 2: Send parsed logs to AI for analysis
    ai_report = analyze_threats_with_ai(parsed_logs)
    
    # Step 3: Return the complete package to the user/dashboard
    return UploadResponse(
        message="Log file processed and analyzed successfully, bruh!",
        filename=file.filename,
        total_logs_parsed=len(parsed_logs),
        ai_analysis=ai_report
    )