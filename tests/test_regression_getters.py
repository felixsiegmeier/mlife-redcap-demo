import pytest
import pandas as pd
from datetime import datetime
from state_provider.state_provider_class import StateProvider


@pytest.fixture
def mock_parsed_data():
    """Fixture für Mock ParsedData."""
    vitals_data = pd.DataFrame({
        'timestamp': [datetime(2023, 1, 1, 12, 0), datetime(2023, 1, 1, 13, 0), datetime(2023, 1, 1, 14, 0)],
        'value': [80.0, 85.0, 90.0],
        'parameter': ['HR', 'HR', 'RR'],
        'category': ['vitals', 'vitals', 'vitals']
    })
    
    respiratory_data = pd.DataFrame({
        'timestamp': [datetime(2023, 1, 1, 12, 0), datetime(2023, 1, 1, 13, 0)],
        'value': [20.0, 22.0],
        'parameter': ['RR', 'RR'],
        'category': ['respiratory', 'respiratory']
    })
    
    return type('MockParsedData', (), {
        'vitals': vitals_data,
        'respiratory': respiratory_data,
        'medication': pd.DataFrame(),
        'lab': pd.DataFrame(),
        'ecmo': pd.DataFrame(),
        'impella': pd.DataFrame(),
        'crrt': pd.DataFrame(),
        'fluidbalance': pd.DataFrame(),
        'nirs': pd.DataFrame(),
        'all_patient_data': {}
    })()


@pytest.fixture
def provider_with_mock_data(mock_parsed_data):
    """Fixture für StateProvider mit Mock-Daten."""
    provider = StateProvider()
    state = provider.get_state()
    state.parsed_data = mock_parsed_data
    provider.save_state(state)
    return provider


def test_get_vitals_value_median(provider_with_mock_data):
    """Test get_vitals_value median gegen query_data."""
    date = datetime(2023, 1, 1)
    
    # Old method
    old_result = provider_with_mock_data.get_vitals_value(date, 'HR', 'median')
    
    # New method
    new_result_df = provider_with_mock_data.query_data('vitals', {'timestamp': date, 'parameter': 'HR', 'selection': 'median'})
    new_result = new_result_df['value'].iloc[0] if not new_result_df.empty else None
    
    assert old_result == new_result == 82.5


def test_get_vitals_value_mean(provider_with_mock_data):
    """Test get_vitals_value mean."""
    date = datetime(2023, 1, 1)
    
    old_result = provider_with_mock_data.get_vitals_value(date, 'HR', 'mean')
    new_result_df = provider_with_mock_data.query_data('vitals', {'timestamp': date, 'parameter': 'HR', 'selection': 'mean'})
    new_result = new_result_df['value'].iloc[0] if not new_result_df.empty else None
    
    expected = (80.0 + 85.0) / 2  # 82.5
    assert old_result == new_result == expected


def test_get_vitals_value_last(provider_with_mock_data):
    """Test get_vitals_value last."""
    date = datetime(2023, 1, 1)
    
    old_result = provider_with_mock_data.get_vitals_value(date, 'HR', 'last')
    new_result_df = provider_with_mock_data.query_data('vitals', {'timestamp': date, 'parameter': 'HR', 'selection': 'last'})
    new_result = new_result_df['value'].iloc[0] if not new_result_df.empty else None
    
    assert old_result == new_result == 85.0


def test_get_respiratory_value_median(provider_with_mock_data):
    """Test get_respiratory_value median gegen query_data."""
    date = datetime(2023, 1, 1)
    
    old_result = provider_with_mock_data.get_respiratory_value(date, 'RR', 'median')
    new_result_df = provider_with_mock_data.query_data('respiratory', {'timestamp': date, 'parameter': 'RR', 'selection': 'median'})
    new_result = new_result_df['value'].iloc[0] if not new_result_df.empty else None
    
    expected = (20.0 + 22.0) / 2  # 21.0
    assert old_result == new_result == expected


def test_get_vitals_value_no_data(provider_with_mock_data):
    """Test getter mit nicht vorhandenen Daten."""
    date = datetime(2023, 1, 2)  # Different date
    
    old_result = provider_with_mock_data.get_vitals_value(date, 'HR')
    new_result_df = provider_with_mock_data.query_data('vitals', {'timestamp': date, 'parameter': 'HR', 'selection': 'median'})
    new_result = None if new_result_df.empty else new_result_df['value'].iloc[0]
    
    assert old_result == new_result == None


def test_getters_backward_compatibility(provider_with_mock_data):
    """Test dass alte Getter noch funktionieren."""
    date = datetime(2023, 1, 1)
    
    # Should not raise exceptions
    hr_median = provider_with_mock_data.get_vitals_value(date, 'HR', 'median')
    rr_median = provider_with_mock_data.get_respiratory_value(date, 'RR', 'median')
    
    assert hr_median is not None
    assert rr_median is not None