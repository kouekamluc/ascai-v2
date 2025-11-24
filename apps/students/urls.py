"""
URL configuration for students app.
"""
from django.urls import path
from .views import (
    StudentsIndexView,
    LivingGuideView,
    UniversitiesListView,
    EnrollmentProcessView,
    OrientationView
)

app_name = 'students'

urlpatterns = [
    path('', StudentsIndexView.as_view(), name='index'),
    path('living-guide/', LivingGuideView.as_view(), name='living_guide'),
    path('universities/', UniversitiesListView.as_view(), name='universities_list'),
    path('enrollment/', EnrollmentProcessView.as_view(), name='enrollment_process'),
    path('orientation/', OrientationView.as_view(), name='orientation'),
]

