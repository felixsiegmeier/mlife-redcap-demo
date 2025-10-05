from services.headers import headers

def extract_all_patient_data_headers(data: str, DELIMITER: str = ";"):
    """Input ist der String-Block 'ALLE Patientendaten'.

    Liefert ein Set mit allen Überschriften, die als dritte Spalte in Zeilen
    mit zwei führenden leeren Feldern erscheinen. (Konvention aus den CSV-Exporten.)
    """
    lines = data.splitlines()
    headers_set = set()
    for line in lines:
        l = line.split(DELIMITER)
        if len(l) > 2 and l[0] == "" and l[1] == "" and l[2] and l[2] != "Datum":
            headers_set.add(l[2])
    return headers_set