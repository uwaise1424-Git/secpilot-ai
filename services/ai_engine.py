import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_threats_with_ai(log_data):
    system_prompt = """
    You are an expert AI Security Operations Center (SOC) Analyst. 
    Analyze the provided raw system logs for security threats. Map the attack to a specific MITRE ATT&CK technique.
    
    CRITICAL JSON RULES:
    1. Return your analysis strictly as a JSON object.
    2. NEVER use double quotes (") or backslashes (\) inside your explanation or remediation text. Use single quotes (') instead.
    3. ABSOLUTELY DO NOT copy/paste raw log payloads. Summarize the attack in your own words.
    
    {
      "incident_title": "Short title of the attack",
      "severity": "LOW, MEDIUM, HIGH, or CRITICAL",
      "mitre_attack_technique": "TXXXX - Name",
      "explanation": "Provide a deep, comprehensive technical analysis using ONLY single quotes.",
      "remediation_steps": "Provide a highly detailed, step-by-step incident response plan for a sysadmin."
    }
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze these raw logs:\n{log_data}"}
            ],
            temperature=0.2
        )
        
        raw_text = response.choices[0].message.content
        
        # 🚨 THE SMART EXTRACTOR
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            cleaned_text = raw_text[start_idx:end_idx+1]
        else:
            cleaned_text = raw_text # Fallback
            
        return cleaned_text
        
    except Exception as e:
        print(f"API Error: {e}")
        # Safe fallback so the server doesn't crash
        return json.dumps({
            "incident_title": "AI Engine Error",
            "severity": "UNKNOWN",
            "mitre_attack_technique": "N/A",
            "explanation": f"Failed to reach AI. Error: {str(e)}",
            "remediation_steps": "Check API key and connection."
        })