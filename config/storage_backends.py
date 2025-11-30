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
    """
    location = 'media'
    file_overwrite = False
    # Set ACL to None - let bucket policy handle public access
    # Setting to 'public-read' causes "Access Denied" when bucket blocks public access
    default_acl = None
