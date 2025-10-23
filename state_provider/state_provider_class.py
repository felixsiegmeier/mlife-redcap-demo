import streamlit as st
from schemas.app_state_schemas.app_state import AppState, ParsedData, Views
from datetime import datetime, date, timedelta
import pandas as pd
from typing import Any, Callable, Dict, Optional, Tuple, Union
from schemas.db_schemas.vitals import VentilationType
import logging

# Import der neuen DataParser Klasse
from services.data_parser import DataParser
from schemas.parse_schemas.vitals import VitalsModel
from schemas.parse_schemas.lab import LabModel

logger = logging.getLogger(__name__)


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
        vitals = parser._parse_table_data("Vitaldaten", VitalsModel)
        respiratory = parser.parse_respiratory_data()
        lab = parser._parse_table_data("Labor", LabModel, skip_first=True, clean_lab=True)
        ecmo = parser.parse_data_from_all_patient_data('ECMO')
        impella = parser.parse_data_from_all_patient_data('IMPELLA')
        crrt = parser.parse_data_from_all_patient_data('HÄMOFILTER')
        medication = parser.parse_special_data("Medication")
        nirs = parser.parse_special_data("NIRS")
        time_range = parser.get_date_range_from_df(vitals)
        # Convert date tuple to datetime tuple
        if time_range and time_range[0] and time_range[1]:
            time_range_dt = (datetime.combine(time_range[0], datetime.min.time()), 
                           datetime.combine(time_range[1], datetime.max.time()))
        else:
            time_range_dt = None
        fluidbalance = parser.parse_special_data("Fluidbalance")
        all_patient_data = parser.parse_all_patient_data()
        
        # Aktualisiere State mit geparsten Daten
        state.parsed_data = ParsedData(
            crrt=crrt,
            ecmo=ecmo,
            impella=impella,
            lab=lab,
            medication=medication,
            respiratory=respiratory,
            vitals=vitals,
            fluidbalance=fluidbalance,
            nirs=nirs,
            all_patient_data=all_patient_data
        )
        
        state.time_range = time_range_dt
        state.selected_time_range = time_range_dt
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
        """Deprecated: Use query_data('devices', {'category': device}) and compute time ranges manually."""

        device_df = self.query_data("devices", {"category": device})
        if device_df.empty:
            return None

        try:
            time_ranges = []
            for category in device_df.get("category", pd.Series(dtype=object)).dropna().unique():
                cat_df = device_df[device_df["category"] == category]
                if cat_df.empty or "timestamp" not in cat_df.columns:
                    continue
                timestamps = pd.to_datetime(cat_df["timestamp"], errors="coerce").dropna()
                if timestamps.empty:
                    continue
                time_ranges.append(
                    {
                        "category": category,
                        "start": timestamps.min().date(),
                        "end": timestamps.max().date(),
                    }
                )
            return pd.DataFrame(time_ranges) if time_ranges else None
        except Exception:
            return None

    def query_data(self, data_source: str, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Generalisierte Methode zum Abfragen von geparsten Daten mit Filtern und Aggregation."""

        filters = filters or {}
        state = self.get_state()
        if not state.parsed_data:
            return pd.DataFrame()

        df: Optional[pd.DataFrame] = None

        if data_source == "devices":
            all_patient_data = getattr(state.parsed_data, "all_patient_data", {}) or {}
            device_frames: list[pd.DataFrame] = []
            for source_header, categories in all_patient_data.items():
                if not isinstance(categories, dict):
                    continue
                for category, category_df in categories.items():
                    if isinstance(category_df, pd.DataFrame) and not category_df.empty:
                        current = category_df.copy()
                        current["source_header"] = source_header
                        current["category"] = category
                        device_frames.append(current)
            df = pd.concat(device_frames, ignore_index=True) if device_frames else pd.DataFrame()
        elif hasattr(state.parsed_data, data_source):
            candidate = getattr(state.parsed_data, data_source)
            if isinstance(candidate, pd.DataFrame):
                df = candidate
            else:
                df = pd.DataFrame()
        else:
            logger.warning("Unknown data source requested: %s", data_source)
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        filtered_df = df.copy()

        if "timestamp" in filtered_df.columns:
            filtered_df["timestamp"] = pd.to_datetime(filtered_df["timestamp"], errors="coerce")

        def _apply_filter(frame: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
            if column not in frame.columns:
                return frame
            if isinstance(value, str):
                return frame[frame[column].astype(str).str.contains(value, na=False, case=False)]
            if isinstance(value, (list, tuple, set)):
                return frame[frame[column].isin(list(value))]
            return frame

        timestamp_filter = filters.get("timestamp")
        if timestamp_filter is not None and "timestamp" in filtered_df.columns:
            if isinstance(timestamp_filter, datetime):
                target_date = timestamp_filter.date()
                filtered_df = filtered_df[filtered_df["timestamp"].dt.date == target_date]
            elif (
                isinstance(timestamp_filter, (list, tuple))
                and len(timestamp_filter) == 2
                and all(isinstance(item, datetime) for item in timestamp_filter)
            ):
                start, end = timestamp_filter
                if start > end:
                    start, end = end, start
                filtered_df = filtered_df[
                    (filtered_df["timestamp"] >= start) & (filtered_df["timestamp"] <= end)
                ]

        for key in ("parameter", "category", "source_header", "time_range"):
            value = filters.get(key)
            if value is not None:
                filtered_df = _apply_filter(filtered_df, key, value)

        limit = filters.get("limit")
        if isinstance(limit, int) and limit >= 0:
            filtered_df = filtered_df.head(limit)

        selection = filters.get("selection")
        if selection and not filtered_df.empty and "value" in filtered_df.columns:
            group_cols = [col for col in ("parameter", "category") if col in filtered_df.columns]

            def _aggregate_numeric(series: pd.Series, agg: str) -> float:
                numeric = pd.to_numeric(series, errors="coerce").dropna()
                if numeric.empty:
                    return float("nan")
                if agg == "median":
                    return float(numeric.median())
                if agg == "mean":
                    return float(numeric.mean())
                raise ValueError(f"Unsupported aggregation '{agg}'")

            if selection in {"median", "mean"}:
                if group_cols:
                    aggregated = (
                        filtered_df.groupby(group_cols)["value"]
                        .apply(lambda s: _aggregate_numeric(s, selection))
                        .reset_index(name="value")
                    )
                else:
                    aggregated = pd.DataFrame(
                        {"value": [_aggregate_numeric(filtered_df["value"], selection)]}
                    )
                return aggregated.reset_index(drop=True)

            if selection in {"first", "last"}:
                if "timestamp" in filtered_df.columns:
                    filtered_df = filtered_df.sort_values("timestamp")
                if group_cols:
                    grouped = filtered_df.groupby(group_cols, as_index=False)
                    result = grouped.first() if selection == "first" else grouped.last()
                else:
                    result = filtered_df.iloc[[0]] if selection == "first" else filtered_df.iloc[[-1]]
                return result.reset_index(drop=True)

            logger.warning("Unknown selection '%s' requested for %s", selection, data_source)

        return filtered_df.reset_index(drop=True)

    def has_device_past_24h(self, device: str, date: datetime) -> bool:
        """Prüft, ob für das angegebene Device Daten in den letzten 24 Stunden vorliegen."""

        state = self.get_state()
        if not state.parsed_data:
            return False

        device_df = getattr(state.parsed_data, device, None)
        if not isinstance(device_df, pd.DataFrame) or device_df.empty:
            return False

        if "timestamp" not in device_df.columns:
            return False

        cutoff_time = date - timedelta(hours=24)
        timestamps = pd.to_datetime(device_df["timestamp"], errors="coerce").dropna()
        if timestamps.empty:
            return False

        return bool((timestamps >= cutoff_time).any())

    def has_mcs_records_past_24h(self, date: datetime) -> bool:
        """Prüft, ob ECMO- oder Impella-Daten in den letzten 24 Stunden vorhanden sind."""

        for device in ("ecmo", "impella"):
            if self.has_device_past_24h(device, date):
                return True
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

    def get_vitals_value(self, date: datetime, parameter: str, selection: str = "median") -> Optional[float]:
        """Deprecated: Use query_data('vitals', {'timestamp': date, 'parameter': parameter, 'selection': selection}) instead."""
        filtered = self.query_data('vitals', {'timestamp': date, 'parameter': parameter, 'selection': selection})
        if filtered.empty:
            return None
        # Assuming selection returns aggregated value
        if 'value' in filtered.columns and not filtered.empty:
            return float(filtered['value'].iloc[0])
        return None

    def get_vasoactive_agents_df(self, date: datetime, agent: str) -> pd.DataFrame:
        state = self.get_state()
        if not state.parsed_data:
            return pd.DataFrame()

        medication_df = getattr(state.parsed_data, "medication", None)
        if medication_df is None or medication_df.empty:
            return pd.DataFrame()

        filtered = medication_df[
            ((medication_df["start"].dt.date == date) | (medication_df["stop"].dt.date == date))
            & (medication_df["medication"].str.contains(agent, na=False))
        ]

        if filtered.empty:
            return pd.DataFrame()

        return filtered

    def get_respiratory_value(self, date: datetime, parameter: str, selection: str = "median") -> Optional[float]:
        """Deprecated: Use query_data('respiratory', {'timestamp': date, 'parameter': parameter, 'selection': selection}) instead."""
        filtered = self.query_data('respiratory', {'timestamp': date, 'parameter': parameter, 'selection': selection})
        if filtered.empty:
            return None
        if 'value' in filtered.columns and not filtered.empty:
            return float(filtered['value'].iloc[0])
        return None

    def get_respiration_type(self, date: datetime) -> Optional[VentilationType]:
        pass
        # Hier weiter machen => evtl. anhand Vorhandensein Tubus, Beatmungseinstellungen (vorhandensein), HFNC-Vorhandensein

state_provider = StateProvider()