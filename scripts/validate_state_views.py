#!/usr/bin/env python3
"""
Validierungsskript für State und Views.
Führt Tests für StateProvider und Views aus.
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def run_state_tests():
    """Führt Tests für StateProvider aus."""
    print("Running state provider tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_state_provider_query.py", "tests/test_regression_getters.py", "-v"], cwd=project_root)
    return result.returncode == 0

def run_views_tests():
    """Führt Tests für Views aus."""
    print("Running views tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_views_integration.py", "-v"], cwd=project_root)
    return result.returncode == 0

def main():
    """Hauptfunktion."""
    print("Starting state and views validation...")
    
    success = True
    
    if not run_state_tests():
        print("❌ State tests failed")
        success = False
    else:
        print("✓ State tests passed")
    
    if not run_views_tests():
        print("❌ Views tests failed")
        success = False
    else:
        print("✓ Views tests passed")
    
    if success:
        print("🎉 State and views validation passed!")
        sys.exit(0)
    else:
        print("❌ State and views validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()