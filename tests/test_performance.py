import pytest
import pandas as pd
from state_provider.state_provider_class import StateProvider
from services.data_parser import DataParser
import os


@pytest.fixture
def real_csv_path():
    """Fixture für reale CSV-Datei."""
    path = "data/gesamte_akte.csv"
    if os.path.exists(path):
        return path
    return "data/test_data_1.csv"


@pytest.fixture
def parser(real_csv_path):
    """Fixture für DataParser."""
    return DataParser(real_csv_path)


@pytest.fixture
def provider():
    """Fixture für StateProvider."""
    return StateProvider()


@pytest.mark.benchmark
def test_parse_nirs_logic_performance(benchmark, parser):
    """Performance-Test für parse_nirs_logic."""
    def run():
        return parser.parse_nirs_logic()
    
    result = benchmark(run)
    assert isinstance(result, type(pd.DataFrame()))  # Ensure it returns DataFrame


@pytest.mark.benchmark
def test_parse_medication_logic_performance(benchmark, parser):
    """Performance-Test für parse_medication_logic."""
    def run():
        return parser.parse_medication_logic()
    
    result = benchmark(run)
    assert isinstance(result, type(pd.DataFrame()))


@pytest.mark.benchmark
def test_query_data_vitals_performance(benchmark, provider, real_csv_path):
    """Performance-Test für query_data vitals."""
    # Setup data
    state = provider.parse_data_to_state(real_csv_path)
    
    def run():
        return provider.query_data('vitals', {'parameter': 'HR', 'value_strategy': 'median'})
    
    result = benchmark(run)
    assert isinstance(result, type(pd.DataFrame()))


@pytest.mark.benchmark
def test_parse_data_to_state_performance(benchmark, provider, real_csv_path):
    """Performance-Test für gesamtes Parsing."""
    def run():
        return provider.parse_data_to_state(real_csv_path)
    
    result = benchmark(run)
    assert result.parsed_data is not None


# Baseline values (update after initial run)
NIRS_PARSE_TIME_BASELINE = 2.0  # seconds
MEDICATION_PARSE_TIME_BASELINE = 0.1
QUERY_TIME_BASELINE = 0.05
FULL_PARSE_TIME_BASELINE = 1.0


def test_performance_regression_nirs(parser):
    """Regressionstest für NIRS Parsing Zeit."""
    import time
    start = time.time()
    result = parser.parse_nirs_logic()
    duration = time.time() - start
    assert duration < NIRS_PARSE_TIME_BASELINE * 2  # Allow 2x baseline


def test_performance_regression_medication(parser):
    """Regressionstest für Medication Parsing Zeit."""
    import time
    start = time.time()
    result = parser.parse_medication_logic()
    duration = time.time() - start
    assert duration < MEDICATION_PARSE_TIME_BASELINE * 2


def test_performance_regression_query(provider, real_csv_path):
    """Regressionstest für Query Zeit."""
    provider.parse_data_to_state(real_csv_path)
    import time
    start = time.time()
    result = provider.query_data('vitals', {'parameter': 'HR'})
    duration = time.time() - start
    assert duration < QUERY_TIME_BASELINE * 2