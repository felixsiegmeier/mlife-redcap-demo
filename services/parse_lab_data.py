from services.split_blocks import split_blocks
from schemas.lab_model import LabModel
import pandas as pd
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def parse_lab_data(clean_file, DELIMITER: str = ";") -> pd.DataFrame:
    blocks = split_blocks(clean_file, DELIMITER)
    lab_list = []
    DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}")

    for key, block_str in blocks.get("Labor", {}).items():
        timestamps = None
        lines = [ln.rstrip('\r') for ln in block_str.splitlines()]
        for raw in lines:
            parts = raw.split(DELIMITER)
            # detect timestamp row
            if any(isinstance(tok, str) and DATE_RE.search(tok) for tok in parts):
                timestamps = [tok.strip() for tok in parts]
                continue
            if not timestamps:
                continue
            first_value = get_first_entry(parts)
            if not first_value:
                continue
            for i, token in enumerate(parts):
                if not isinstance(token, str) or token.strip() == "":
                    continue
                tok = token.strip().replace(",", ".")
                try:
                    value = float(tok)
                except (ValueError, TypeError):
                    continue
                try:
                    ts_str = timestamps[i]
                except (IndexError, TypeError):
                    continue
                timestamp = None
                for fmt in ("%d.%m.%y %H:%M", "%d.%m.%Y %H:%M"):
                    try:
                        timestamp = datetime.strptime(ts_str, fmt)
                        break
                    except Exception:
                        continue
                if timestamp is None:
                    continue
                lab_list.append(LabModel(
                    timestamp=timestamp,
                    value=value,
                    category=key.strip("Labor:").strip(),
                    parameter=first_value[1],
                ))

    result = pd.DataFrame([v.__dict__ for v in lab_list])
    logging.debug("Parsed %d lab rows", len(result))
    return result

def get_first_entry(l) -> tuple[int, str] | None:
    for i, entry in enumerate(l):
        if isinstance(entry, str) and entry != "":
            return (i, entry)
    return None