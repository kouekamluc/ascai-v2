"""
Script to compile Django translation files (.po to .mo) without requiring gettext tools.
Uses babel library to compile translations.
"""
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for stdout/stderr to handle Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from babel.messages.catalog import Catalog
    from babel.messages.pofile import read_po
    from babel.messages.mofile import write_mo
except ImportError:
    print("ERROR: babel library is required but not installed.")
    print("Please install it with: pip install babel")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / 'locale'

def compile_translations():
    """Compile all .po files to .mo files."""
    if not LOCALE_DIR.exists():
        print(f"ERROR: Locale directory not found: {LOCALE_DIR}")
        return False
    
    compiled_count = 0
    errors = []
    
    for lang_dir in sorted(LOCALE_DIR.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith('.'):
            continue
        
        lc_messages_dir = lang_dir / 'LC_MESSAGES'
        if not lc_messages_dir.exists():
            print(f"WARNING: LC_MESSAGES directory not found in {lang_dir}, skipping...")
            continue
        
        po_file = lc_messages_dir / 'django.po'
        mo_file = lc_messages_dir / 'django.mo'
        
        if not po_file.exists():
            print(f"WARNING: {po_file} not found, skipping...")
            continue
        
        try:
            # Read the .po file
            with open(po_file, 'rb') as f:
                catalog = read_po(f)
            
            # Write the .mo file
            with open(mo_file, 'wb') as f:
                write_mo(f, catalog)
            
            # Use ASCII-safe characters for cross-platform compatibility
            checkmark = "[OK]" if sys.platform == 'win32' else "✓"
            print(f"{checkmark} Compiled {po_file.name} -> {mo_file.name} ({lang_dir.name})")
            compiled_count += 1
        except Exception as e:
            xmark = "[ERROR]" if sys.platform == 'win32' else "✗"
            error_msg = f"{xmark} Error compiling {po_file}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    if errors:
        print(f"\nWARNING: {len(errors)} error(s) occurred during compilation")
        for error in errors:
            print(f"  - {error}")
    
    if compiled_count == 0:
        print("\nERROR: No translation files were compiled!")
        return False
    
    checkmark = "[OK]" if sys.platform == 'win32' else "✓"
    print(f"\n{checkmark} Successfully compiled {compiled_count} translation file(s).")
    return True

if __name__ == '__main__':
    success = compile_translations()
    sys.exit(0 if success else 1)






