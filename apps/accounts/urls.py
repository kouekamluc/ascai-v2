"""
URL configuration for accounts app.
"""
from django.urls import path
from .views import profile

app_name = 'accounts'

urlpatterns = [
    # Keep profile view as it's custom
    # Note: login, logout, signup are handled by allauth URLs
    path('profile/', profile, name='profile'),
]

