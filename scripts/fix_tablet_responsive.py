"""
Script to update max-w-7xl to responsive classes for better tablet support.
Replaces max-w-7xl with: max-w-full md:max-w-[95%] lg:max-w-6xl xl:max-w-7xl
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'

# Pattern to match max-w-7xl in class attributes
pattern = r'max-w-7xl'
replacement = 'max-w-full md:max-w-[95%] lg:max-w-6xl xl:max-w-7xl'

# Files to update (key templates)
key_files = [
    'templates/diaspora/index.html',
    'templates/community/index.html',
    'templates/universities/university_list.html',
    'templates/scholarships/scholarship_list.html',
    'templates/gallery/album_list.html',
    'templates/contact/index.html',
    'templates/downloads/document_list.html',
    'templates/mentorship/mentor_list.html',
]

def update_file(file_path):
    """Update max-w-7xl to responsive classes in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if pattern in content:
            new_content = content.replace(pattern, replacement)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Updating templates for better tablet responsiveness...\n")
    
    updated_count = 0
    for file_path in key_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            if update_file(full_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Updated {updated_count} files")
    print("\n💡 Note: Other templates may still use max-w-7xl.")
    print("   The navbar, footer, and home page have been updated manually.")

