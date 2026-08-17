from pydantic import BaseModel
from typing import Optional

# 1. First, define what a single log entry looks like
class LogEntry(BaseModel):
    timestamp: str
    hostname: str
    service: str
    event_type: str
    user: str
    source_ip: str

# 2. Second, define the AI's output rules
class ThreatAnalysis(BaseModel):
    incident_title: str
    severity: str
    mitre_attack_technique: str
    explanation: str
    remediation_steps: str

# 3. Third, define the upload response (which now safely knows what ThreatAnalysis is!)
class UploadResponse(BaseModel):
    message: str
    filename: str
    total_logs_parsed: int
    ai_analysis: Optional[ThreatAnalysis] = None