"""
URL configuration for accounts app.
"""
from django.urls import path
from .views import profile

app_name = 'accounts'

urlpatterns = [
    # Keep profile view as it's custom
    # Note: login, logout, signup are handled by allauth URLs
    # Email confirmation view is overridden in config/urls.py before allauth URLs
    path('profile/', profile, name='profile'),
]

