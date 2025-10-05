import io
import csv
from typing import Dict, List, Optional

import pandas as pd


def _safe_join_lines(cell: Optional[str]) -> Optional[str]:
    if cell is None:
        return None
    parts = [ln.strip() for ln in str(cell).splitlines() if ln.strip()]
    return " | ".join(parts) if parts else None


def _split_lines(cell: Optional[str]) -> List[str]:
    if cell is None:
        return []
    return [ln.strip() for ln in str(cell).splitlines() if ln.strip()]


def _parse_rate(s: Optional[str]):
    if s is None or s == "":
        return None
    s = str(s).replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return s


def parseMedications(data: Dict[str, str], DELIMITER: str = ";") -> pd.DataFrame:
    import io
    import csv
    from typing import Dict, List, Optional

    import pandas as pd


    _MODULE_TEMPLATE = "clean_parseMedications_v1"


    def _safe_join_lines(cell: Optional[str]) -> Optional[str]:
        if cell is None:
            return None
        parts = [ln.strip() for ln in str(cell).splitlines() if ln.strip()]
        return " | ".join(parts) if parts else None


    def _split_lines(cell: Optional[str]) -> List[str]:
        if cell is None:
            return []
        return [ln.strip() for ln in str(cell).splitlines() if ln.strip()]


    def _parse_rate(s: Optional[str]):
        if s is None or s == "":
            return None
        s = str(s).replace(",", ".").strip()
        try:
            return float(s)
        except Exception:
            return s


    def parseMedications(data: Dict[str, str], DELIMITER: str = ";") -> pd.DataFrame:
        """Minimal, robust parser for medication table blocks.

        Inputs:
          - data: mapping panel_name -> semicolon-delimited CSV block (string).
          - DELIMITER: delimiter used in the block (default ';').

        Output: pandas.DataFrame with parsed rows.
        """
        frames: List[Dict[str, Optional[object]]] = []

        for panel, block_str in data.items():
            if not isinstance(block_str, str):
                continue

            f = io.StringIO(block_str)
            reader = csv.reader(f, delimiter=DELIMITER, quotechar='"')
            rows = [r for r in reader]
            if not rows:
                continue

            # find header row
            header_idx: Optional[int] = None
            header_lower: List[str] = []
            for i, row in enumerate(rows):
                joined = " ".join(((c or "").lower() for c in row))
                if any(k in joined for k in ("medik", "konzentr", "app", "start", "stopp", "rate")):
                    header_idx = i
                    header_lower = [(c or "").lower() for c in row]
                    break

            if header_idx is None:
                header_idx = 0
                header_lower = [(c or "").lower() for c in rows[0]]

            def find_col(subs: List[str]) -> Optional[int]:
                for idx, val in enumerate(header_lower):
                    if any(s in val for s in subs):
                        return idx
                return None

            med_idx = find_col(["medik", "medikations", "medikament"]) or 0
            conc_idx = find_col(["konzentr"])
            app_idx = find_col(["app", "app.-", "applik"])
            start_idx = find_col(["start", "änderung"])
            stop_idx = find_col(["stopp", "stop"])
            rate_idx = find_col(["rate", "ml/h", "rate(m"]) if header_lower else None

            if rate_idx is None:
                rate_idx = max(len(header_lower) - 1, 0)

            for row in rows[header_idx + 1:]:
                if not any(isinstance(c, str) and c.strip() for c in row):
                    continue

                def get_cell(idx: Optional[int]) -> str:
                    return row[idx] if idx is not None and idx < len(row) else ""

                med_raw = get_cell(med_idx)
                conc_raw = get_cell(conc_idx) if conc_idx is not None else ""
                app_raw = get_cell(app_idx) if app_idx is not None else ""
                start_raw = get_cell(start_idx) if start_idx is not None else ""
                stop_raw = get_cell(stop_idx) if stop_idx is not None else ""
                rate_raw = get_cell(rate_idx) if rate_idx is not None else ""

                medication = _safe_join_lines(med_raw)
                concentration = _safe_join_lines(conc_raw)
                app_form = _safe_join_lines(app_raw)

                starts = _split_lines(start_raw)
                stops = _split_lines(stop_raw)
                rates = _split_lines(rate_raw)

                max_len = max(len(starts), len(stops), len(rates), 1)
                for i in range(max_len):
                    s_raw = starts[i] if i < len(starts) else None
                    t_raw = stops[i] if i < len(stops) else None
                    rate_val_raw = rates[i] if i < len(rates) else None

                    s_raw = s_raw.strip() if isinstance(s_raw, str) and s_raw.strip() != "" else None
                    t_raw = t_raw.strip() if isinstance(t_raw, str) and t_raw.strip() != "" else None

                    start_parsed = pd.to_datetime(s_raw, dayfirst=True, errors='coerce') if s_raw else None
                    stop_parsed = pd.to_datetime(t_raw, dayfirst=True, errors='coerce') if t_raw else None

                    rate_parsed = _parse_rate(rate_val_raw)

                    frames.append({
                        'panel': panel,
                        'medication': medication,
                        'concentration': concentration,
                        'app_form': app_form,
                        'start_raw': s_raw,
                        'stop_raw': t_raw,
                        'rate_raw': rate_val_raw,
                        'start_parsed': start_parsed,
                        'stop_parsed': stop_parsed,
                        'rate': rate_parsed,
                    })

        if frames:
            df = pd.DataFrame(frames)
        else:
            df = pd.DataFrame(columns=[
                'panel', 'medication', 'concentration', 'app_form',
                'start_raw', 'stop_raw', 'rate_raw', 'start_parsed', 'stop_parsed', 'rate'
            ])

        return df
