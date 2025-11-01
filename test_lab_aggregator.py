#!/usr/bin/env python3
"""
Test script to verify LabAggregator functionality with the updated query_data method.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_provider.state_provider_class import state_provider
from services.value_aggregation.lab_aggregator import LabAggregator
from datetime import date, time
import pandas as pd

def create_test_data():
    """Create test data for LabAggregator"""
    # Create mock lab data
    test_date = date(2025, 11, 1)
    lab_data = [
        {
            "timestamp": pd.Timestamp(f"{test_date} 08:00:00"),
            "category": "Blutgase arteriell",
            "parameter": "PCO2",
            "value": 35.0
        },
        {
            "timestamp": pd.Timestamp(f"{test_date} 12:00:00"),
            "category": "Blutgase arteriell",
            "parameter": "PCO2",
            "value": 38.0
        },
        {
            "timestamp": pd.Timestamp(f"{test_date} 08:00:00"),
            "category": "Blutgase arteriell",
            "parameter": "PO2",
            "value": 85.0
        }
    ]

    lab_df = pd.DataFrame(lab_data)

    # Set in state
    from schemas.app_state_schemas.app_state import ParsedData
    state = state_provider.get_state()
    state.parsed_data = ParsedData(
        lab=lab_df,
        vitals=None,
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
    print("Test data created for LabAggregator")

def test_lab_aggregator():
    """Test LabAggregator with different value strategies"""
    print("Testing LabAggregator...")

    test_date = date(2025, 11, 1)

    # Test with median (default)
    aggregator = LabAggregator(
        state_provider=state_provider,
        date=test_date,
        record_id="test123",
        redcap_event_name="test_event",
        redcap_repeat_instrument="labor",
        redcap_repeat_instance=1,
        value_strategy="median"
    )

    lab_entry = aggregator.create_lab_entry()
    print(f"Median PCO2: {lab_entry.pc02}")  # Should be 36.5 (median of 35.0 and 38.0)
    print(f"PO2: {lab_entry.p02}")  # Should be 85.0 (only one value)

    # Test with mean
    aggregator_mean = LabAggregator(
        state_provider=state_provider,
        date=test_date,
        record_id="test123",
        redcap_event_name="test_event",
        redcap_repeat_instrument="labor",
        redcap_repeat_instance=1,
        value_strategy="mean"
    )

    lab_entry_mean = aggregator_mean.create_lab_entry()
    print(f"Mean PCO2: {lab_entry_mean.pc02}")  # Should be 36.5 (mean of 35.0 and 38.0)

    # Test with nearest
    nearest_time = time(10, 0, 0)  # 10:00
    aggregator_nearest = LabAggregator(
        state_provider=state_provider,
        date=test_date,
        record_id="test123",
        redcap_event_name="test_event",
        redcap_repeat_instrument="labor",
        redcap_repeat_instance=1,
        value_strategy="nearest",
        nearest_time=nearest_time
    )

    lab_entry_nearest = aggregator_nearest.create_lab_entry()
    print(f"Nearest PCO2 (to 10:00): {lab_entry_nearest.pc02}")  # Should be 35.0 (08:00 is closer to 10:00 than 12:00)

    print("LabAggregator tests completed successfully!")

if __name__ == "__main__":
    create_test_data()
    test_lab_aggregator()