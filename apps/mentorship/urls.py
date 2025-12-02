"""
URL configuration for mentorship app.
"""
from django.urls import path
from .views import (
    MentorListView,
    MentorDetailView,
    MentorProfileCreateView,
    MentorProfileUpdateView,
    MentorshipRequestCreateView,
    MentorDashboardView,
    StudentDashboardView,
    RequestDetailView,
    RateMentorView,
    accept_request,
    reject_request,
    complete_request,
    update_availability,
    get_messages
)

app_name = 'mentorship'

urlpatterns = [
    path('', MentorListView.as_view(), name='index'),
    path('mentors/', MentorListView.as_view(), name='mentor_list'),
    path('mentors/<int:pk>/', MentorDetailView.as_view(), name='mentor_detail'),
    path('mentors/<int:mentor_id>/request/', MentorshipRequestCreateView.as_view(), name='request_create'),
    path('profile/create/', MentorProfileCreateView.as_view(), name='profile_create'),
    path('profile/update/', MentorProfileUpdateView.as_view(), name='profile_update'),
    path('dashboard/mentor/', MentorDashboardView.as_view(), name='mentor_dashboard'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('requests/<int:pk>/', RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:request_id>/accept/', accept_request, name='accept_request'),
    path('requests/<int:request_id>/reject/', reject_request, name='reject_request'),
    path('requests/<int:request_id>/complete/', complete_request, name='complete_request'),
    path('requests/<int:request_id>/rate/', RateMentorView.as_view(), name='rate_mentor'),
    path('requests/<int:request_id>/messages/', get_messages, name='get_messages'),
    path('availability/update/', update_availability, name='update_availability'),
]

