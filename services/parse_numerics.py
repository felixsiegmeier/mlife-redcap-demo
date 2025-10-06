import re
import pandas as pd

DATE_RE = re.compile(r'\d{2}\.\d{2}\.\d{2}\s*\d{2}:\d{2}')

def _clean_value(s: str):
    if s is None:
        return None
    s = s.strip()
    if s == '':
        return None
    s = s.replace('(', '').replace(')', '')
    s = s.replace(',', '.')
    if s.startswith('+'):
        s = s[1:]
    # <4, >100 sollen Strings bleiben
    if re.match(r'^[<>]=?[-+]?\d+(\.\d+)?$', s):
        return s
    try:
        return float(s)
    except Exception:
        return s

def _extract_name_unit(param_raw: str):
    if not param_raw:
        return None, None
    param_raw = param_raw.strip()
    m = re.match(r'^(.*?)\s*\[(.+?)\]\s*$', param_raw)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return param_raw, None

def _parse_block_string(block_str: str, panel: str, DELIMITER=";"):
    lines = [ln.rstrip('\r') for ln in block_str.splitlines()]
    header_indices = [i for i,ln in enumerate(lines) if DATE_RE.search(ln)]
    rows = []
    for h_idx_idx, h_idx in enumerate(header_indices):
        header_line = lines[h_idx]
        header_tokens = header_line.split(DELIMITER)
        timestamp_positions = [i for i,t in enumerate(header_tokens) if DATE_RE.search(t)]
        timestamps = [header_tokens[i].strip() for i in timestamp_positions]
        end_idx = header_indices[h_idx_idx+1] if h_idx_idx+1 < len(header_indices) else len(lines)
        for ln in lines[h_idx+1:end_idx]:
            if not ln.strip():
                continue
            tokens = ln.split(DELIMITER)
            # finde Parameter-Spalte
            param_index = None
            for idx, tk in enumerate(tokens):
                if tk.strip() and not DATE_RE.search(tk):
                    param_index = idx
                    break
            if param_index is None:
                continue
            param_raw = tokens[param_index].strip()
            param_name, unit = _extract_name_unit(param_raw)
            # alle Werte durchlaufen
            for pos_idx, pos in enumerate(timestamp_positions):
                ts = timestamps[pos_idx]
                val = tokens[pos].strip() if pos < len(tokens) else ''
                val_clean = _clean_value(val)
                rows.append({
                    'panel': panel,
                    'parameter': param_name,
                    'unit': unit,
                    'timestamp': ts,
                    'value_raw': val if val != '' else None,
                    'value': val_clean
                })
    if not rows:
        return pd.DataFrame(columns=['panel','parameter','unit','timestamp','value_raw','value'])
    return pd.DataFrame(rows)

def parseNumerics(data: dict, DELIMITER: str = ";") -> pd.DataFrame:
    """
    data: dict mit Panels und Strings (Blockstruktur mit ; getrennt)
    DELIMITER: Trennzeichen (default ";")

    Gibt ein pandas.DataFrame im Long-Format zurück.
    """
    frames = []
    for key, block_str in data.items():
        if not isinstance(block_str, str):
            continue
        df = _parse_block_string(block_str, key, DELIMITER=DELIMITER)
        frames.append(df)
    if frames:
        result = pd.concat(frames, ignore_index=True)
    else:
        result = pd.DataFrame(columns=['panel','parameter','unit','timestamp','value_raw','value'])

    result['timestamp_parsed'] = pd.to_datetime(
    result['timestamp'],
    format='%d.%m.%y %H:%M',
    dayfirst=True,
    errors='coerce'
    )

    cols = ['panel','parameter','unit',
            'timestamp','timestamp_parsed','value_raw','value']

    result = result[cols].dropna(subset=["value"]).reset_index(drop=True)
    return result