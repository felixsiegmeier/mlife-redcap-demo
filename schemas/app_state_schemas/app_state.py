# state_model.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import pandas as pd

from schemas.db_schemas.lab import LabModel

class Views(Enum):
    HOMEPAGE = "homepage"
    STARTPAGE = "startpage"
    VITALS = "vitals"
    LAB = "lab"
    LAB_FORM = "lab_form"

class ParsedData(BaseModel):
    # Allow arbitrary types such as pandas.DataFrame (pydantic v2)
    model_config = {"arbitrary_types_allowed": True}
    crrt: Optional[pd.DataFrame] = None
    ecmo: Optional[pd.DataFrame] = None
    impella: Optional[pd.DataFrame] = None
    lab: Optional[pd.DataFrame] = None
    medication: Optional[pd.DataFrame] = None
    respiratory: Optional[pd.DataFrame] = None
    vitals: Optional[pd.DataFrame] = None
    fluidbalance: Optional[pd.DataFrame] = None

class UiState(BaseModel):
    selected_categories : list[str] = []
    selected_parameters : list[str] = []
    show_median : bool = False

class AppState(BaseModel):
    # Allow arbitrary types in nested models (safe to include here as well)
    model_config = {"arbitrary_types_allowed": True}
    last_updated: Optional[datetime] = None
    selected_patient_id: Optional[str] = None
    parsed_data: Optional[ParsedData] = None
    selected_view: Views = Views.STARTPAGE
    time_range: Optional[tuple[datetime, datetime]] = None
    selected_time_range: Optional[tuple[datetime, datetime]] = time_range
    vitals_ui: UiState = UiState()
    lab_ui: UiState = UiState()
    lab_form: list[LabModel] | None = []
    