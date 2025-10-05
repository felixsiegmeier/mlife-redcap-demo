import os
from services.clean_csv import cleanCSV
from services.split_blocks import splitBlocks
from services.parse_numerics import parseNumerics
from services.parse_from_all_patient_data import parse_from_all_patient_data


def test_parsing_pipeline_smoke():
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "gesamte_akte.csv")
    sample_path = os.path.abspath(sample_path)
    assert os.path.exists(sample_path), f"Sample data not found: {sample_path}"

    with open(sample_path, "rb") as f:
        raw = f.read()

    # try utf-8 then latin-1
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("latin-1")

    cleaned = cleanCSV(content)
    assert isinstance(cleaned, str) and len(cleaned) > 0

    blocks = splitBlocks(cleaned, ";")
    assert isinstance(blocks, dict)

    df_vitals = parseNumerics(blocks.get("Vitaldaten", {}), ";")
    df_resp = parseNumerics(blocks.get("Respiratordaten", {}), ";")
    df_lab = parseNumerics(blocks.get("Labor", {}), ";")

    # At least one of the numeric dfs should be non-empty on the sample dataset
    assert (not df_vitals.empty) or (not df_resp.empty) or (not df_lab.empty)

    # parse some therapy data
    ecmo = parse_from_all_patient_data(blocks.get("ALLE Patientendaten", {}), "ecmo", ";")
    # ecmo could be empty, but function should return a dataframe
    assert ecmo is not None
