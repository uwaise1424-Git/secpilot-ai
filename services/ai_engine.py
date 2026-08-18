import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_threats_with_ai(log_data):
    system_prompt = """
    You are an expert AI Security Operations Center (SOC) Analyst. 
    You will receive raw system logs. They could be Linux Auth logs, Nginx Web Server logs, or Network Firewall logs.
    
    1. Identify the log type and analyze it for security threats.
    2. Map the attack to a specific MITRE ATT&CK technique.
    3. Return ONLY a pure JSON object. Do not include markdown formatting or backticks.
    
    Strict JSON Format required:
    {
      "incident_title": "Short title of the attack",
      "severity": "LOW, MEDIUM, HIGH, or CRITICAL",
      "mitre_attack_technique": "TXXXX - Name",
      "explanation": "1-2 sentences explaining what the attacker is doing.",
      "remediation_steps": "1-2 sentences on how to stop it."
    }
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze these raw logs:\n{log_data}"}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        # Safe fallback so the server doesn't crash
        return json.dumps({
            "incident_title": "AI Engine Error",
            "severity": "UNKNOWN",
            "mitre_attack_technique": "N/A",
            "explanation": f"Failed to reach AI. Error: {str(e)}",
            "remediation_steps": "Check Groq API key and connection."
        })