from services.split_blocks import split_blocks
from parse_schemas.medication_model import MedicationModel
import pandas as pd
import re
from datetime import datetime
import logging
import json

# das könnte ein Problem werden - mLife exportiert hier nur 117h-Blöcke
# -> ich muss schauen, ob da ein anderer Export möglich ist.

logger = logging.getLogger(__name__)

def parse_fluidbalance_data(clean_file, DELIMITER: str = ";") -> pd.DataFrame:
    blocks = split_blocks(clean_file, DELIMITER)
    fluidbalance_blocks = blocks.get("Bilanz", {}).get("Bilanz", "")
    fluidbalance_list = []
    fluidbalance_blocks = remove_linebreaks_in_cells(fluidbalance_blocks)
    fluidbalance_blocks = [line.split(DELIMITER) for line in fluidbalance_blocks.splitlines()]
    
    DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}")
    
    with open("fluidtest.json", "w") as f:
        json.dump(fluidbalance_blocks, f)
    
    return pd.DataFrame({})

    buffer = []
    last_header = None
    for line in fluidbalance_blocks:
        if is_header(line):
            if line == last_header:
                continue
            if buffer and last_header:
                fluidbalance_list.extend(pack_medication(buffer, last_header, DELIMITER))
                buffer = []
            last_header = line
            continue
        if not last_header:
            continue
        buffer.append(line)
    if buffer and last_header:
        medication_list.extend(pack_medication(buffer, last_header, DELIMITER))

    result = pd.DataFrame([v.__dict__ for v in medication_list])
    logging.debug("Parsed %d medication rows", len(result))
    return result

def get_first_entry(l) -> str:
    for entry in l:
        if isinstance(entry, str) and entry != "":
            return entry
    return ""

def remove_linebreaks_in_cells(s: str) -> str:
    def replacer(match):
        return match.group(0).replace("\n", " ").replace("\r", "").replace("\"", "")
    return re.sub(r'"(.*?)"', replacer, s, flags=re.DOTALL)

def is_header(line: list[str]) -> bool:
    DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}")
    return not any(isinstance(tok, str) and DATE_RE.search(tok) for tok in line)

def pack_medication(lines: list[list], header: list, DELIMITER: str = ";") -> list[MedicationModel]:
    result = []
    category = get_first_entry(header)
    # Perfusoren Konzentration App.- form Start/Änderung Stopp Rate(mL/h)
    medication_index = header.index(category)
    concentration_index = header.index("Konzentration")
    application_index = header.index("App.- form")
    start_index = header.index("Start/Änderung")
    stop_index = header.index("Stopp")
    rate_index = header.index("Rate(mL/h)")
    for l in lines:
        start_timestamps = get_timestamps(l, start_index)
        stop_timestamps = get_timestamps(l, stop_index)
        rates = get_rates(l, rate_index)
        for i, start in enumerate(start_timestamps):
            try:
                stop=stop_timestamps[i]
            except:
                stop=None
            try:
                rate = rates[i]
            except:
                rate=None
                
            result.append(MedicationModel(
                medication=l[medication_index],
                category=category,
                concentration=l[concentration_index],
                application=l[application_index],
                start=start,
                stop=stop,
                rate=rate
                ))
    return result

def get_timestamps(l: list[str], i: int) -> list[datetime|None]:
    timestamps = []
    for ts_str in re.findall(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}", l[i]):
        for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%y %H:%M"):
            try:
                timestamps.append(datetime.strptime(ts_str.strip(), fmt))
                break
            except ValueError:
                continue
    return timestamps

def get_rates(l: list[str], i: int) -> list[float|None]:
    rates = []
    for rate_str in re.findall(r"\d+(?:[.,]\d+)?", l[i]):
        try:
            rates.append(float(rate_str.replace(",", ".")))
        except ValueError:
            rates.append(None)
    return rates