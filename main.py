from pathlib import Path
from services.clean_csv import cleanCSV
from services.split_blocks import splitBlocks
from services.parse_numerics import parseNumerics
from services.parse_documentation import parseDocumentation
from services.pars_vitals import parsVitals
import pandas as pd
import json
from services.parse_from_all_patient_data import parse_from_all_patient_data


def main():
    CSV = "data/gesamte_akte.csv"
    file = open(CSV, "r", encoding="utf-8").read()
    DELIMITER = ";"

    clean_file = cleanCSV(file)
    # split_blocks = splitBlocks(clean_file, DELIMITER)
    # df_1 = parseNumerics(split_blocks["Vitaldaten"], DELIMITER)
    # df_2 = parseNumerics(split_blocks["Respiratordaten"], DELIMITER)
    # df_3 = parseNumerics(split_blocks["Labor"], DELIMITER)
    # # Medikationsdaten mit spezialisiertem Parser extrahieren
    # # df_4 = parseMedications(split_blocks, DELIMITER)
    # ecmo_df = parse_from_all_patient_data(split_blocks["ALLE Patientendaten"], "ecmo", DELIMITER)
    # impella_df = parse_from_all_patient_data(split_blocks["ALLE Patientendaten"], "impella", DELIMITER)
    # crrt_df = parse_from_all_patient_data(split_blocks["ALLE Patientendaten"], "hämofilter", DELIMITER)
    
    vitals = parsVitals(clean_file, ";")

    # with open("test.json", "w") as f:
    #     f.write(json.dumps(vitals))

    # print(df_4.head)

if __name__ == "__main__":
    main()
