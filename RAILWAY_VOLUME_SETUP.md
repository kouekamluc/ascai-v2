# Railway Persistent Volume Setup Guide

This guide explains how to set up Railway persistent volumes for media files in your Django application.

## Overview

When `USE_S3=False`, the application uses Railway's persistent volume feature to store media files (user uploads, images, etc.) that persist across container restarts. Static files (CSS, JS) are served via WhiteNoise and don't require a volume.

## Why Use Railway Volumes?

- **Persistence**: Media files survive container restarts and deployments
- **No External Dependencies**: No need for AWS S3 or other cloud storage
- **Simple Setup**: Easy to configure in Railway dashboard
- **Cost-Effective**: Included in Railway's pricing

## Setup Instructions

### Step 1: Add a Volume in Railway

1. Go to your Railway project dashboard
2. Select your service (the Django application)
3. Click on the **"Volumes"** tab (or look for "Add Volume" button)
4. Click **"Add Volume"** or **"Create Volume"**
5. Give it a name (e.g., `media-storage`)
6. Set the mount path to `/data` (or your preferred path)
7. Click **"Create"** or **"Add"**

### Step 2: Configure Environment Variables

In your Railway service, set the following environment variables:

```bash
USE_S3=False
RAILWAY_VOLUME_MOUNT_PATH=/data
```

**Note**: If you mounted the volume to a different path (not `/data`), update `RAILWAY_VOLUME_MOUNT_PATH` to match.

### Step 3: Verify Configuration

After deploying, check your application logs. You should see:

```
Using Railway volume for media files: /data/media
```

If you see a warning about the volume not being found, verify:
- The volume is mounted to the correct path
- The `RAILWAY_VOLUME_MOUNT_PATH` environment variable matches the mount path
- The service has been redeployed after adding the volume

## How It Works

### Static Files (No Volume Needed)

- Static files (CSS, JS, admin files) are collected to `staticfiles/` directory
- WhiteNoise middleware serves these files directly from the container
- Files are regenerated on each deployment via `collectstatic`
- No persistence needed (files are part of the codebase)

### Media Files (Volume Required)

- Media files (user uploads, images) are stored in `/data/media` (on the volume)
- The volume persists across container restarts
- Files are served via Django view (`serve_media_file`)
- Files persist even after redeployments

## Directory Structure

When a Railway volume is mounted at `/data`, the application creates:

```
/data/
└── media/
    ├── profiles/      # User profile images
    ├── uploads/      # General uploads
    ├── events/       # Event images
    └── ...           # Other media subdirectories
```

## Troubleshooting

### Media Files Not Persisting

**Problem**: Media files are lost after container restart.

**Solutions**:
1. Verify the volume is mounted in Railway dashboard
2. Check that `RAILWAY_VOLUME_MOUNT_PATH` matches the mount path
3. Check application logs for volume detection messages
4. Ensure the volume is actually mounted (check logs for "Railway volume detected")

### Volume Not Detected

**Problem**: Logs show "Railway volume not found" warning.

**Solutions**:
1. Verify the volume exists in Railway dashboard
2. Check the mount path matches `RAILWAY_VOLUME_MOUNT_PATH`
3. Redeploy the service after adding the volume
4. Check Railway documentation for volume mounting requirements

### Permission Issues

**Problem**: Cannot write to media directory.

**Solutions**:
1. The entrypoint script automatically creates directories with proper permissions
2. If issues persist, check Railway volume permissions
3. Verify the service has write access to the mounted volume

### Media Files Not Accessible via URL

**Problem**: Media files return 404 errors.

**Solutions**:
1. Verify `USE_S3=False` is set
2. Check that media files are being saved to the volume path
3. Verify the `serve_media_file` view is working (check logs)
4. Ensure `MEDIA_URL` is set to `/media/` (default)

## Migration from S3 to Railway Volume

If you're currently using S3 and want to switch to Railway volumes:

1. **Backup existing media files** from S3
2. **Add Railway volume** (follow Step 1 above)
3. **Set environment variables**:
   ```bash
   USE_S3=False
   RAILWAY_VOLUME_MOUNT_PATH=/data
   ```
4. **Download media files from S3** and upload to Railway volume (if needed)
5. **Redeploy** the application

## Best Practices

1. **Regular Backups**: Even with persistent volumes, regularly backup your media files
2. **Volume Size**: Monitor volume usage and upgrade if needed
3. **Cleanup**: Implement periodic cleanup of old/unused media files
4. **Monitoring**: Monitor disk usage on the volume

## Alternative: Using AWS S3

If you prefer to use AWS S3 instead of Railway volumes:

1. Set `USE_S3=True`
2. Configure AWS credentials (see `env.railway.example`)
3. Media files will be stored in S3 bucket
4. Static files can also be stored in S3 (optional)

See `env.railway.example` for S3 configuration details.

## Support

For Railway-specific volume issues, consult:
- [Railway Volumes Documentation](https://docs.railway.app/storage/volumes)
- Railway support team

For application-specific issues, check:
- Application logs for error messages
- `config/settings/production.py` for media configuration
- `scripts/entrypoint.sh` for volume setup logic



