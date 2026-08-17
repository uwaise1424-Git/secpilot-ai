from sqlalchemy import Column, Integer, String
from database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    incident_title = Column(String)
    severity = Column(String)
    mitre_attack_technique = Column(String)
    explanation = Column(String)
    remediation_steps = Column(String)