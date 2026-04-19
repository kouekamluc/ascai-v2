"""Template tags for internationalization utilities."""
from django import template
from django.conf import settings
from django.urls import translate_url
from django.utils.translation import activate, get_language

register = template.Library()


def _strip_language_prefix(path):
    """Normalize a URL path by removing any active language prefix."""
    if not path:
        return "/"

    normalized_path = path if path.startswith("/") else f"/{path}"
    for lang_code, _ in settings.LANGUAGES:
        prefixed_path = f"/{lang_code}/"
        if normalized_path == f"/{lang_code}":
            return "/"
        if normalized_path.startswith(prefixed_path):
            return normalized_path[len(f"/{lang_code}"):] or "/"
    return normalized_path


@register.simple_tag(takes_context=True)
def translate_current_url(context, language):
    """
    Translate the current URL to a different language.
    Handles prefix_default_language=False correctly.
    
    Usage: {% translate_current_url 'fr' %}
    """
    request = context.get('request')
    if not request:
        return ''

    current_path = request.path_info or "/"
    current_lang = get_language()
    if current_path.startswith(('/admin/', '/i18n/')):
        return request.get_full_path()

    path_without_lang = _strip_language_prefix(current_path)

    try:
        activate(language)
        translated_path = translate_url(path_without_lang, language) or path_without_lang
    finally:
        activate(current_lang)

    translated_path = _strip_language_prefix(translated_path)

    if language != settings.LANGUAGE_CODE:
        translated_path = (
            f"/{language}/"
            if translated_path == "/"
            else f"/{language}{translated_path}"
        )

    if request.GET:
        translated_path = f"{translated_path}?{request.GET.urlencode()}"

    return translated_path
