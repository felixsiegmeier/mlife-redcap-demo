import json
from pathlib import Path
from typing import Optional
from pathlib import Path
from services.clean_csv import cleanCSV
from services.split_blocks import splitBlocks
from services.parse_numerics import parseNumerics
from services.parse_documentation import parseDocumentation
import pandas as pd
from services.parse_from_all_patient_data import parse_from_all_patient_data
from views.vitals import render_vitals
from views.respirator import render_respirator
from app_core import run_app


if __name__ == "__main__":
    run_app()

