import re

def cleanCSV(file: str) -> str:
    lines = file.splitlines()
    clean_lines = []
    headers = []
    skip = set()
    intervall_pattern = re.compile(r"Intervall:\s*\d{2}\s*min\.,?")
    skip.add(len(lines)-1)
    for i, line in enumerate(lines):
        if line.lstrip().__contains__("Ausdruck: Gesamte Akte"):
            headers.append(i)
        if line.lstrip().__contains__("Bei aktuell laufenden Statusmodulen"):
            skip.add(i)
        if line.lstrip().__contains__("Datum/Uhrzeit bezieht sich jeweils auf den Intervallstart."):
            skip.add(i-1)
            skip.add(i)
        if intervall_pattern.search(line.lstrip()):
            skip.add(i)

    for j, h in enumerate(headers):
        # Header-Zeile + die nächsten 7 Zeilen überspringen
        skip.update(range(h, min(h + 8, len(lines))))
        # Zusätzlich: die Footer-Zeile davor (außer beim allerersten Header)
        if j > 0 and h - 1 >= 0:
            skip.add(h - 1)

    for i, line in enumerate(lines):
        if i in skip:
            continue
        clean_lines.append(line)
    
    return "\n".join(clean_lines)