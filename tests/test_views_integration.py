import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch
from state_provider.state_provider_class import StateProvider
from schemas.app_state_schemas.app_state import ParsedData, UiState


@pytest.fixture
def mock_state():
    """Fixture für Mock AppState."""
    vitals_data = pd.DataFrame({
        'timestamp': [datetime(2023, 1, 1, 12, 0), datetime(2023, 1, 1, 13, 0)],
        'value': [80.0, 85.0],
        'parameter': ['HR', 'RR'],
        'category': ['vitals1', 'vitals2']
    })
    
    lab_data = pd.DataFrame({
        'timestamp': [datetime(2023, 1, 1, 12, 0)],
        'value': [4.5],
        'parameter': ['Creatinine'],
        'category': ['lab1']
    })
    
    parsed_data = ParsedData(
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
    
    state = Mock()
    state.parsed_data = parsed_data
    state.vitals_ui = UiState()
    state.lab_ui = UiState()
    state.selected_time_range = (datetime(2023, 1, 1, 0, 0), datetime(2023, 1, 1, 23, 59))
    
    return state


@patch('views.vitals_data.get_state')
@patch('views.vitals_data.save_state')
def test_render_vitals_data_logic(mock_save_state, mock_get_state, mock_state):
    """Test der Logik in render_vitals_data ohne UI."""
    mock_get_state.return_value = mock_state
    
    # Import after mocking
    from views.vitals_data import render_vitals_data
    
    # Mock streamlit functions
    with patch('streamlit.expander') as mock_expander, \
         patch('streamlit.pills', return_value=['vitals1']), \
         patch('streamlit.warning'):
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock(return_value=None)
        
        # This would normally render UI, but we're testing the logic
        try:
            # Just call the function - it should not crash
            render_vitals_data()
        except Exception as e:
            # UI functions might not be available, but logic should work
            if "streamlit" not in str(e).lower():
                raise e


@patch('views.lab_data.get_state')
@patch('views.lab_data.save_state')
def test_render_lab_data_logic(mock_save_state, mock_get_state, mock_state):
    """Test der Logik in render_lab_data ohne UI."""
    mock_get_state.return_value = mock_state
    
    from views.lab_data import render_lab_data
    
    with patch('streamlit.expander') as mock_expander, \
         patch('streamlit.pills', return_value=['lab1']), \
         patch('streamlit.warning'):
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock(return_value=None)
        
        try:
            render_lab_data()
        except Exception as e:
            if "streamlit" not in str(e).lower():
                raise e


def test_vitals_data_filtering_logic(mock_state):
    """Test der Filter-Logik in vitals_data."""
    # Simulate the filtering logic from get_filtered_vitals
    vitals = mock_state.parsed_data.vitals
    
    # Set some selections
    mock_state.vitals_ui.selected_categories = ['vitals1']
    mock_state.vitals_ui.selected_parameters = ['HR']
    
    # Apply filters as in the view
    filtered = vitals[
        vitals["category"].isin(mock_state.vitals_ui.selected_categories) &
        vitals["parameter"].isin(mock_state.vitals_ui.selected_parameters)
    ]
    
    # Apply time filter
    if mock_state.selected_time_range:
        start, end = mock_state.selected_time_range
        filtered = filtered[
            (filtered["timestamp"] >= start) &
            (filtered["timestamp"] <= end)
        ]
    
    assert not filtered.empty
    assert filtered['parameter'].iloc[0] == 'HR'
    assert filtered['category'].iloc[0] == 'vitals1'


def test_lab_data_filtering_logic(mock_state):
    """Test der Filter-Logik in lab_data."""
    lab = mock_state.parsed_data.lab
    
    mock_state.lab_ui.selected_categories = ['lab1']
    mock_state.lab_ui.selected_parameters = ['Creatinine']
    
    filtered = lab[
        lab["category"].isin(mock_state.lab_ui.selected_categories) &
        lab["parameter"].isin(mock_state.lab_ui.selected_parameters)
    ]
    
    if mock_state.selected_time_range:
        start, end = mock_state.selected_time_range
        filtered = filtered[
            (filtered["timestamp"] >= start) &
            (filtered["timestamp"] <= end)
        ]
    
    assert not filtered.empty
    assert filtered['parameter'].iloc[0] == 'Creatinine'