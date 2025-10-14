import pandas as pd
import re
from ..get_from_all_patient_data_by_string import get_from_all_patient_data_by_string

def parse_from_all_patient_data(dataset: dict, querry: str, DELIMITER: str = ";") -> pd.DataFrame:
    data = get_from_all_patient_data_by_string(dataset, querry, DELIMITER)
    records = []
    current_time = None
    
    for category, entries in data.items():
        for device, lines in entries.items():
            for line in lines:
                line = line.strip(";")
                
                # Zeitstempel
                time_match = re.match(r"^(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2})", line)
                if time_match:
                    current_time = time_match.group(1)
                    continue
                
                # Datenzeilen mit mindestens 3 Segmenten
                parts = [p for p in line.split(";") if p.strip() != ""]
                if len(parts) >= 3 and current_time:
                    parameter = parts[0].strip()
                    value = parts[1].strip()
                    records.append({
                        "Zeit": current_time,
                        "Kategorie": category,
                        "Sub-Kategorie": device,
                        "Parameter": parameter,
                        "Wert": value
                    })
    
    return pd.DataFrame(records)