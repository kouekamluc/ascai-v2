"""
URL configuration for accounts app.
"""
from django.urls import path
from .views import RegisterView, LoginView, register_success, profile
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/success/', register_success, name='register_success'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
]

