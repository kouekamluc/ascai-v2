"""
Template tags for internationalization utilities.
"""
from django import template
from django.urls import translate_url
from django.utils.translation import activate, get_language
from django.conf import settings

register = template.Library()


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
    
    current_path = request.path
    current_lang = get_language()
    
    # Remove ALL language prefixes from current path
    path_without_lang = current_path
    for lang_code, _ in settings.LANGUAGES:
        if current_path.startswith(f'/{lang_code}/'):
            path_without_lang = current_path[len(f'/{lang_code}'):]
            break
        elif current_path == f'/{lang_code}':
            path_without_lang = '/'
            break
    
    # Ensure path starts with /
    if not path_without_lang.startswith('/'):
        path_without_lang = '/' + path_without_lang
    
    # Use translate_url to get the translated path
    # But we'll manually handle the prefix since prefix_default_language=False
    activate(language)
    translated_path = translate_url(path_without_lang, language)
    activate(current_lang)
    
    # Remove any language prefix that translate_url might have added
    # We'll add it back manually based on our settings
    for lang_code, _ in settings.LANGUAGES:
        if translated_path.startswith(f'/{lang_code}/'):
            translated_path = translated_path[len(f'/{lang_code}'):]
            break
        elif translated_path == f'/{lang_code}':
            translated_path = '/'
            break
    
    # Now add prefix only for non-default languages
    if language != settings.LANGUAGE_CODE:
        # Non-default language needs prefix
        if not translated_path.startswith('/'):
            translated_path = '/' + translated_path
        translated_path = f'/{language}{translated_path}'
    # For default language, no prefix needed (already removed above)
    
    # Add query string if present
    if request.GET:
        query_string = request.GET.urlencode()
        translated_path = f"{translated_path}?{query_string}"
    
    return translated_path

