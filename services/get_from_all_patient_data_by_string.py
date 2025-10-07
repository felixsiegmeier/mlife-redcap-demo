from typing import Dict, List, Optional
import json

def get_from_all_patient_data_by_string(
    data: dict, query: str, DELIMITER: str = ";"
) -> Dict[str, Dict[str, List[str]]]:
    """Suche in `data["ALLE Patientendaten"]` nach Headern, die `query` enthalten.

    Die Funktion gibt die gefundenen Header als Schlüssel zurück. Jeder Header
    wird weiter in nummerierte Sub-Header partitioniert (z.B. "Header 1", "Header 2"),
    wenn derselbe Header mehrmals in unterschiedlichen Abschnitten vorkommt.

    Args:
        data: Dict mit dem Schlüssel "ALLE Patientendaten" (mehrzeiliger Text).
        query: Suchbegriff (case-insensitiv).
        DELIMITER: Feldtrenner in den Zeilen (Standard: ";").

    Returns:
        Dict[header -> Dict[sub_header_name -> List[line]]]
    """

    # Alle bekannten Header extrahieren (aus helpers)
    headers = extract_all_patient_data_headers(data.get("ALLE Patientendaten", {}), DELIMITER)

    # Nur die Header behalten, die den Suchbegriff enthalten (case-insensitiv)
    matching_headers = [header for header in headers if query.lower() in header.lower()]

    lines = data.get("ALLE Patientendaten", "").splitlines()
    # Ergebnis-Dict vorbereiten: jeder gefundene Header bekommt ein leeres Dict
    result: Dict[str, Dict[str, List[str]]] = {header: {} for header in matching_headers}

    current_header: Optional[str] = None
    current_sub_header_counter = 1
    current_sub_header: Optional[str] = None
    current_sub_header_line: Optional[str] = None
    buffer: List[str] = []

    for line in lines:
        parts = line.split(DELIMITER)
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

def extract_all_patient_data_headers(data_str: str, DELIMITER: str = ";"):
    """Input ist der String-Block 'ALLE Patientendaten'.

    Liefert ein Set mit allen Überschriften, die als dritte Spalte in Zeilen
    mit zwei führenden leeren Feldern erscheinen. (Konvention aus den CSV-Exporten.)
    """
    lines = data_str.splitlines()
    headers_set = set()
    for line in lines:
        l = line.split(DELIMITER)
        if len(l) > 2 and l[0] == "" and l[1] == "" and l[2] and l[2] != "Datum":
            headers_set.add(l[2])
    return headers_set