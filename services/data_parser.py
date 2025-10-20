"""
DataParser Klasse zur Konsolidierung aller Parser und Hilfsfunktionen.
Diese Klasse akzeptiert eine Datei als Input und bietet alle verfügbaren Parser als eigene Methoden.
"""

import pandas as pd
import re
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, date
import logging

# Import nur der Schema-Definitionen
from schemas.parse_schemas.vitals import VitalsModel
from schemas.parse_schemas.lab import LabModel
from schemas.parse_schemas.respiratory import RespiratoryModel
from schemas.parse_schemas.ecmo import EcmoModel
from schemas.parse_schemas.impella import ImpellaModel
from schemas.parse_schemas.crrt import CrrtModel
from schemas.parse_schemas.medication import MedicationModel

logger = logging.getLogger(__name__)


class DataParser:
    """Einfache Klasse für alle Parsing-Operationen."""
    
    def __init__(self, file: str, delimiter: str = ";"):
        """Initialisiert den DataParser."""
        self.raw_file = file
        self.delimiter = delimiter
        self._clean_file = None
        self._blocks = None
        
        self.headers = {
            "Vitaldaten": ['Online erfasste Vitaldaten', 'Manuell erfasste Vitaldaten'],
            "Respiratordaten": ['Online erfasste Respiratorwerte', 'Beatmung', 'Manuell erfasste Respiratorwerte'],
            "Labor": ['Labor: Blutgase arteriell', 'Labor: Blutgase venös', 'Labor: Blutgase gv', 
                     'Labor: Blutgase unspez.', 'Labor: Blutbild', 'Labor: Differentialblutbild',
                     'Labor: Blutgruppe', 'Labor: Gerinnung', 'Labor: TEG', 'Labor: TAT',
                     'Labor: Enzyme', 'Labor: Retention', 'Labor: Lipide', 'Labor: Proteine',
                     'Labor: Elektrolyte', 'Labor: Blutzucker', 'Labor: Klinische Chemie',
                     'Labor: Medikamentenspiegel', 'Labor: Schilddrüse', 'Labor: Serologie/Infektion'],
            'Medikamentengaben': ["Medikamentengaben"],
            'ALLE Patientendaten': ["ALLE Patientendaten"]
        }
    
    def _clean_csv(self) -> str:
        """Bereinigt die CSV-Datei."""
        if self._clean_file is not None:
            return self._clean_file
            
        lines = self.raw_file.splitlines()
        skip = {len(lines) - 1}  # Skip last line
        headers = []
        
        # Find lines to skip
        for i, line in enumerate(lines):
            line_stripped = line.lstrip()
            if "Ausdruck: Gesamte Akte" in line_stripped:
                headers.append(i)
            elif any(text in line_stripped for text in [
                "Bei aktuell laufenden Statusmodulen",
                "Datum/Uhrzeit bezieht sich jeweils auf den Intervallstart."
            ]):
                skip.add(i)
                if "Datum/Uhrzeit" in line_stripped:
                    skip.add(i - 1)
            elif re.search(r"Intervall:\s*\d{2}\s*min\.,?", line_stripped):
                skip.add(i)
        
        # Skip header blocks
        for j, h in enumerate(headers):
            skip.update(range(h, min(h + 8, len(lines))))
            if j > 0 and h - 1 >= 0:
                skip.add(h - 1)
        
        # Build clean file
        clean_lines = [line for i, line in enumerate(lines) if i not in skip]
        self._clean_file = "\n".join(clean_lines)
        return self._clean_file
    
    def _split_blocks(self) -> Dict[str, Dict[str, str]]:
        """Teilt die Datei in kategorisierte Blöcke auf."""
        if self._blocks is not None:
            return self._blocks
            
        lines = self._clean_csv().splitlines()
        result = {category: {} for category in self.headers}
        current_category = None
        current_block = None
        buffer = []

        for line in lines:
            key = line.split(self.delimiter, 1)[0].strip()
            
            # Check if line starts a new block
            found_category = None
            for category, blocks in self.headers.items():
                if key in blocks:
                    found_category = category
                    break
            
            if found_category:
                # Save previous buffer
                if current_category and current_block and buffer:
                    result[current_category][current_block] = "\n".join(buffer).strip()
                # Start new block
                current_category = found_category
                current_block = key
                buffer = []
            else:
                buffer.append(line)
        
        # Save final buffer
        if current_category and current_block and buffer:
            result[current_category][current_block] = "\n".join(buffer).strip()
            
        self._blocks = result
        return result
    
    def _get_first_entry(self, parts) -> Optional[Tuple[int, str]]:
        """Findet ersten nicht-leeren Eintrag."""
        for i, entry in enumerate(parts):
            if isinstance(entry, str) and entry.strip():
                return (i, entry.strip())
        return None
    
    def _parse_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Parst Timestamp."""
        ts_str = ts_str.strip()
        for fmt in ("%d.%m.%y %H:%M", "%d.%m.%Y %H:%M"):
            try:
                return datetime.strptime(ts_str, fmt)
            except (ValueError, TypeError):
                continue
        return None
    
    def _is_timestamp_row(self, parts) -> bool:
        """Prüft ob Zeile Timestamps enthält."""
        date_pattern = re.compile(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}")
        return any(isinstance(tok, str) and date_pattern.search(tok) for tok in parts)
    
    def _parse_table_data(self, category_name: str, data_class, **options):
        """Parst tabellarische Daten (Vitals, Respiratory, Lab)."""
        blocks = self._split_blocks().get(category_name, {})
        data_list = []

        for key, block_str in blocks.items():
            timestamps = None
            lines = [line.rstrip('\r') for line in block_str.splitlines()]
            
            for line in lines:
                parts = line.split(self.delimiter)
                
                # Timestamp row?
                if self._is_timestamp_row(parts):
                    timestamps = [tok.strip() for tok in parts]
                    continue
                    
                if not timestamps:
                    continue
                    
                first_entry = self._get_first_entry(parts)
                if not first_entry:
                    continue
                    
                # Parse values
                for i, token in enumerate(parts):
                    if not isinstance(token, str) or not token.strip():
                        continue
                        
                    # Skip parameter column for lab data
                    if options.get('skip_first') and i == first_entry[0]:
                        continue
                        
                    # Clean token
                    clean_token = token.strip().replace(",", ".")
                    if options.get('clean_lab'):
                        clean_token = clean_token.replace("(-)", "").replace("(+)", "")
                        
                    try:
                        value = float(clean_token)
                    except (ValueError, TypeError):
                        continue
                        
                    # Get timestamp
                    try:
                        timestamp = self._parse_timestamp(timestamps[i])
                        if not timestamp:
                            continue
                    except (IndexError, TypeError):
                        continue
                        
                    # Clean category name
                    category = key.replace("Labor:", "").strip() if "Labor:" in key else key.strip()
                    
                    data_list.append(data_class(
                        timestamp=timestamp,
                        value=value,
                        category=category,
                        parameter=first_entry[1]
                    ))

        return pd.DataFrame([item.__dict__ for item in data_list])
    
    def parse_vitals_data(self) -> pd.DataFrame:
        """Parst Vitaldaten."""
        return self._parse_table_data("Vitaldaten", VitalsModel)
    
    def parse_respiratory_data(self) -> pd.DataFrame:
        """Parst Respiratordaten."""
        return self._parse_table_data("Respiratordaten", RespiratoryModel)
    
    def parse_lab_data(self) -> pd.DataFrame:
        """Parst Labordaten."""
        return self._parse_table_data("Labor", LabModel, skip_first=True, clean_lab=True)
    
    def _extract_all_patient_data_headers(self, data_str: str) -> set:
        """Input ist der String-Block 'ALLE Patientendaten'.
        
        Liefert ein Set mit allen Überschriften, die als dritte Spalte in Zeilen
        mit zwei führenden leeren Feldern erscheinen.
        """
        lines = data_str.splitlines()
        headers_set = set()
        for line in lines:
            l = line.split(self.delimiter)
            if len(l) > 2 and l[0] == "" and l[1] == "" and l[2] and l[2] != "Datum":
                headers_set.add(l[2])
        return headers_set

    def _get_from_all_patient_data_by_string(self, query: str) -> Dict[str, Dict[str, List[str]]]:
        """Suche in den "ALLE Patientendaten"-Blöcken nach Headern, die `query` enthalten.
        
        Originalimplementierung aus get_from_all_patient_data_by_string.py
        """
        # Extrahiere den String aus der Datenstruktur
        patient_data = self._split_blocks().get("ALLE Patientendaten", {})
        if isinstance(patient_data, dict):
            # Falls es ein Dict ist, nehme den ersten Wert (String)
            data_str = next(iter(patient_data.values()), "")
        else:
            data_str = patient_data

        # Alle bekannten Header extrahieren
        headers = self._extract_all_patient_data_headers(data_str)

        # Nur die Header behalten, die den Suchbegriff enthalten (case-insensitiv)
        matching_headers = [header for header in headers if query.lower() in header.lower()]

        lines = data_str.splitlines()
        # Ergebnis-Dict vorbereiten: jeder gefundene Header bekommt ein leeres Dict
        result: Dict[str, Dict[str, List[str]]] = {header: {} for header in matching_headers}

        current_header: Optional[str] = None
        current_sub_header_counter = 1
        current_sub_header: Optional[str] = None
        current_sub_header_line: Optional[str] = None
        buffer: List[str] = []

        for line in lines:
            parts = line.split(self.delimiter)
            # Wir erwarten mindestens 3 Felder; sonst ist die Zeile uninteressant
            if len(parts) < 3:
                continue

            key = parts[2]

            if key in headers:
                # Header-Zeile gefunden -> vorherigen Buffer in das aktuelle Sub-Header-Objekt
                if current_header is not None and current_sub_header is not None and buffer:
                    result[current_header].setdefault(current_sub_header, []).extend(buffer)
                    buffer = []

                # Wenn der Header zu unseren gesuchten Headern gehört, (re)starten wir ein Sub-Header
                if key in matching_headers:
                    # Derselbe Header tritt erneut auf: prüfen, ob sich die konkrete Zeile unterscheidet
                    if key == current_header:
                        if current_sub_header_line is None:
                            current_sub_header_line = line
                        elif line != current_sub_header_line:
                            # Neuer Abschnitt desselben Headers -> Zähler erhöhen
                            current_sub_header_counter += 1
                            current_sub_header_line = line
                    else:
                        # Neuer Header -> Zähler zurücksetzen
                        current_sub_header_counter = 1

                    current_header = key
                    current_sub_header = f"{current_header} {current_sub_header_counter}"
                    # Initialisiere die Liste für das Sub-Header (sicherer Zugriff)
                    result[current_header].setdefault(current_sub_header, [])
                else:
                    # Gefundener Header ist nicht in unseren Suchergebnissen -> Sammeln stoppen
                    current_header = None
                    current_sub_header = None
                    current_sub_header_line = None
                    current_sub_header_counter = 1
            else:
                # Keine Header-Zeile: wenn wir in einem relevanten Header sind, sammeln
                if current_header is not None:
                    buffer.append(line)

        # Restlichen Buffer in das letzte Sub-Header schreiben
        if current_header is not None and current_sub_header is not None and buffer:
            result[current_header].setdefault(current_sub_header, []).extend(buffer)

        return result
    
    def _get_device_values(self, parts) -> Tuple[Optional[str], Optional[str]]:
        """Extrahiert Parameter und Wert aus Device-Zeile."""
        non_empty = [entry for entry in parts if isinstance(entry, str) and entry.strip()]
        if len(non_empty) >= 2:
            return non_empty[0], non_empty[1]
        return None, None
    
    def _find_timestamp(self, parts) -> Optional[datetime]:
        """Findet Timestamp in parts."""
        for token in parts:
            if isinstance(token, str) and re.search(r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}", token):
                return self._parse_timestamp(token)
        return None
    
    def _parse_device_data(self, search_term: str, data_class, nested=False):
        """Parst Device-Daten (ECMO, Impella, CRRT)."""
        device_blocks = self._get_from_all_patient_data_by_string(search_term)
        data_list = []

        def process_lines(lines, category):
            timestamp = None
            for line in lines:
                parts = line.split(self.delimiter)
                
                if self._is_timestamp_row(parts):
                    timestamp = self._find_timestamp(parts)
                    continue
                    
                if not timestamp:
                    continue
                    
                parameter, value_str = self._get_device_values(parts)
                if not parameter or not value_str:
                    continue
                    
                try:
                    value = float(value_str.replace(",", "."))
                except ValueError:
                    value = value_str
                    
                data_list.append(data_class(
                    timestamp=timestamp,
                    value=value,
                    category=category,
                    parameter=parameter
                ))

        if nested:
            # Impella/CRRT structure
            for key, device_dict in device_blocks.items():
                for device_key, lines in device_dict.items():
                    process_lines(lines, device_key)
        else:
            # ECMO structure
            for key, lines in device_blocks.get(search_term, {}).items():
                process_lines(lines, key)

        return pd.DataFrame([item.__dict__ for item in data_list])
    
    def parse_ecmo_data(self) -> pd.DataFrame:
        """Parst ECMO-Daten."""
        return self._parse_device_data("ECMO", EcmoModel, nested=False)
    
    def parse_impella_data(self) -> pd.DataFrame:
        """Parst Impella-Daten."""
        return self._parse_device_data("Impella", ImpellaModel, nested=True)
    
    def parse_crrt_data(self) -> pd.DataFrame:
        """Parst CRRT-Daten."""
        return self._parse_device_data("Hämofilter", CrrtModel, nested=True)
    
    def parse_nirs_data(self) -> pd.DataFrame:
        """Parst NIRS-Daten (PSI/NIRS/ICP) als Vitaldaten."""
        nirs_blocks = self._get_from_all_patient_data_by_string("PSI/NIRS/ICP")
        data_list = []
        
        for key, nirs_dict in nirs_blocks.items():
            for nirs_key, lines in nirs_dict.items():
                current_timestamp = None
                
                for line in lines:
                    parts = line.split(self.delimiter)
                    
                    # Prüfe auf Timestamp-Zeile (Format: ;;;DD.MM.YYYY HH:MM;;...)
                    if (len(parts) >= 4 and 
                        parts[0] == "" and parts[1] == "" and parts[2] == "" and 
                        parts[3].strip()):
                        
                        timestamp_str = parts[3].strip()
                        if re.search(r"\d{2}\.\d{2}\.\d{4}\s*\d{2}:\d{2}", timestamp_str):
                            current_timestamp = self._parse_timestamp(timestamp_str)
                        continue
                    
                    # Prüfe auf Datenzeile (Format: ;;;;Parameter;;;;;Wert;;;;...)
                    if (len(parts) >= 10 and 
                        parts[0] == "" and parts[1] == "" and parts[2] == "" and parts[3] == "" and
                        parts[4].strip() and parts[9].strip()):  # Parameter und Wert vorhanden
                        
                        if not current_timestamp:
                            continue
                            
                        parameter = parts[4].strip()
                        value_str = parts[9].strip()
                        
                        # Versuche Wert zu parsen
                        try:
                            value = float(value_str)
                        except (ValueError, TypeError):
                            continue
                        
                        # Erstelle VitalsModel-Eintrag mit category "nirs"
                        data_list.append(VitalsModel(
                            timestamp=current_timestamp,
                            value=value,
                            category="nirs",
                            parameter=parameter
                        ))
        
        return pd.DataFrame([item.__dict__ for item in data_list])
    
    def _clean_medication_text(self, text: str) -> str:
        """Bereinigt Medikamenten-Text."""
        return re.sub(r'"(.*?)"', lambda m: m.group(0).replace("\n", " ").replace("\r", "").replace('"', ""), 
                     text, flags=re.DOTALL)
    
    def _extract_from_cell(self, cell_content: str, pattern: str, converter=None) -> List:
        """Extrahiert Werte aus Zelle mit Pattern."""
        matches = re.findall(pattern, cell_content)
        if converter:
            return [converter(match) for match in matches if converter(match) is not None]
        return matches
    
    def _get_medication_columns(self, header) -> Optional[Dict[str, int]]:
        """Findet Spalten-Indices für Medikamente."""
        category = next((entry for entry in header if isinstance(entry, str) and entry.strip()), "")
        try:
            return {
                'medication': header.index(category),
                'concentration': header.index("Konzentration"),
                'application': header.index("App.- form"),
                'start': header.index("Start/Änderung"),
                'stop': header.index("Stopp"),
                'rate': header.index("Rate(mL/h)")
            }
        except ValueError:
            return None

    def parse_medication_data(self) -> pd.DataFrame:
        """Parst Medikamentendaten."""
        blocks = self._split_blocks()
        med_text = blocks.get("Medikamentengaben", {}).get("Medikamentengaben", "")
        
        # Bereinige Text
        clean_text = self._clean_medication_text(med_text)
        lines = [line.split(self.delimiter) for line in clean_text.splitlines()]
        
        data_list = []
        buffer = []
        current_header = None
        
        for line in lines:
            # Header = keine Timestamps
            if not self._is_timestamp_row(line):
                # Verarbeite vorherigen Block
                if buffer and current_header:
                    cols = self._get_medication_columns(current_header)
                    if cols:
                        data_list.extend(self._process_medication_block(buffer, cols, current_header))
                # Neuer Header
                current_header = line
                buffer = []
            else:
                if current_header:
                    buffer.append(line)
        
        # Letzter Block
        if buffer and current_header:
            cols = self._get_medication_columns(current_header)
            if cols:
                data_list.extend(self._process_medication_block(buffer, cols, current_header))
        
        return pd.DataFrame([item.__dict__ for item in data_list])
    
    def _process_medication_block(self, lines, cols, header) -> List[MedicationModel]:
        """Verarbeitet Medikamenten-Block."""
        result = []
        category = next((entry for entry in header if isinstance(entry, str) and entry.strip()), "")
        
        for line in lines:
            if len(line) <= max(cols.values()):
                continue
                
            # Extrahiere Timestamps und Raten
            start_times = self._extract_from_cell(line[cols['start']], r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}", self._parse_timestamp)
            stop_times = self._extract_from_cell(line[cols['stop']], r"\d{2}\.\d{2}\.\d{2,4}\s*\d{2}:\d{2}", self._parse_timestamp) 
            rates = self._extract_from_cell(line[cols['rate']], r"\d+(?:[.,]\d+)?", lambda x: float(x.replace(",", ".")))
            
            # Erstelle Einträge
            for i, start in enumerate(start_times):
                result.append(MedicationModel(
                    medication=line[cols['medication']],
                    category=category,
                    concentration=line[cols['concentration']],
                    application=line[cols['application']],
                    start=start,
                    stop=stop_times[i] if i < len(stop_times) else None,
                    rate=rates[i] if i < len(rates) else None
                ))
        
        return result
    
    def parse_fluidbalance_data(self) -> pd.DataFrame:
        """Parst Flüssigkeitsbilanz (noch nicht implementiert)."""
        return pd.DataFrame()
    
    def get_blocks(self) -> Dict[str, Dict[str, str]]:
        """Gibt alle Datenblöcke zurück."""
        return self._split_blocks()
    
    def parse_all_data(self) -> Dict[str, pd.DataFrame]:
        """Parst alle Daten."""
        return {
            'vitals': self.parse_vitals_data(),
            'respiratory': self.parse_respiratory_data(),
            'lab': self.parse_lab_data(),
            'ecmo': self.parse_ecmo_data(),
            'impella': self.parse_impella_data(),
            'crrt': self.parse_crrt_data(),
            'medication': self.parse_medication_data(),
            'fluidbalance': self.parse_fluidbalance_data(),
            'nirs': self.parse_nirs_data()
        }
    
    @staticmethod
    def get_date_range_from_df(df: pd.DataFrame) -> Tuple[Optional[date], Optional[date]]:
        """Ermittelt Datumsbereich aus DataFrame."""
        try:
            ts = pd.to_datetime(df['timestamp'], errors='coerce').dropna()
            return (ts.min().date(), ts.max().date()) if not ts.empty else (None, None)
        except:
            return (datetime(2010, 1, 1).date(), datetime.now().date())