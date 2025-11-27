"""
URL configuration for contact app.
"""
from django.urls import path
from .views import ContactView, ContactSuccessView

app_name = 'contact'

urlpatterns = [
    path('', ContactView.as_view(), name='index'),
    path('success/', ContactSuccessView.as_view(), name='success'),
]










