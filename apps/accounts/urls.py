"""
URL configuration for accounts app.
"""
from django.urls import path
from django.urls import reverse_lazy
from .views import RegisterView, LoginView, register_success, profile
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/success/', register_success, name='register_success'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('core:home')), name='logout'),
    path('profile/', profile, name='profile'),
]

