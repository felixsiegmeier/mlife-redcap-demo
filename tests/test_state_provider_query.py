import pytest
import pandas as pd
from datetime import datetime
from state_provider.state_provider_class import StateProvider
from schemas.app_state_schemas.app_state import ParsedData


@pytest.fixture
def mock_parsed_data():
    """Fixture für Mock ParsedData."""
    # Create mock DataFrames
    vitals_data = pd.DataFrame({
        'timestamp': [datetime(2023, 1, 1, 12, 0), datetime(2023, 1, 1, 13, 0)],
        'value': [80.0, 85.0],
        'parameter': ['HR', 'HR'],
        'category': ['vitals', 'vitals']
    })
    
    lab_data = pd.DataFrame({
        'timestamp': [datetime(2023, 1, 1, 12, 0)],
        'value': [4.5],
        'parameter': ['Creatinine'],
        'category': ['lab']
    })
    
    return ParsedData(
        vitals=vitals_data,
        lab=lab_data,
        respiratory=pd.DataFrame(),
        medication=pd.DataFrame(),
        ecmo=pd.DataFrame(),
        impella=pd.DataFrame(),
        crrt=pd.DataFrame(),
        fluidbalance=pd.DataFrame(),
        nirs=pd.DataFrame(),
        all_patient_data={}
    )


@pytest.fixture
def provider_with_mock_data(mock_parsed_data):
    """Fixture für StateProvider mit Mock-Daten."""
    provider = StateProvider()
    state = provider.get_state()
    state.parsed_data = mock_parsed_data
    provider.save_state(state)
    return provider


def test_query_data_vitals_no_filters(provider_with_mock_data):
    """Test query_data für vitals ohne Filter."""
    result = provider_with_mock_data.query_data('vitals')
    assert not result.empty
    assert len(result) == 2
    assert 'HR' in result['parameter'].values


def test_query_data_vitals_with_timestamp_filter(provider_with_mock_data):
    """Test query_data für vitals mit Timestamp-Filter."""
    date_filter = datetime(2023, 1, 1)
    result = provider_with_mock_data.query_data('vitals', {'timestamp': date_filter})
    assert not result.empty
    assert len(result) == 2


def test_query_data_vitals_with_parameter_filter(provider_with_mock_data):
    """Test query_data für vitals mit Parameter-Filter."""
    result = provider_with_mock_data.query_data('vitals', {'parameter': 'HR'})
    assert not result.empty
    assert all(result['parameter'] == 'HR')


def test_query_data_vitals_with_selection_median(provider_with_mock_data):
    """Test query_data für vitals mit Median-Aggregation."""
    result = provider_with_mock_data.query_data('vitals', {'parameter': 'HR', 'selection': 'median'})
    assert not result.empty
    assert 'value' in result.columns
    # Should have aggregated to one row per parameter/category
    assert len(result) == 1
    assert result['value'].iloc[0] == 82.5  # median of 80, 85


def test_query_data_lab(provider_with_mock_data):
    """Test query_data für lab."""
    result = provider_with_mock_data.query_data('lab')
    assert not result.empty
    assert result['parameter'].iloc[0] == 'Creatinine'


def test_query_data_empty_source(provider_with_mock_data):
    """Test query_data für nicht vorhandene Datenquelle."""
    result = provider_with_mock_data.query_data('nonexistent')
    assert result.empty


def test_query_data_no_parsed_data():
    """Test query_data ohne geparste Daten."""
    provider = StateProvider()
    result = provider.query_data('vitals')
    assert result.empty