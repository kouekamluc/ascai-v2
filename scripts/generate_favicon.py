"""
Script to generate favicon files from the ASCAI Lazio logo.
Requires Pillow: pip install Pillow
"""
import os
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_IMAGES_DIR = BASE_DIR / 'static' / 'images'

# Source logo file (user should place their logo here)
LOGO_FILE = STATIC_IMAGES_DIR / 'ascai-logo.png'  # or .jpg, .svg, etc.

# Favicon sizes to generate
FAVICON_SIZES = {
    'favicon-16x16.png': (16, 16),
    'favicon-32x32.png': (32, 32),
    'apple-touch-icon.png': (180, 180),
    'android-chrome-192x192.png': (192, 192),
    'android-chrome-512x512.png': (512, 512),
}


def generate_favicons():
    """Generate all favicon sizes from the source logo."""
    
    # Check if logo file exists
    if not LOGO_FILE.exists():
        print(f"❌ Logo file not found: {LOGO_FILE}")
        print(f"\n📋 Instructions:")
        print(f"1. Save your ASCAI Lazio logo image as 'ascai-logo.png' in: {STATIC_IMAGES_DIR}")
        print(f"2. Supported formats: PNG, JPG, SVG")
        print(f"3. Run this script again: python scripts/generate_favicon.py")
        return False
    
    try:
        # Open the source image
        print(f"📸 Opening logo: {LOGO_FILE}")
        img = Image.open(LOGO_FILE)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Generate each favicon size
        print(f"\n🎨 Generating favicon files...")
        for filename, size in FAVICON_SIZES.items():
            output_path = STATIC_IMAGES_DIR / filename
            resized = img.resize(size, Image.Resampling.LANCZOS)
            resized.save(output_path, 'PNG', optimize=True)
            print(f"  ✅ Created: {filename} ({size[0]}x{size[1]})")
        
        # Generate favicon.ico (multi-size ICO file)
        print(f"\n📦 Generating favicon.ico (multi-size)...")
        ico_sizes = [(16, 16), (32, 32), (48, 48)]
        ico_images = [img.resize(size, Image.Resampling.LANCZOS) for size in ico_sizes]
        ico_path = STATIC_IMAGES_DIR / 'favicon.ico'
        ico_images[0].save(
            ico_path,
            format='ICO',
            sizes=[(s[0], s[1]) for s in ico_sizes],
            append_images=ico_images[1:] if len(ico_images) > 1 else None
        )
        print(f"  ✅ Created: favicon.ico")
        
        # Generate SVG if source is SVG, otherwise create a simple SVG
        if LOGO_FILE.suffix.lower() == '.svg':
            # Copy SVG as favicon.svg
            import shutil
            svg_path = STATIC_IMAGES_DIR / 'favicon.svg'
            shutil.copy(LOGO_FILE, svg_path)
            print(f"  ✅ Created: favicon.svg")
        else:
            # Create a simple SVG placeholder
            svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img.width} {img.height}">
  <image href="{LOGO_FILE.name}" width="{img.width}" height="{img.height}"/>
</svg>'''
            svg_path = STATIC_IMAGES_DIR / 'favicon.svg'
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            print(f"  ✅ Created: favicon.svg")
        
        print(f"\n✅ All favicon files generated successfully!")
        print(f"\n📋 Next steps:")
        print(f"1. Review the generated files in: {STATIC_IMAGES_DIR}")
        print(f"2. Commit and push: git add static/images/* && git commit -m 'Add ASCAI logo favicons' && git push")
        print(f"3. After deployment, the favicon will appear in browser tabs!")
        
        return True
        
    except ImportError:
        print("❌ Pillow (PIL) not installed.")
        print("📦 Install it with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Error generating favicons: {e}")
        return False


if __name__ == '__main__':
    generate_favicons()

