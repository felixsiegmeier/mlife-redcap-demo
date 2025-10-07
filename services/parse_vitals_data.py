from services.split_blocks import split_blocks
from schemas.vitals_model import VitalsModel
import pandas as pd
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def parse_vitals_data(clean_file, DELIMITER: str = ";") -> pd.DataFrame:
    blocks = split_blocks(clean_file, DELIMITER)
    vitals_list = []
    DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}")

    for key, block_str in blocks.get("Vitaldaten", {}).items():
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
                vitals_list.append(VitalsModel(
                    timestamp=timestamp,
                    value=value,
                    category=key,
                    parameter=first_value[1]
                ))

    result = pd.DataFrame([v.__dict__ for v in vitals_list])
    logging.debug("Parsed %d vitals rows", len(result))
    return result


def get_first_entry(l) -> tuple[int, str] | None:
    for i, entry in enumerate(l):
        if isinstance(entry, str) and entry != "":
            return (i, entry)
    return None