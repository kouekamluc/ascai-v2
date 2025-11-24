"""
URL configuration for students app.
"""
from django.urls import path
from .views import (
    StudentsIndexView,
    LivingGuideView,
    UniversitiesListView,
    StudyProgramsView,
    ErasmusExchangeView,
    ScholarshipsListView,
    EnrollmentProcessView,
    OrientationView,
    ResourcesView
)

app_name = 'students'

urlpatterns = [
    path('', StudentsIndexView.as_view(), name='index'),
    path('living-guide/', LivingGuideView.as_view(), name='living_guide'),
    path('universities/', UniversitiesListView.as_view(), name='universities_list'),
    path('study-programs/', StudyProgramsView.as_view(), name='study_programs'),
    path('erasmus-exchange/', ErasmusExchangeView.as_view(), name='erasmus_exchange'),
    path('scholarships/', ScholarshipsListView.as_view(), name='scholarships_list'),
    path('enrollment/', EnrollmentProcessView.as_view(), name='enrollment_process'),
    path('orientation/', OrientationView.as_view(), name='orientation'),
    path('resources/', ResourcesView.as_view(), name='resources'),
]

