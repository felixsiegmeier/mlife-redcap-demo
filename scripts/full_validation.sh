#!/bin/zsh
"""
Vollständiges Validierungsskript für das gesamte Refactoring.
Führt alle Validierungen sequentiell aus.
"""

set -e  # Beende bei Fehler

echo "Starting full validation..."

# Parsing-Validierung
echo "Step 1: Parsing validation"
python scripts/validate_parsing.py

# Code-Validierung
echo "Step 2: Code validation"
python scripts/validate_code.py

# State und Views Validierung
echo "Step 3: State and views validation"
python scripts/validate_state_views.py

echo "🎉 All validations passed successfully!"