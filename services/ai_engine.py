import os
import json
from dotenv import load_dotenv
from groq import Groq
from models.schemas import ThreatAnalysis

# Load the hidden environment variables (your API key)
load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_threats_with_ai(parsed_logs: list) -> ThreatAnalysis:
    # Convert our list of parsed logs into a readable text format for the AI
    logs_text = "\n".join([f"{log.timestamp} | {log.source_ip} | {log.event_type} | {log.user}" for log in parsed_logs])
    
    # This is the "System Prompt" - it tells the AI exactly how to behave
    prompt = f"""
    You are an expert AI SOC Analyst. Review the following server logs and identify any security threats.
    Logs:
    {logs_text}
    
    Respond ONLY with a valid JSON object matching this exact structure:
    {{
        "incident_title": "Short title of the attack",
        "severity": "Low, Medium, High, or Critical",
        "mitre_attack_technique": "Name of the MITRE ATT&CK technique",
        "explanation": "Brief explanation of what the attacker did",
        "remediation_steps": "Actionable steps to fix it"
    }}
    """
    
    # Send the prompt to the Llama 3 model on Groq
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a highly skilled cybersecurity AI. Output strictly in JSON format."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-20b", # The most stable and accessible model for all tiers
        response_format={"type": "json_object"} # Forces the AI to strictly output JSON
    )
    
    # Extract the AI's response text
    ai_response_text = response.choices[0].message.content
    
    # Convert the JSON string into a Python dictionary, then lock it into our strict Pydantic model
    json_data = json.loads(ai_response_text)
    return ThreatAnalysis(**json_data)