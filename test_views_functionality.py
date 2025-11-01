#!/usr/bin/env python3
"""
Test script to verify the updated views functionality without UI calls.
Tests the state_provider query_data method and basic view logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_provider.state_provider_class import state_provider
import pandas as pd

def test_state_provider_basic():
    """Test basic state_provider functionality"""
    print("Testing state_provider basic functionality...")

    # Check if state exists
    state = state_provider.get_state()
    print(f"State exists: {state is not None}")
    
    # If no parsed data, create mock data for testing
    if not state_provider.has_parsed_data():
        print("No parsed data found. Creating mock data for testing...")
        create_mock_data()
    
    print(f"Has parsed data: {state_provider.has_parsed_data()}")
    return True

def create_mock_data():
    """Create mock data for testing"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Create mock lab data
    dates = [datetime(2025, 11, 1) + timedelta(days=i) for i in range(5)]
    lab_data = []
    for date in dates:
        for category in ["Blood", "Urine"]:
            for param in ["Glucose", "Creatinine"]:
                for hour in [8, 12, 16, 20]:
                    timestamp = date.replace(hour=hour)
                    value = 100 + (hash(f"{category}{param}{timestamp}") % 50)  # Random-ish value
                    lab_data.append({
                        "timestamp": timestamp,
                        "category": category,
                        "parameter": param,
                        "value": value
                    })
    
    lab_df = pd.DataFrame(lab_data)
    
    # Create mock vitals data
    vitals_data = []
    for date in dates:
        for category in ["Vital Signs", "Respiratory"]:
            for param in ["HR", "RR", "Temp"]:
                for hour in [8, 12, 16, 20]:
                    timestamp = date.replace(hour=hour)
                    value = 70 + (hash(f"{category}{param}{timestamp}") % 30)
                    vitals_data.append({
                        "timestamp": timestamp,
                        "category": category,
                        "parameter": param,
                        "value": value
                    })
    
    vitals_df = pd.DataFrame(vitals_data)
    
    # Set mock data in state
    from schemas.app_state_schemas.app_state import ParsedData
    state = state_provider.get_state()
    state.parsed_data = ParsedData(
        lab=lab_df,
        vitals=vitals_df,
        crrt=None,
        ecmo=None,
        impella=None,
        medication=None,
        respiratory=None,
        fluidbalance=None,
        nirs=None,
        all_patient_data=None
    )
    state_provider.save_state(state)
    print("Mock data created successfully")

def test_query_data():
    """Test query_data method for lab and vitals"""
    print("\nTesting query_data method...")

    # Test lab data
    try:
        lab_data = state_provider.query_data("lab")
        print(f"Lab data shape: {lab_data.shape}")
        print(f"Lab data columns: {list(lab_data.columns)}")
        if not lab_data.empty:
            print(f"Lab categories: {lab_data['category'].unique().tolist()[:5]}")  # First 5
    except Exception as e:
        print(f"Error querying lab data: {e}")
        return False

    # Test vitals data
    try:
        vitals_data = state_provider.query_data("vitals")
        print(f"Vitals data shape: {vitals_data.shape}")
        print(f"Vitals data columns: {list(vitals_data.columns)}")
        if not vitals_data.empty:
            print(f"Vitals categories: {vitals_data['category'].unique().tolist()[:5]}")  # First 5
    except Exception as e:
        print(f"Error querying vitals data: {e}")
        return False

    return True

def test_view_logic():
    """Test the logic from views without UI components"""
    print("\nTesting view logic...")

    state = state_provider.get_state()

    # Simulate lab_ui state - use proper initialization
    try:
        if not hasattr(state, 'lab_ui') or state.lab_ui is None:
            from schemas.app_state_schemas.app_state import UiState
            state.lab_ui = UiState()
        state.lab_ui.selected_categories = []
        state.lab_ui.selected_parameters = []
        state.lab_ui.show_median = False
        state_provider.save_state(state)
    except Exception as e:
        print(f"Could not initialize lab_ui: {e}")
        return False

    # Test category picker logic
    try:
        lab_data = state_provider.query_data("lab")
        if not lab_data.empty:
            categories = lab_data["category"].unique().tolist()
            print(f"Available lab categories: {categories[:5]}")  # First 5

            # Simulate selecting first category
            if categories:
                state.lab_ui.selected_categories = [categories[0]]
                state_provider.save_state(state)

                # Test parameter picker logic
                filtered_data = state_provider.query_data("lab", {"category": state.lab_ui.selected_categories})
                if not filtered_data.empty:
                    parameters = filtered_data["parameter"].unique().tolist()
                    print(f"Parameters for category '{categories[0]}': {parameters[:5]}")  # First 5

                    # Simulate selecting first parameter
                    if parameters:
                        state.lab_ui.selected_parameters = [parameters[0]]
                        state_provider.save_state(state)

                        # Test get_filtered_lab logic
                        from typing import Any, Dict
                        filters: Dict[str, Any] = {
                            "category": state.lab_ui.selected_categories,
                            "parameter": state.lab_ui.selected_parameters
                        }
                        if hasattr(state, "selected_time_range") and state.selected_time_range:
                            start, end = state.selected_time_range
                            filters["timestamp"] = [start, end]

                        filtered_lab = state_provider.query_data("lab", filters)
                        print(f"Filtered lab data shape: {filtered_lab.shape}")

                        # Test with median
                        state.lab_ui.show_median = True
                        state_provider.save_state(state)
                        filters["value_strategy"] = "median"
                        filtered_lab_median = state_provider.query_data("lab", filters)
                        print(f"Filtered lab data with median shape: {filtered_lab_median.shape}")
                        if not filtered_lab_median.empty:
                            print(f"Columns: {list(filtered_lab_median.columns)}")
                            if 'date' in filtered_lab_median.columns:
                                print(f"Date column type: {type(filtered_lab_median['date'].iloc[0])}")
    except Exception as e:
        print(f"Error in lab view logic: {e}")
        return False

    # Similar test for vitals
    try:
        if not hasattr(state, 'vitals_ui') or state.vitals_ui is None:
            from schemas.app_state_schemas.app_state import UiState
            state.vitals_ui = UiState()
        state.vitals_ui.selected_categories = []
        state.vitals_ui.selected_parameters = []
        state.vitals_ui.show_median = False
        state_provider.save_state(state)
    except Exception as e:
        print(f"Could not initialize vitals_ui: {e}")
        return False

    try:
        vitals_data = state_provider.query_data("vitals")
        if not vitals_data.empty:
            categories = vitals_data["category"].unique().tolist()
            print(f"Available vitals categories: {categories[:5]}")  # First 5
    except Exception as e:
        print(f"Error in vitals view logic: {e}")
        return False

    return True

def main():
    print("Starting functionality test for updated views...")

    if not test_state_provider_basic():
        print("Basic state_provider test failed.")
        return

    if not test_query_data():
        print("query_data test failed.")
        return

    if not test_view_logic():
        print("View logic test failed.")
        return

    print("\nAll tests passed! The updated views should work correctly.")

if __name__ == "__main__":
    main()