import pandas as pd


def _safe_join_lines(cell: Optional[str]) -> Optional[str]:
    """Collapse internal newlines in a cell into a single string (or None)."""
    if cell is None:
        return None
    parts = [ln.strip() for ln in str(cell).splitlines() if ln.strip()]
    return " | ".join(parts) if parts else None


def _split_lines(cell: Optional[str]) -> List[str]:
    """Split a possibly-multiline cell into a list of non-empty lines."""
    if cell is None:
        return []
    return [ln.strip() for ln in str(cell).splitlines() if ln.strip()]


def _parse_rate(s: Optional[str]):
    """Normalize numeric rate strings (commas->dots) and convert to float when possible."""
    if s is None or s == "":
        return None
    s = str(s).replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return s


def parseMedications(data: Dict[str, str], DELIMITER: str = ";") -> pd.DataFrame:
    """
    Parse medication blocks into a long DataFrame.

    - `data` is a mapping panel_name -> semicolon-delimited block string. Quoted
      cells may contain embedded newlines.
    - Medication / concentration / app-form fields are collapsed into single-cell
      strings (internal newlines joined with " | ").
    - Start / Stop / Rate fields that contain multiple newline-separated entries
      are expanded into multiple rows (one per entry) while duplicating the
      medication fields.

    Returns a pandas.DataFrame with columns:
    panel, medication, concentration, app_form, start_raw, stop_raw, rate_raw,
    start_parsed, stop_parsed, rate
    """
    frames = []

    for panel, block_str in data.items():
        if not isinstance(block_str, str):
            continue

        f = io.StringIO(block_str)
        reader = csv.reader(f, delimiter=DELIMITER, quotechar='"')
        rows = [r for r in reader]
        if not rows:
            continue

        # Heuristically find header row by searching for known keywords
        header_idx: Optional[int] = None
        header_lower: List[str] = []
        for i, row in enumerate(rows):
            joined = " ".join([(c or "").lower() for c in row])
            if any(k in joined for k in ["medik", "konzentr", "app", "start", "stopp", "rate"]):
                header_idx = i
                header_lower = [(c or "").lower() for c in row]
                break

        if header_idx is None:
            header_idx = 0
            header_lower = [(c or "").lower() for c in rows[0]]

        def find_col(subs: List[str]) -> Optional[int]:
            for idx, val in enumerate(header_lower):
                if any(s in val for s in subs):
                    return idx
            return None

        med_idx = find_col(["medik", "medikations", "medikament"]) or 0
        conc_idx = find_col(["konzentr"])
        app_idx = find_col(["app", "app.-", "applik"])
        start_idx = find_col(["start", "änderung"])
        stop_idx = find_col(["stopp", "stop"])
        rate_idx = find_col(["rate", "ml/h", "rate(m"]) if header_lower else None

        if rate_idx is None:
            rate_idx = max(len(header_lower) - 1, 0)

        for row in rows[header_idx + 1:]:
            if not any(isinstance(c, str) and c.strip() for c in row):
                continue

            def get_cell(idx: Optional[int]) -> str:
                return row[idx] if idx is not None and idx < len(row) else ""

            med_raw = get_cell(med_idx)
            conc_raw = get_cell(conc_idx) if conc_idx is not None else ""
            app_raw = get_cell(app_idx) if app_idx is not None else ""
            start_raw = get_cell(start_idx) if start_idx is not None else ""
            stop_raw = get_cell(stop_idx) if stop_idx is not None else ""
            rate_raw = get_cell(rate_idx) if rate_idx is not None else ""

            medication = _safe_join_lines(med_raw)
            concentration = _safe_join_lines(conc_raw)
            app_form = _safe_join_lines(app_raw)

            starts = _split_lines(start_raw)
            stops = _split_lines(stop_raw)
            rates = _split_lines(rate_raw)

            max_len = max(len(starts), len(stops), len(rates), 1)
            for i in range(max_len):
                s_raw = starts[i] if i < len(starts) else None
                t_raw = stops[i] if i < len(stops) else None
                rate_val_raw = rates[i] if i < len(rates) else None

                s_raw = s_raw.strip() if isinstance(s_raw, str) and s_raw.strip() != "" else None
                t_raw = t_raw.strip() if isinstance(t_raw, str) and t_raw.strip() != "" else None

                start_parsed = pd.to_datetime(s_raw, dayfirst=True, errors='coerce') if s_raw else None
                stop_parsed = pd.to_datetime(t_raw, dayfirst=True, errors='coerce') if t_raw else None

                rate_parsed = _parse_rate(rate_val_raw)

                frames.append({
                    'panel': panel,
                    'medication': medication,
                    'concentration': concentration,
                    'app_form': app_form,
                    'start_raw': s_raw,
                    'stop_raw': t_raw,
                    'rate_raw': rate_val_raw,
                    'start_parsed': start_parsed,
                    'stop_parsed': stop_parsed,
                    'rate': rate_parsed,
                })

    if frames:
        df = pd.DataFrame(frames)
    else:
        df = pd.DataFrame(columns=[
            'panel', 'medication', 'concentration', 'app_form',
            'start_raw', 'stop_raw', 'rate_raw', 'start_parsed', 'stop_parsed', 'rate'
        ])

    return df

				if frames:
					df = pd.DataFrame(frames)
				else:
					df = pd.DataFrame(columns=['panel', 'medication', 'concentration', 'app_form', 'start_raw', 'stop_raw', 'rate_raw', 'start_parsed', 'stop_parsed', 'rate'])

				return df



