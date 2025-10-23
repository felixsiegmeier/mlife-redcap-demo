import pytest
import pandas as pd
from state_provider.state_provider_class import StateProvider
import os


@pytest.fixture
def real_csv_path():
    """Fixture für reale CSV-Datei."""
    # Verwende eine vorhandene Testdatei
    path = "data/gesamte_akte.csv"
    if os.path.exists(path):
        return path
    # Fallback zu kleiner Testdatei
    return "data/test_data_1.csv"


def test_parse_data_to_state_integration(real_csv_path):
    """Integrationstest für parse_data_to_state."""
    provider = StateProvider()
    
    # Parse data
    state = provider.parse_data_to_state(real_csv_path)
    
    assert state.parsed_data is not None
    
    # Check that special data is parsed
    if hasattr(state.parsed_data, 'nirs'):
        nirs_df = state.parsed_data.nirs
        assert isinstance(nirs_df, pd.DataFrame)
        if not nirs_df.empty:
            assert 'timestamp' in nirs_df.columns
            assert 'value' in nirs_df.columns
            assert nirs_df['value'].min() >= 0  # NIRS values should be positive
    
    if hasattr(state.parsed_data, 'medication'):
        med_df = state.parsed_data.medication
        assert isinstance(med_df, pd.DataFrame)
        # Check expected columns for medication
        if not med_df.empty:
            expected_cols = ['medication', 'start', 'stop', 'rate']
            for col in expected_cols:
                assert col in med_df.columns
    
    # Check other data sources
    assert isinstance(state.parsed_data.vitals, pd.DataFrame)
    assert isinstance(state.parsed_data.lab, pd.DataFrame)
    assert isinstance(state.parsed_data.respiratory, pd.DataFrame)


def test_parsed_data_not_empty(real_csv_path):
    """Test dass geparste Daten nicht leer sind."""
    provider = StateProvider()
    state = provider.parse_data_to_state(real_csv_path)
    
    # At least vitals should have data
    assert not state.parsed_data.vitals.empty
    
    # Check time range
    assert state.time_range is not None
    assert len(state.time_range) == 2