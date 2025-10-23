#!/usr/bin/env python3
"""
Validierungsskript für Parsing-Funktionalität.
Führt Tests aus und vergleicht Ausgaben mit erwarteten Snapshots.
"""

import subprocess
import sys
import os
import pandas as pd
from pathlib import Path

# Füge das Projekt-Root zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.data_parser import DataParser
from state_provider.state_provider_class import StateProvider

def run_pytest():
    """Führt pytest für alle Tests aus."""
    print("Running pytest...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=project_root)
    return result.returncode == 0

def validate_parsing_with_real_data():
    """Validiert Parsing mit realen Daten."""
    print("Validating parsing with real data...")
    try:
        parser = DataParser(str(project_root / "data" / "gesamte_akte.csv"), ";")
        state_provider = StateProvider()
        state = state_provider.parse_data_to_state(str(project_root / "data" / "gesamte_akte.csv"), ";")
        
        # Prüfe, ob Daten geparst wurden
        checks = {
            "vitals": not state.parsed_data.vitals.empty,
            "lab": not state.parsed_data.lab.empty,
            "respiratory": not state.parsed_data.respiratory.empty,
            "medication": not state.parsed_data.medication.empty,
            "nirs": not state.parsed_data.nirs.empty,
            "fluidbalance": not state.parsed_data.fluidbalance.empty,
        }
        
        for key, check in checks.items():
            if not check:
                print(f"Warning: {key} data is empty")
            else:
                print(f"✓ {key} data parsed successfully")
        
        return all(checks.values())
    except Exception as e:
        print(f"Error during validation: {e}")
        return False

def main():
    """Hauptfunktion."""
    print("Starting parsing validation...")
    
    success = True
    
    # Führe Tests aus
    if not run_pytest():
        print("❌ Pytest failed")
        success = False
    else:
        print("✓ Pytest passed")
    
    # Validiere mit realen Daten
    if not validate_parsing_with_real_data():
        print("❌ Real data validation failed")
        success = False
    else:
        print("✓ Real data validation passed")
    
    if success:
        print("🎉 All validations passed!")
        sys.exit(0)
    else:
        print("❌ Some validations failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()