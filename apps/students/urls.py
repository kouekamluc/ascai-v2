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
    ResourcesView,
    ResourceDetailView,
    NewStudentGuideView,
    GuideSectionDetailView,
    GuideStepDetailView,
    save_guide_progress
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
    path('resources/<int:pk>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('new-student-guide/', NewStudentGuideView.as_view(), name='new_student_guide'),
    path('new-student-guide/<slug:slug>/', GuideSectionDetailView.as_view(), name='guide_section_detail'),
    path('new-student-guide/step/<int:pk>/', GuideStepDetailView.as_view(), name='guide_step_detail'),
    path('new-student-guide/progress/<int:step_id>/save/', save_guide_progress, name='save_guide_progress'),
]

