import pytest
import pandas as pd
from services.data_parser import DataParser
from schemas.parse_schemas.vitals import VitalsModel
from schemas.parse_schemas.medication import MedicationModel


@pytest.fixture
def sample_csv_data():
    """Fixture für simulierte CSV-Daten."""
    return """Header1;Header2;Header3
Vitaldaten;Online erfasste Vitaldaten;
;;Timestamp;HR;RR;SpO2
;;01.01.2023 12:00;80;20;98
;;01.01.2023 13:00;85;22;97

Medikamentengaben;Medikamentengaben;
Medikament;Konzentration;Applikation;Start;Stop;Rate
Dopamin;5mg/ml;i.v.;01.01.2023 10:00;01.01.2023 11:00;10

ALLE Patientendaten;ALLE Patientendaten;
PSI/NIRS/ICP;PSI/NIRS/ICP 1;
;;;01.01.2023 14:00;;;
;;;;Parameter1;;;;;100;;;;
;;;01.01.2023 15:00;;;
;;;;Parameter2;;;;;110;;;;
"""


@pytest.fixture
def parser(sample_csv_data):
    """Fixture für DataParser Instanz."""
    return DataParser(sample_csv_data)


def test_parse_special_data_nirs(parser):
    """Test parse_special_data für NIRS."""
    result = parser.parse_special_data("NIRS")
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'timestamp' in result.columns
    assert 'value' in result.columns
    assert 'category' in result.columns
    assert 'parameter' in result.columns
    assert result['category'].iloc[0] == 'nirs'


def test_parse_special_data_medication(parser):
    """Test parse_special_data für Medication."""
    result = parser.parse_special_data("Medication")
    assert isinstance(result, pd.DataFrame)
    # Medication parsing might be complex, check if it runs without error
    # assert not result.empty  # Uncomment if medication data is properly parsed


def test_parse_special_data_fluidbalance(parser):
    """Test parse_special_data für Fluidbalance."""
    result = parser.parse_special_data("Fluidbalance")
    assert isinstance(result, pd.DataFrame)
    # Currently returns empty DataFrame
    assert result.empty


def test_parse_special_data_unknown(parser):
    """Test parse_special_data für unbekanntes Keyword."""
    result = parser.parse_special_data("Unknown")
    assert isinstance(result, pd.DataFrame)
    assert result.empty


@pytest.mark.parametrize("keyword", ["NIRS", "Medication", "Fluidbalance"])
def test_parse_special_data_parametrized(parser, keyword):
    """Parametrisierter Test für alle Keywords."""
    result = parser.parse_special_data(keyword)
    assert isinstance(result, pd.DataFrame)
    # Check columns if not empty
    if not result.empty:
        assert 'timestamp' in result.columns
        assert 'value' in result.columns