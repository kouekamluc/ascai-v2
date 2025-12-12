# ASCAI Lazio Logo Favicon Setup

## Quick Setup (Easiest Method)

### Step 1: Save Your Logo
1. Save your ASCAI Lazio logo image (the one with Colosseum, flags, etc.) as:
   - **File name:** `ascai-logo.png` (or `.jpg` if you only have JPG)
   - **Location:** `static/images/ascai-logo.png`

### Step 2: Generate Favicon Files (Choose One Method)

#### Option A: Using Python Script (Recommended)
```bash
# Install Pillow if not already installed
pip install Pillow

# Run the generation script
python scripts/generate_favicon.py
```

This will automatically create all required favicon sizes from your logo.

#### Option B: Using Online Tool
1. Go to: https://realfavicongenerator.net/
2. Upload your `ascai-logo.png` file
3. Configure settings (optional)
4. Download the generated package
5. Extract and copy all files to `static/images/`

### Step 3: Commit and Deploy
```bash
git add static/images/
git commit -m "Add ASCAI Lazio logo favicon files"
git push
```

After deployment, your logo will appear as the favicon in browser tabs!

## Generated Files

The favicon setup will create/use these files:

1. **favicon.ico** - Main favicon (multi-size: 16x16, 32x32, 48x48)
2. **favicon.svg** - SVG version (for modern browsers)
3. **favicon-16x16.png** - 16x16 PNG
4. **favicon-32x32.png** - 32x32 PNG
5. **apple-touch-icon.png** - 180x180 PNG (iOS devices)
6. **android-chrome-192x192.png** - 192x192 PNG (Android)
7. **android-chrome-512x512.png** - 512x512 PNG (Android)

## Notes

- The favicon links are already configured in `templates/base.html`
- Files will be automatically uploaded to S3 (if USE_S3=True) on deployment
- The detailed logo may be simplified at small sizes (16x16, 32x32) - this is normal

