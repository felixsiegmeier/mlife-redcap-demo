import pandas as pd
from typing import Optional, Dict, Tuple
from datetime import datetime, date, time

from schemas.db_schemas.lab import LabModel, WithdrawalSite
from state_provider.state_provider_class import StateProvider, state_provider

class LabAggregator:
    """Aggregiert Laborwerte zu einem LabModel mittels StateProvider.query_data.

    Hinweise zur Wertestrategie (method):
    - "median", "mean", "first", "last" werden direkt als value_strategy an query_data übergeben.
    - "nearest-12" wählt pro Tag den Messwert mit der geringsten Abweichung zu 12:00 Uhr.
    Unbekannte Methoden fallen auf "median" zurück.
    """

    def __init__(self, state_provider: StateProvider, date: date, record_id: str, value_strategy: Optional[str] = None) -> None:
        self.state_provider = state_provider
        self.date = date
        self.record_id = record_id
        self.value_strategy = value_strategy or "median"

    # Mapping: LabModel-Feld -> (Kategorie, Parameter)
    _FIELD_MAP: Dict[str, Tuple[str, str]] = {
        # Blutgase arteriell
        "pco2": ("Blutgase arteriell", "PCO2"),
        "po2": ("Blutgase arteriell", "PO2"),
        "ph": ("Blutgase arteriell", "PH"),
        "hco3": ("Blutgase arteriell", "HCO3"),
        "be": ("Blutgase arteriell", "ABEc"),
        "sao2": ("Blutgase arteriell", "O2-SAETTIGUNG"),
        "kalium": ("Blutgase arteriell", "KALIUM"),
        "natrium": ("Blutgase arteriell", "NATRIUM"),
        "glucose": ("Blutgase arteriell", "GLUCOSE"),
        "lactate": ("Blutgase arteriell", "LACTAT"),
        # Blutgase venös
        "svo2": ("Blutgase venös", "O2-SAETTIGUNG"),
        # Hämatologie & Gerinnung
        "wbc": ("Blutbild", "WBC"),
        "hb": ("Blutbild", "HB"),
        "hct": ("Blutbild", "HCT"),
        "plt": ("Blutbild", "PLT"),
        "ptt": ("Gerinnung", "PTT"),
        "quick": ("Gerinnung", "TPZ"),
        "inr": ("Gerinnung", "INR"),
        # Organsystem-Labore / Enzyme etc.
        "ck": ("Enzyme", "CK"),
        "ckmb": ("Enzyme", "CK-MB"),
        "ggt": ("Enzyme", "GGT"),
        "ldh": ("Enzyme", "LDH"),
        "lipase": ("Enzyme", "LIPASE"),
        "free_hb": ("Blutbild", "FREIES HB"),
        "pct": ("Klinische Chemie", "PROCALCITONIN"),
        "total_bilirubin": ("Klinische Chemie", "BILI"),
        "creatinine": ("Klinische Chemie", "KREATININ"),
        "urea": ("Klinische Chemie", "HARNSTOFF"),
        "creatinine_clearance": ("Klinische Chemie", "GFRKREA"),
    }

    def _selection_for_method(self, method: Optional[str], nearest_time: Optional[time] = None):
        if not method:
            return "median"
        method = method.lower().strip()
        if method in {"median", "mean", "first", "last"}:
            return method
        if method in {"nearest-12", "nearest", "nearest_noon"}:
            anchor = nearest_time or (time(12, 0) if method != "nearest" else None)
            # Wenn "nearest" gewählt wurde, wird eine Zeit erwartet; ohne Zeit kein nearest-Selection
            if method == "nearest" and anchor is None:
                return "median"
            return {"nearest": anchor}
        # Fallback
        return "median"

    def _get_lab_value(self, category: str, parameter: str, value_strategy) -> Optional[float]:
        filters: Dict = {
            "timestamp": self.date,
            "category": category,
            "parameter": parameter,
        }
        if value_strategy:
            filters["value_strategy"] = value_strategy

        df = self.state_provider.query_data("lab", filters)
        if df is None or df.empty or "value" not in df.columns:
            return None

        # value in float wandeln
        try:
            val = pd.to_numeric(df["value"].iloc[0], errors="coerce")
        except Exception:
            return None
        return None if pd.isna(val) else float(val)

    def create_lab_entry(self, method: Optional[str] = None, nearest_time: Optional[time] = None) -> LabModel:
        method = method or self.value_strategy
        selection = self._selection_for_method(method, nearest_time)
        # Basismetadaten
        assess_t = selection.get("nearest") if isinstance(selection, dict) else None

        values: Dict[str, Optional[float]] = {}
        for field, (cat, param) in self._FIELD_MAP.items():
            values[field] = self._get_lab_value(cat, param, selection)

        # Nutzlast mit Aliases zusammenbauen und per model_validate validieren
        alias_map: Dict[str, str] = {
            "pco2": "pc02",
            "po2": "p02",
            "ph": "ph",
            "hco3": "hco3",
            "be": "be",
            "sao2": "sa02",
            "kalium": "k",
            "natrium": "na",
            "glucose": "gluc",
            "lactate": "lactate",
            "svo2": "sv02",
            "wbc": "wbc",
            "hb": "hb",
            "hct": "hct",
            "plt": "plt",
            "ptt": "ptt",
            "quick": "quick",
            "inr": "inr",
            "ck": "ck",
            "ckmb": "ckmb",
            "ggt": "ggt",
            "ldh": "ldh",
            "lipase": "lipase",
            "free_hb": "fhb",
            "pct": "pct",
            "total_bilirubin": "bili",
            "creatinine": "crea",
            "urea": "urea",
            "creatinine_clearance": "cc",
        }

        payload: Dict[str, object] = {
            "record_id": self.record_id,
            "assess_date_labor": self.date,
            "date_assess_labor": self.date,
            "time_assess_labor": assess_t,
            "art_site": WithdrawalSite.UNKNOWN,
        }

        for field, val in values.items():
            alias = alias_map.get(field)
            if alias is not None and val is not None:
                payload[alias] = val

        return LabModel.model_validate(payload)


def create_lab_entry(record_date: date, value_strategy: str = "median", nearest_time: Optional[time] = None) -> LabModel:
    """Kompatibilitäts-Wrapper für Views: erstellt ein LabModel für das gegebene Datum.

    - Ermittelt record_id aus dem globalen State (selected_patient_id), fällt andernfalls auf "unknown" zurück.
    - Verwendet StateProvider.query_data mit dem Schlüssel 'value_strategy'.
    - Unterstützt optional nearest_time, wenn value_strategy "nearest"-Varianten beinhaltet.
    """
    state = state_provider.get_state()
    record_id = getattr(state, "selected_patient_id", None) or "unknown"
    aggregator = LabAggregator(state_provider, record_date, record_id, value_strategy=value_strategy)
    return aggregator.create_lab_entry(method=value_strategy, nearest_time=nearest_time)