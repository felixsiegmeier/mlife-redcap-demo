import streamlit as st
from schemas.app_state_schemas.app_state import AppState, ParsedData
from datetime import datetime
import pandas as pd
from typing import Tuple

# import parsers and helper
from services.clean_csv import cleanCSV
from services.parse_respiratory_data import parse_respiratory_data
from services.parse_vitals_data import parse_vitals_data
from services.parse_lab_data import parse_lab_data
from services.parse_ecmo_data import parse_ecmo_data
from services.parse_impella_data import parse_impella_data
from services.parse_crrt_data import parse_crrt_data
from services.parse_medication_data import parse_medication_data
from services.parse_fluidbalance_data import parse_fluidbalance_data



def get_date_range_from_df(df: pd.DataFrame) -> Tuple:
    try:
        ts = pd.to_datetime(df['timestamp'], errors='coerce').dropna()
        if ts.empty:
            raise ValueError("Keine gültigen Timestamps gefunden")
        start = ts.min().date()
        end = ts.max().date()
    except Exception:
        start = datetime(2010, 1, 1).date()
        end = datetime(datetime.now().year, 12, 31).date()
    return (start, end)

def get_state() -> AppState:
    if "app_state" not in st.session_state:
        st.session_state.app_state = AppState()
    return st.session_state.app_state


def save_state(state: AppState):
    st.session_state.app_state = state
    

def parse_data_to_state(file: str, DELIMITER: str = ";"):
    state = get_state()

    clean_file = cleanCSV(file)

    vitals = parse_vitals_data(clean_file, DELIMITER)
    respiratory = parse_respiratory_data(clean_file, DELIMITER)
    lab = parse_lab_data(clean_file, DELIMITER)
    ecmo = parse_ecmo_data(clean_file, DELIMITER)
    impella = parse_impella_data(clean_file, DELIMITER)
    crrt = parse_crrt_data(clean_file, DELIMITER)
    medication = parse_medication_data(clean_file, DELIMITER)
    time_range = get_date_range_from_df(vitals)
    fluidbalance = parse_fluidbalance_data(clean_file, DELIMITER)

    state.parsed_data = ParsedData(
        crrt=crrt,
        ecmo=ecmo,
        impella=impella,
        lab=lab,
        medication=medication,
        respiratory=respiratory,
        vitals=vitals,
        fluidbalance=None #not yet implemented,
    )

    state.time_range = time_range
    state.selected_time_range = time_range

    state.last_updated = datetime.now()
    save_state(state)
    return state