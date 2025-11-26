"""
Script to compile Django translation files (.po to .mo) without requiring gettext tools.
Uses babel library to compile translations.
"""
import os
from pathlib import Path

try:
    from babel.messages.catalog import Catalog
    from babel.messages.pofile import read_po
    from babel.messages.mofile import write_mo
except ImportError:
    print("Installing babel library...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'babel'])
    from babel.messages.catalog import Catalog
    from babel.messages.pofile import read_po
    from babel.messages.mofile import write_mo

BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / 'locale'

def compile_translations():
    """Compile all .po files to .mo files."""
    if not LOCALE_DIR.exists():
        print(f"Locale directory not found: {LOCALE_DIR}")
        return
    
    compiled_count = 0
    for lang_dir in LOCALE_DIR.iterdir():
        if not lang_dir.is_dir():
            continue
        
        lc_messages_dir = lang_dir / 'LC_MESSAGES'
        if not lc_messages_dir.exists():
            continue
        
        po_file = lc_messages_dir / 'django.po'
        mo_file = lc_messages_dir / 'django.mo'
        
        if not po_file.exists():
            print(f"Warning: {po_file} not found, skipping...")
            continue
        
        try:
            # Read the .po file
            with open(po_file, 'rb') as f:
                catalog = read_po(f)
            
            # Write the .mo file
            with open(mo_file, 'wb') as f:
                write_mo(f, catalog)
            
            print(f"✓ Compiled {po_file} -> {mo_file}")
            compiled_count += 1
        except Exception as e:
            print(f"✗ Error compiling {po_file}: {e}")
    
    print(f"\nCompiled {compiled_count} translation file(s).")

if __name__ == '__main__':
    compile_translations()






