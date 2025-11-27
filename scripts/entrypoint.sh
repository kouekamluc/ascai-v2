#!/usr/bin/env bash

set -euo pipefail

# Default PORT to 8000 for local usage if Railway does not inject one.
: "${PORT:=8000}"

# Function to run migrations with error handling
run_migrations() {
    echo "Running database migrations..."
    
    # Check database connectivity first
    if ! python manage.py check --database default 2>/dev/null; then
        echo "⚠ Warning: Database connectivity check failed, but continuing..."
    fi
    
    # Try to run migrations with retry logic
    local max_retries=3
    local retry_count=0
    local migration_success=false
    
    while [ $retry_count -lt $max_retries ]; do
        local migration_output
        local exit_code=0
        
        # Capture both output and exit code (disable set -e for this command)
        set +e
        migration_output=$(python manage.py migrate --noinput 2>&1)
        exit_code=$?
        set -e
        
        if [ $exit_code -eq 0 ]; then
            migration_success=true
            echo "✓ Migrations completed successfully"
            break
        else
            retry_count=$((retry_count + 1))
            
            # Check if error is related to duplicate types (partial migration state)
            if echo "$migration_output" | grep -q "duplicate key value violates unique constraint\|pg_type_typname_nsp_index"; then
                echo "⚠ Warning: Migration conflict detected (possibly partial migration state)"
                echo "Checking migration status..."
                
                # Check if migrations are actually in sync
                local unapplied_migrations
                unapplied_migrations=$(python manage.py showmigrations --plan 2>/dev/null | grep -c "\[ \]" || echo "0")
                
                if [ "$unapplied_migrations" -gt 0 ]; then
                    echo "⚠ Some migrations appear unapplied, but continuing due to type conflict..."
                    echo "⚠ This may indicate a partial migration state. Manual intervention may be required."
                    migration_success=true  # Continue anyway
                    break
                else
                    echo "✓ All migrations appear to be applied"
                    migration_success=true
                    break
                fi
            fi
            
            if [ $retry_count -lt $max_retries ]; then
                echo "⚠ Migration attempt $retry_count failed, retrying in 2 seconds..."
                sleep 2
            else
                echo "⚠ Migration failed after $max_retries attempts"
                echo "⚠ Continuing with deployment, but database may be in inconsistent state"
            fi
        fi
    done
    
    if [ "$migration_success" = false ]; then
        echo "⚠ Warning: Migrations did not complete successfully"
        echo "⚠ Application will start, but database state may be inconsistent"
    fi
}

# Run migrations with error handling
run_migrations

# Ensure admin user exists and has correct permissions
echo "Ensuring admin user exists..."
python manage.py create_admin --update || echo "⚠ Warning: Could not create/update admin user, but continuing..."

# Compile translation files before collecting static files
# (This is a fallback in case they weren't compiled during build)
echo "Checking translation files..."
mo_files_exist=true
for lang_dir in locale/*/LC_MESSAGES/; do
    if [ ! -f "${lang_dir}django.mo" ]; then
        mo_files_exist=false
        break
    fi
done

if [ "$mo_files_exist" = false ]; then
    echo "Compiling translation files (not found from build)..."
    # Try Django's compilemessages first (requires gettext)
    if command -v msgfmt >/dev/null 2>&1; then
        if python manage.py compilemessages --noinput 2>&1; then
            echo "✓ Translations compiled using Django compilemessages"
        else
            echo "Falling back to Python translation compiler..."
            if python compile_translations.py 2>&1; then
                echo "✓ Translations compiled using Python script"
            else
                echo "✗ ERROR: Translation compilation failed!"
                echo "✗ Translations will not work correctly"
                exit 1
            fi
        fi
    else
        echo "Using Python translation compiler (gettext not available)..."
        if python compile_translations.py 2>&1; then
            echo "✓ Translations compiled using Python script"
        else
            echo "✗ ERROR: Translation compilation failed!"
            echo "✗ Translations will not work correctly"
            exit 1
        fi
    fi
else
    echo "✓ Translation files already compiled (found from build)"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting application server..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output


