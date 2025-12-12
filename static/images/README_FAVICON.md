# Favicon Setup Instructions

## Logo File Placement

Place your ASCAI Lazio logo files in this directory (`static/images/`) with the following names:

1. **favicon.ico** - Main favicon file (16x16, 32x32, 48x48 sizes recommended)
2. **favicon-16x16.png** - 16x16 PNG version
3. **favicon-32x32.png** - 32x32 PNG version
4. **apple-touch-icon.png** - 180x180 PNG for iOS devices
5. **android-chrome-192x192.png** - 192x192 PNG for Android
6. **android-chrome-512x512.png** - 512x512 PNG for Android

## Recommended Sizes

- favicon.ico: Multi-size (16x16, 32x32, 48x48)
- PNG files: Use the exact sizes mentioned above

## Quick Setup (Using Your Logo)

If you have the ASCAI Lazio logo image:

1. Convert it to the required sizes using an online tool like:
   - https://realfavicongenerator.net/
   - https://favicon.io/

2. Save all generated files to `static/images/`

3. Run `python manage.py collectstatic` to copy files to `staticfiles/`

4. The favicon will appear in browser tabs automatically!

## Note

The favicon links are already configured in `templates/base.html`. Once you place the image files here, the favicon will work automatically.

