from pathlib import Path
from services.clean_csv import cleanCSV
from services.split_blocks import split_blocks
# parsing utilities
from services.parsers.parse_respiratory_data import parse_respiratory_data
from services.parsers.parse_vitals_data import parse_vitals_data
from services.parsers.parse_lab_data import parse_lab_data
from services.parsers.parse_ecmo_data import parse_ecmo_data
from services.parsers.parse_impella_data import parse_impella_data
from services.parsers.parse_crrt_data import parse_crrt_data
from services.parsers.parse_medication_data import parse_medication_data
from services.parsers.parse_fluidbalance_data import parse_fluidbalance_data
import pandas as pd
import json, logging
from services.parsers.parse_from_all_patient_data import parse_from_all_patient_data

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

def main():
    CSV = "data/gesamte_akte.csv"
    file = open(CSV, "r", encoding="utf-8").read()
    DELIMITER = ";"

    clean_file = cleanCSV(file)
    vitals = parse_vitals_data(clean_file, ";")
    respiratory = parse_respiratory_data(clean_file, ";")
    lab = parse_lab_data(clean_file, ";")
    ecmo = parse_ecmo_data(clean_file, ";")
    impella = parse_impella_data(clean_file, ";")
    crrt = parse_crrt_data(clean_file, ";")
    medication = parse_medication_data(clean_file, ";")
    fluidbalance = parse_fluidbalance_data(clean_file, ";")

    # with open("testmed.json", "w") as f:
    #     medication.to_json(f)

if __name__ == "__main__":
    main()
