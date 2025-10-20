import streamlit as st
from schemas.app_state_schemas.app_state import AppState, ParsedData, Views
from datetime import datetime, date, timedelta
import pandas as pd
from typing import Tuple, Optional

# Import der neuen DataParser Klasse
from services.data_parser import DataParser


class StateProvider: 
    def __init__(self, data_parser: Optional[DataParser] = None):
        self._state_key = "app_state"
        self.data_parser = data_parser
    
    def get_state(self) -> AppState:
        if self._state_key not in st.session_state:
            st.session_state[self._state_key] = AppState()
        return st.session_state[self._state_key]
    
    def save_state(self, state: AppState) -> None:
        st.session_state[self._state_key] = state
    
    def update_state(self, **kwargs) -> None:
        state = self.get_state()
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        self.save_state(state)
    
    def parse_data_to_state(self, file: str, delimiter: str = ";") -> AppState:
        state = self.get_state()
        
        # Verwende DataParser für alle Parsing-Operationen
        parser = DataParser(file, delimiter)
        
        # Parse alle Datentypen mit dem DataParser
        vitals = parser.parse_vitals_data()
        respiratory = parser.parse_respiratory_data()
        lab = parser.parse_lab_data()
        ecmo = parser.parse_ecmo_data()
        impella = parser.parse_impella_data()
        crrt = parser.parse_crrt_data()
        medication = parser.parse_medication_data()
        time_range = parser.get_date_range_from_df(vitals)
        fluidbalance = parser.parse_fluidbalance_data()
        
        # Aktualisiere State mit geparsten Daten
        state.parsed_data = ParsedData(
            crrt=crrt,
            ecmo=ecmo,
            impella=impella,
            lab=lab,
            medication=medication,
            respiratory=respiratory,
            vitals=vitals,
            fluidbalance=None  # not yet implemented
        )
        
        state.time_range = time_range
        state.selected_time_range = time_range
        state.last_updated = datetime.now()
        
        self.save_state(state)
        return state
    
    def reset_state(self) -> None:
        """Setzt den State auf einen neuen, leeren AppState zurück."""
        st.session_state[self._state_key] = AppState()
    
    def has_parsed_data(self) -> bool:
        state = self.get_state()
        return state.parsed_data is not None

    def get_device_time_ranges(self, device: str) -> Optional[pd.DataFrame]:
        state = self.get_state()
        if not state.parsed_data:
            return None
            
        device_data = getattr(state.parsed_data, device, None)
        if device_data is None or device_data.empty:
            return None
        
        try:
            df = device_data
            categories = df['category'].dropna().unique().tolist()
            
            time_ranges = []
            for category in categories:
                try:
                    ts = df[df['category'] == category]['timestamp']
                    ts = pd.to_datetime(ts, errors='coerce').dropna()
                    if not ts.empty:
                        start = ts.min().date()
                        end = ts.max().date()
                        time_ranges.append({
                            'category': category,
                            'start': start,
                            'end': end
                        })
                except Exception:
                    continue
            
            if time_ranges:
                return pd.DataFrame(time_ranges)
            else:
                return None
                
        except Exception:
            return None

    def has_device_past_24h(self, device: str, date: datetime) -> bool:

        cutoff_time = date - timedelta(hours=24)
        state = self.get_state()

        device_df = getattr(state.parsed_data, device, None)
        if device_df is not None and not device_df.empty:
            ts = pd.to_datetime(device_df["timestamp"], errors="coerce").dropna()
            if not ts.empty and (ts >= cutoff_time).any():
                return True

        return False

    def has_mcs_records_past_24h(self, date: datetime) -> bool:
        state = self.get_state()
        if not state.parsed_data:
            return False
        
        for device in ("ecmo", "impella"):
            try:
                if self.has_device_past_24h(device, date):
                    return True
            except Exception:
                continue
                
        return False

    def get_time_range(self) -> Optional[Tuple]:
        state = self.get_state()
        return state.time_range

    def get_time_of_mcs(self, date: datetime) -> int:
        """
        Berechnet die Anzahl der Tage seit dem Start des MCS (ECMO oder Impella).
        Gibt die Tage seit dem frühesten Startdatum zurück.
        """
        state = self.get_state()
        if not state.parsed_data:
            return 0

        earliest_start = None
        
        for device in ("ecmo", "impella"):
            try:
                device_df = getattr(state.parsed_data, device, None)
                if device_df is not None and not device_df.empty:
                    ts = pd.to_datetime(device_df["timestamp"], errors="coerce").dropna()
                    if not ts.empty:
                        device_start = ts.min()
                        if earliest_start is None or device_start < earliest_start:
                            earliest_start = device_start
            except Exception:
                continue

        if earliest_start is None:
            return 0
            
        # Berechne Tage seit MCS-Start
        days_since_start = (date - earliest_start).days
        return max(0, days_since_start)  # Negative Werte vermeiden

    def get_selected_view(self) -> Optional[Views]:
        state = self.get_state()
        return state.selected_view

    def set_selected_time_range(self, start_date, end_date) -> None:
        state = self.get_state()
        state.selected_time_range = (start_date, end_date)
        self.save_state(state)


state_provider = StateProvider()