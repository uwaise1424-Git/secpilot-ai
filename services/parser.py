import re
from models.schemas import LogEntry

def parse_auth_log(file_content: str):
    parsed_logs = []
    
    # This is a Regular Expression (Regex). It is basically a highly specific search pattern 
    # that tells Python exactly how to slice up the text in our log file.
    log_pattern = re.compile(
        r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
        r"(?P<hostname>\S+)\s+(?P<service>\w+)\[\d+\]:\s+"
        r"(?P<event_type>(?:Failed|Accepted) password)\s+for\s+"
        r"(?P<user>\S+)\s+from\s+(?P<source_ip>\S+)"
    )
    
    # Read the file line by line
    lines = file_content.splitlines()
    for line in lines:
        match = log_pattern.search(line)
        if match:
            # If the line matches our pattern, extract the data as a dictionary
            log_data = match.groupdict()
            # Validate and format it using our Pydantic schema
            parsed_logs.append(LogEntry(**log_data))
            
    return parsed_logs