from pathlib import Path
from services.clean_csv import cleanCSV
from services.split_blocks import split_blocks
from services.parse_numerics import parseNumerics
from services.parse_documentation import parseDocumentation
from services.parse_vitals import parse_vitals
import pandas as pd
import json, logging
from services.parse_from_all_patient_data import parse_from_all_patient_data

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

def main():
    CSV = "data/gesamte_akte.csv"
    file = open(CSV, "r", encoding="utf-8").read()
    DELIMITER = ";"

    clean_file = cleanCSV(file)
    vitals = parse_vitals(clean_file, ";")

    # with open("test.json", "w") as f:
    #     f.write(json.dumps(vitals))

    # print(df_4.head)

if __name__ == "__main__":
    main()
