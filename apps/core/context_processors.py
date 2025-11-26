"""
Context processors for core app.
"""


def language_preference(request):
    """Add language preference to context."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return {'user_language': request.user.language_preference}
    return {'user_language': 'en'}

