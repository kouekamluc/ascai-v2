#!/usr/bin/env bash

set -euo pipefail

echo "Running predeploy tasks..."

# Check database connectivity
echo "Checking database connectivity..."
if python manage.py check --database default 2>/dev/null; then
    echo "✓ Database connection successful"
else
    echo "⚠ Warning: Database connectivity check failed"
    echo "⚠ Migrations may fail if database is not accessible"
fi

# Check migration state
echo "Checking migration state..."
if python manage.py showmigrations --plan >/dev/null 2>&1; then
    unapplied_count=$(python manage.py showmigrations --plan 2>/dev/null | grep -c "\[ \]" || echo "0")
    if [ "$unapplied_count" -gt 0 ]; then
        echo "⚠ Found $unapplied_count unapplied migration(s)"
    else
        echo "✓ All migrations are applied"
    fi
else
    echo "⚠ Could not check migration state"
fi

# Compile Django translation files
echo "Compiling translation files..."
# Try Django's compilemessages first (requires gettext)
if command -v msgfmt >/dev/null 2>&1; then
    if python manage.py compilemessages --noinput 2>&1; then
        echo "✓ Translations compiled using Django compilemessages"
    else
        echo "⚠ Django compilemessages failed, trying Python script..."
        if python compile_translations.py 2>&1; then
            echo "✓ Translations compiled using Python script"
        else
            echo "✗ ERROR: Translation compilation failed!"
            echo "✗ Translations will not work correctly"
            exit 1
        fi
    fi
else
    echo "gettext not available, using Python translation compiler..."
    if python compile_translations.py 2>&1; then
        echo "✓ Translations compiled using Python script"
    else
        echo "✗ ERROR: Translation compilation failed!"
        echo "✗ Translations will not work correctly"
        exit 1
    fi
fi

# Verify .mo files exist
echo "Verifying compiled translation files..."
mo_files_found=0
for lang_dir in locale/*/LC_MESSAGES/; do
    if [ -f "${lang_dir}django.mo" ]; then
        mo_files_found=$((mo_files_found + 1))
        echo "✓ Found: ${lang_dir}django.mo"
    fi
done

if [ $mo_files_found -eq 0 ]; then
    echo "✗ ERROR: No compiled translation files (.mo) found!"
    exit 1
fi

echo "✓ Verified $mo_files_found compiled translation file(s)"

# Validate Django settings (optional but helpful)
echo "Validating Django configuration..."
python manage.py check --deploy || echo "⚠ Warning: Django check found issues"

echo "✓ Predeploy tasks completed"


