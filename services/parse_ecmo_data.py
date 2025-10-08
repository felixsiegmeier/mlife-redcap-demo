from services.split_blocks import split_blocks
from services.get_from_all_patient_data_by_string import get_from_all_patient_data_by_string
from schemas.ecmo_model import EcmoModel
import pandas as pd
import re
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

def parse_ecmo_data(clean_file, DELIMITER: str = ";") -> pd.DataFrame:
    blocks = split_blocks(clean_file, DELIMITER)
    ecmo_blocks = get_from_all_patient_data_by_string(blocks.get("ALLE Patientendaten", {}), "ECMO", DELIMITER)
    ecmo_list = []
    DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}")

    for key, lines in ecmo_blocks.get("ECMO", {}).items():
        timestamp = None
        for raw in lines:
            parts = raw.split(DELIMITER)
            # detect timestamp row
            if any(isinstance(tok, str) and DATE_RE.search(tok) for tok in parts):
                # find the token that contains the timestamp and parse that token
                timestamp = None
                for tok in parts:
                    if not isinstance(tok, str):
                        continue
                    if not DATE_RE.search(tok):
                        continue
                    ts_tok = tok.strip()
                    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%y %H:%M"):
                        try:
                            timestamp = datetime.strptime(ts_tok, fmt)
                            break
                        except ValueError:
                            continue
                    if timestamp is None:
                        logger.warning("Failed to parse timestamp token '%s'", ts_tok)
                    break
                continue
            if not timestamp:
                continue
            try:
                parameter = get_first_entry(parts)
                value_str = get_second_entry(parts)
                if value_str is None:
                    raise ValueError("missing value")
                try:
                    value = float(value_str.replace(",", "."))
                except ValueError:
                    value = value_str  # keep as string if not convertible
            except Exception as e:
                logger.warning(f"Failed to parse parameter or value: {e} in: {parts}")
                continue
            ecmo_list.append(EcmoModel(
                timestamp=timestamp,
                value=value,
                category=key,
                parameter=parameter,
                ))

    result = pd.DataFrame([v.__dict__ for v in ecmo_list])
    logging.debug("Parsed %d ecmo rows", len(result))
    return result

def get_first_entry(l) -> str | None:
    for entry in l:
        if isinstance(entry, str) and entry != "":
            return entry
    return None

def get_second_entry(l) -> str | None:
    first = False
    for entry in l:
        if not isinstance(entry, str):
            continue
        s = entry.strip()
        if s == "":
            continue
        if not first:
            first = True
            continue
        return s
    return None