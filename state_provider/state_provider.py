"""
Backward-kompatible Wrapper für die StateProvider-Klasse.
Diese Funktionen ermöglichen es bestehenden Code weiterhin zu funktionieren,
während sie die neue StateProvider-Klasse verwenden.
"""

import pandas as pd
from typing import Tuple
from schemas.app_state_schemas.app_state import AppState

# Import der neuen StateProvider-Klasse und DataParser
from .state_provider_class import state_provider
from services.data_parser import DataParser


def get_date_range_from_df(df: pd.DataFrame) -> Tuple:
    """
    Wrapper für DataParser.get_date_range_from_df
    
    Args:
        df: DataFrame mit timestamp-Spalte
        
    Returns:
        Tuple mit start- und end-Datum
    """
    return DataParser.get_date_range_from_df(df)


def get_state() -> AppState:
    """
    Wrapper für StateProvider.get_state
    
    Returns:
        AppState-Objekt
    """
    return state_provider.get_state()


def save_state(state: AppState) -> None:
    """
    Wrapper für StateProvider.save_state
    
    Args:
        state: Das zu speichernde AppState-Objekt
    """
    state_provider.save_state(state)


def parse_data_to_state(file: str, DELIMITER: str = ";") -> AppState:
    """
    Wrapper für StateProvider.parse_data_to_state
    
    Args:
        file: Pfad zur Datei
        DELIMITER: CSV-Delimiter (Standard: ";")
        
    Returns:
        Aktualisierter AppState
    """
    return state_provider.parse_data_to_state(file, DELIMITER)