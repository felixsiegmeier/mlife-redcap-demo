#!/usr/bin/env python3
"""
Validierungsskript für Code-Qualität.
Führt Lint und Type-Checks aus.
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def run_mypy():
    """Führt mypy für Type-Checking aus."""
    print("Running mypy...")
    result = subprocess.run([sys.executable, "-m", "mypy", "services/data_parser.py", "state_provider/state_provider_class.py"], cwd=project_root)
    return result.returncode == 0

def run_pylint():
    """Führt pylint für Code-Qualität aus."""
    print("Running pylint...")
    result = subprocess.run([sys.executable, "-m", "pylint", "services/data_parser.py", "state_provider/state_provider_class.py"], cwd=project_root)
    return result.returncode == 0

def main():
    """Hauptfunktion."""
    print("Starting code validation...")
    
    success = True
    
    if not run_mypy():
        print("❌ MyPy failed")
        success = False
    else:
        print("✓ MyPy passed")
    
    if not run_pylint():
        print("❌ Pylint failed")
        success = False
    else:
        print("✓ Pylint passed")
    
    if success:
        print("🎉 Code validation passed!")
        sys.exit(0)
    else:
        print("❌ Code validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()