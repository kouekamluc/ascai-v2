# Media Files Not Showing in Production - Fix Guide

## Problem

Images uploaded in production are returning 404 errors. This happens because:

1. **Ephemeral Container Filesystem**: On Railway (and similar platforms), the container filesystem is ephemeral. When the container restarts, all files stored in `/app/media` are lost.

2. **Database References Persist**: The database still contains references to the uploaded files (e.g., `profiles/20251021_090813.jpg`), but the actual files no longer exist on disk.

3. **Media Files Not Served**: Even though the URL pattern is configured, the files don't exist to be served.

## Solution Options

### Option 1: Use AWS S3 (Recommended for Production)

This is the best solution for production deployments. Files are stored persistently in S3 and won't be lost on container restarts.

#### Steps:

1. **Create an S3 Bucket** (if you don't have one):
   - Go to AWS Console → S3
   - Create a new bucket
   - Configure bucket permissions (public read for media files)

2. **Create IAM User with S3 Access**:
   - Go to AWS Console → IAM
   - Create a new user with programmatic access
   - Attach policy: `AmazonS3FullAccess` (or create a custom policy with read/write access to your bucket)
   - Save the Access Key ID and Secret Access Key

3. **Set Environment Variables in Railway**:
   ```
   USE_S3=True
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   ```

4. **Redeploy**: After setting these variables, redeploy your application.

5. **Re-upload Images**: Since old files were lost, users will need to re-upload their profile images.

#### Benefits:
- ✅ Persistent storage (files never lost)
- ✅ Scalable (handles high traffic)
- ✅ CDN-ready (can add CloudFront later)
- ✅ Cost-effective for small to medium traffic

### Option 2: Use Railway Persistent Volume (Alternative)

Railway supports persistent volumes that survive container restarts.

1. **Add a Volume in Railway**:
   - Go to your Railway project
   - Add a new volume
   - Mount it to `/app/media` in your service

2. **Update MEDIA_ROOT** (if needed):
   - The default `MEDIA_ROOT = BASE_DIR / 'media'` should work if the volume is mounted correctly

3. **Redeploy**

#### Benefits:
- ✅ Persistent storage
- ✅ No external service needed
- ⚠️ Limited to Railway platform
- ⚠️ May have size limitations

### Option 3: Temporary Fix (Not Recommended)

If you can't set up S3 immediately, you can serve media files from the container, but **files will be lost on every restart**:

1. The code already handles this - media files are served when `USE_S3=False`
2. Users will need to re-upload images after each container restart
3. This is only suitable for development/testing

## Current Status

The code has been updated to:
- ✅ Ensure media files are served when S3 is disabled
- ✅ Create the media directory if it doesn't exist
- ✅ Handle both DEBUG and production modes correctly

## Verification

After implementing S3 (Option 1):

1. **Check Environment Variables**: Verify all S3 variables are set in Railway
2. **Upload a Test Image**: Upload a new profile image
3. **Check S3 Bucket**: Verify the file appears in your S3 bucket under the `media/` prefix
4. **Verify URL**: The image URL should be `https://your-bucket.s3.region.amazonaws.com/media/profiles/filename.jpg`
5. **Check Logs**: No more 404 errors for media files

## Migration Notes

- **Existing Files**: Files that were uploaded before enabling S3 are lost and cannot be recovered
- **Database Cleanup**: You may want to clear old file references from the database:
  ```python
  # Run in Django shell
  from apps.accounts.models import User
  User.objects.filter(avatar__isnull=False).update(avatar=None)
  ```
- **User Communication**: Inform users they'll need to re-upload their profile images

## Additional Configuration

### S3 Bucket CORS (if needed for direct uploads)

If you plan to allow direct browser uploads to S3, configure CORS:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["https://your-domain.com"],
        "ExposeHeaders": []
    }
]
```

### S3 Bucket Policy (for public read access)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/media/*"
        }
    ]
}
```

## Support

If you continue to experience issues:

1. Check Railway logs for errors
2. Verify S3 credentials are correct
3. Test S3 access with AWS CLI
4. Check bucket permissions and policies
5. Verify environment variables are set correctly

