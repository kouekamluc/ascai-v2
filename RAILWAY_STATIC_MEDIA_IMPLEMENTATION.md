# Railway Static and Media Files Implementation Summary

## Overview

This document summarizes the implementation of Railway-based static and media file handling without AWS S3.

## Problem Statement

1. **Admin Styling Issue**: When `USE_S3=True`, Django admin was not styled because static files weren't being served correctly from S3.
2. **Media Files Persistence**: Media files need to persist across Railway container restarts.

## Solution Implemented

### Static Files (USE_S3=False)

- **WhiteNoise Middleware**: Serves static files from `STATIC_ROOT` (already configured)
- **collectstatic**: Runs during deployment to collect all static files
- **Fallback URL Pattern**: Ensures admin files load even if WhiteNoise misses a request
- **Status**: ✅ Already working correctly

### Media Files (Railway Persistent Volume)

- **Railway Volume**: Mounted at `/data` (configurable via `RAILWAY_VOLUME_MOUNT_PATH`)
- **Automatic Detection**: Application detects if volume is mounted and uses it
- **Fallback**: If no volume is mounted, uses default `MEDIA_ROOT` (with warning)
- **Directory Creation**: Entrypoint script creates media directories on volume

## Files Modified

### 1. `config/settings/production.py`

**Changes:**
- Added `import os` at the top
- Added Railway volume detection logic for media files
- Automatically uses volume if mounted, falls back to default with warning

**Key Code:**
```python
if not USE_S3:
    RAILWAY_VOLUME_MOUNT_PATH = config('RAILWAY_VOLUME_MOUNT_PATH', default='/data')
    volume_media_path = os.path.join(RAILWAY_VOLUME_MOUNT_PATH, 'media')
    if os.path.exists(RAILWAY_VOLUME_MOUNT_PATH) and os.path.isdir(RAILWAY_VOLUME_MOUNT_PATH):
        MEDIA_ROOT = volume_media_path
        logger.info(f"Using Railway volume for media files: {MEDIA_ROOT}")
    else:
        logger.warning("Railway volume not found, using default MEDIA_ROOT")
```

### 2. `scripts/entrypoint.sh`

**Changes:**
- Added media directory setup logic
- Detects Railway volume and creates media directories
- Creates common subdirectories (profiles, uploads, events)

**Key Code:**
```bash
# Check if Railway volume is mounted
RAILWAY_VOLUME_MOUNT_PATH="${RAILWAY_VOLUME_MOUNT_PATH:-/data}"
if [ -d "$RAILWAY_VOLUME_MOUNT_PATH" ]; then
    MEDIA_DIR="$RAILWAY_VOLUME_MOUNT_PATH/media"
    echo "Railway volume detected, using: $MEDIA_DIR"
else
    MEDIA_DIR="media"
    echo "No Railway volume detected, using default: $MEDIA_DIR"
fi
mkdir -p "$MEDIA_DIR"
```

### 3. `env.railway.example`

**Changes:**
- Updated to show Railway volume option (Option B)
- Added `RAILWAY_VOLUME_MOUNT_PATH` configuration
- Clarified the three storage options: S3, Railway Volume, Local (not recommended)

### 4. `RAILWAY_VOLUME_SETUP.md` (New File)

**Content:**
- Complete setup guide for Railway volumes
- Troubleshooting section
- Best practices
- Migration guide from S3 to Railway volumes

## Configuration

### Required Environment Variables

```bash
USE_S3=False
RAILWAY_VOLUME_MOUNT_PATH=/data  # Optional, defaults to /data
```

### Railway Dashboard Setup

1. Go to your Railway service
2. Add a new volume
3. Mount it to `/data` (or your preferred path)
4. Set `RAILWAY_VOLUME_MOUNT_PATH` to match the mount path

## How It Works

### Static Files Flow

1. During deployment: `collectstatic` collects all static files to `staticfiles/`
2. WhiteNoise middleware serves files from `STATIC_ROOT`
3. Fallback URL pattern handles any missed requests
4. Files are regenerated on each deployment (no persistence needed)

### Media Files Flow

1. During deployment: Entrypoint script checks for Railway volume
2. If volume exists: Creates `/data/media` directory structure
3. If no volume: Uses default `media/` directory (with warning)
4. Application saves uploads to `MEDIA_ROOT` (volume or default)
5. Files are served via `serve_media_file` view
6. Files persist across restarts (if using volume)

## Verification

### Check Application Logs

After deployment, check logs for:

**Success (Volume Mounted):**
```
Using Railway volume for media files: /data/media
```

**Warning (No Volume):**
```
Railway volume not found at /data. Media files will be stored at /app/media and will be lost on container restart.
```

### Test Static Files

1. Access admin interface: `https://your-app.up.railway.app/admin/`
2. Verify admin is styled correctly
3. Check browser console for any 404 errors on static files

### Test Media Files

1. Upload a file (e.g., profile image)
2. Verify file is accessible via URL
3. Restart container and verify file still exists (if using volume)

## Benefits

1. **No External Dependencies**: No need for AWS S3
2. **Simple Setup**: Easy Railway volume configuration
3. **Cost-Effective**: Included in Railway pricing
4. **Persistence**: Media files survive container restarts
5. **Automatic Detection**: Application automatically uses volume if available

## Migration Path

### From S3 to Railway Volume

1. Backup existing media files from S3
2. Add Railway volume in dashboard
3. Set `USE_S3=False` and `RAILWAY_VOLUME_MOUNT_PATH=/data`
4. Redeploy application
5. Upload media files to volume (if needed)

### From Local Storage to Railway Volume

1. Add Railway volume in dashboard
2. Set `RAILWAY_VOLUME_MOUNT_PATH=/data`
3. Redeploy application
4. Existing files in default `media/` will be lost (expected)
5. New uploads will go to volume

## Troubleshooting

See `RAILWAY_VOLUME_SETUP.md` for detailed troubleshooting guide.

## Next Steps

1. **Set up Railway Volume**: Follow instructions in `RAILWAY_VOLUME_SETUP.md`
2. **Configure Environment**: Set `USE_S3=False` and `RAILWAY_VOLUME_MOUNT_PATH=/data`
3. **Deploy**: Redeploy your application
4. **Verify**: Check logs and test file uploads
5. **Monitor**: Monitor volume usage and implement cleanup if needed

## Related Documentation

- `RAILWAY_VOLUME_SETUP.md` - Complete setup guide
- `env.railway.example` - Environment variable template
- `ADMIN_STYLING_FIX_REPORT.md` - Admin styling fix details

