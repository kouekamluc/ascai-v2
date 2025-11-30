"""
Custom storage backends for AWS S3.

We define dedicated storages for static and media assets so:
- static files always live under the ``static/`` prefix
- media uploads live under ``media/`` and do not overwrite existing files
"""
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Store collected static files under the `static/` prefix.
    """
    location = 'static'
    # Set ACL to None - let bucket policy handle public access
    # Setting to 'public-read' causes "Access Denied" when bucket blocks public access
    default_acl = None
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    """
    Store user uploads under the `media/` prefix and keep originals.
    This handles all file types: images, documents, videos, etc.
    Used for:
    - User avatars (profiles/)
    - User documents (user_documents/)
    - Gallery images/videos (gallery/)
    - News/Events images (news/, events/)
    - Story images (story_images/)
    - Group files (group_files/)
    - University logos (universities/logos/)
    - Scholarship documents (scholarships/)
    - CKEditor uploads (uploads/)
    - Admin uploads (all admin file uploads)
    """
    location = 'media'
    file_overwrite = False  # Don't overwrite existing files
    # Set ACL to None - let bucket policy handle public access
    # Setting to 'public-read' causes "Access Denied" when bucket blocks public access
    default_acl = None
    
    # Set content type based on file extension for better S3 handling
    def _get_write_parameters(self, name, content):
        params = super()._get_write_parameters(name, content)
        # Let boto3 auto-detect content type from file extension
        # This ensures proper MIME types for images, PDFs, etc.
        return params
