"""
Custom middleware for ASCAI Lazio project.
"""
from django.conf import settings
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.middleware.security import SecurityMiddleware
from django.urls import translate_url
from django.utils import translation


class UserPreferredLocaleMiddleware:
    """
    Apply the authenticated user's saved language preference to each request.

    URL prefixes still take precedence, but saved member preferences should
    drive the experience whenever the path is not explicitly language-scoped.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.supported_languages = {code for code, _ in settings.LANGUAGES}

    def __call__(self, request):
        current_language = translation.get_language()
        path_language = translation.get_language_from_path(request.path_info)
        selected_language = self._get_selected_language(request)
        preferred_language = None

        if selected_language:
            preferred_language = selected_language
        elif path_language in self.supported_languages:
            preferred_language = path_language
        elif getattr(request, "user", None) and request.user.is_authenticated:
            candidate = getattr(request.user, "language_preference", None)
            if candidate in self.supported_languages:
                preferred_language = candidate

        if preferred_language and preferred_language != current_language:
            translation.activate(preferred_language)
            request.LANGUAGE_CODE = preferred_language
        elif current_language:
            request.LANGUAGE_CODE = current_language

        if (
            preferred_language
            and preferred_language != settings.LANGUAGE_CODE
            and not path_language
            and request.method in {"GET", "HEAD"}
        ):
            translated_url = translate_url(request.get_full_path(), preferred_language)
            if translated_url and translated_url != request.get_full_path():
                response = HttpResponseRedirect(translated_url)
                response = self._set_language_cookie(response, preferred_language)
                self._restore_language(current_language)
                return response

        response = self.get_response(request)

        if (
            selected_language
            and getattr(request, "user", None)
            and request.user.is_authenticated
            and request.user.language_preference != selected_language
        ):
            request.user.language_preference = selected_language
            request.user.save(update_fields=["language_preference"])

        if settings.LANGUAGE_COOKIE_NAME in response.cookies:
            self._restore_language(current_language)
            return response

        active_language = (
            selected_language
            or getattr(request, "LANGUAGE_CODE", None)
            or translation.get_language()
        )
        if active_language in self.supported_languages:
            response = self._set_language_cookie(response, active_language)

        self._restore_language(current_language)
        return response

    def _get_selected_language(self, request):
        """Return the explicitly requested language from the language switch form."""
        if request.method != "POST":
            return None

        if not request.path_info.rstrip("/").endswith("/i18n/setlang"):
            return None

        selected_language = request.POST.get("language")
        if selected_language in self.supported_languages:
            return selected_language
        return None

    def _restore_language(self, language_code):
        """Avoid leaking the active language between requests on the same worker."""
        if language_code:
            translation.activate(language_code)
        else:
            translation.deactivate()

    def _set_language_cookie(self, response, language_code):
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response


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
