#!/usr/bin/env bash

set -euo pipefail

echo "Running predeploy tasks..."

# Compile Django translation files
echo "Compiling translation files..."
if python manage.py compilemessages --noinput 2>/dev/null; then
    echo "✓ Translations compiled using Django compilemessages"
else
    echo "Falling back to Python translation compiler..."
    python compile_translations.py
fi

# Validate Django settings (optional but helpful)
echo "Validating Django configuration..."
python manage.py check --deploy || echo "⚠ Warning: Django check found issues"

echo "✓ Predeploy tasks completed"


