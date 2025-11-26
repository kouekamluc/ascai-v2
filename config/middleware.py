"""
Custom middleware for ASCAI Lazio project.
"""
from django.middleware.security import SecurityMiddleware
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.conf import settings


class CustomSecurityMiddleware(SecurityMiddleware):
    """
    Custom SecurityMiddleware that exempts healthcheck endpoint from SSL redirect.
    This allows Railway's internal healthcheck to work properly.
    """
    # Paths that should be exempt from SSL redirect
    SSL_EXEMPT_PATHS = ['/health/', '/health']
    
    def _is_healthcheck_path(self, path):
        """Check if the given path is a healthcheck path."""
        return path in self.SSL_EXEMPT_PATHS or path.rstrip('/') in self.SSL_EXEMPT_PATHS
    
    def process_response(self, request, response):
        # Check if this is an SSL redirect for a healthcheck path
        if (isinstance(response, HttpResponsePermanentRedirect) and 
            self._is_healthcheck_path(request.path) and
            not request.is_secure()):
            # Check if it's redirecting to HTTPS (SSL redirect)
            location = response.get('Location', '')
            if location.startswith('https://'):
                # This is an SSL redirect for healthcheck - allow HTTP
                # Return OK response instead of redirecting
                return HttpResponse("OK", status=200, content_type="text/plain")
        return super().process_response(request, response)

