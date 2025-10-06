from services.split_blocks import splitBlocks
from schemas.vitals import Vitals
import pandas as pd
import re

def parsVitals(clean_file, DELIMITER: str = ";") -> pd.DataFrame:
    split_blocks = splitBlocks(clean_file, DELIMITER)
    result = pd.DataFrame()

    for key, block_str in split_blocks["Vitaldaten"].items():
        DATE_RE = re.compile(r'\d{2}\.\d{2}\.\d{2}\s*\d{2}:\d{2}')
        lines = [ln.rstrip('\r') for ln in block_str.splitlines()]
        for line in lines:
            line = line.split(";")
            if DATE_RE.search(line[3]):
                timestamps = line
                continue
            if not timestamps:
                continue
            first_value = get_first_entry(line)
            if not first_value:
                continue
            for i, value in enumerate(line):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    continue
                if isinstance(value, float):
                    vital = Vitals(
                        timestamp=timestamps[i], # next: in timestamp parsen
                        value=value, 
                        category=key, 
                        parameter=first_value[1]
                        )
                    print(vital)
    
    return result

def get_first_entry(l) -> tuple[int, str] | None:
    for i, entry in enumerate(l):
        if isinstance(entry, str) and not entry == "":
            return (i, entry)
    return None