"""
URL configuration for dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Home
    path('', views.DashboardHomeView.as_view(), name='home'),
    
    # Profile Management
    path('profile/', views.ProfileView.as_view(), name='profile_view'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='profile_password'),
    path('profile/documents/', views.DocumentUploadView.as_view(), name='profile_documents'),
    path('profile/documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('profile/notifications/', views.NotificationPreferencesView.as_view(), name='profile_notifications'),
    
    # Support Tickets
    path('support/tickets/', views.TicketListView.as_view(), name='tickets_list'),
    path('support/tickets/create/', views.TicketCreateView.as_view(), name='tickets_create'),
    path('support/tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('support/tickets/<int:pk>/reply/', views.TicketReplyView.as_view(), name='ticket_reply'),
    
    # Community Groups
    path('groups/', views.GroupListView.as_view(), name='groups_list'),
    path('groups/<slug:slug>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<slug:slug>/join/', views.group_join, name='group_join'),
    path('groups/<slug:slug>/discussions/create/', views.DiscussionCreateView.as_view(), name='discussion_create'),
    path('groups/discussions/<int:pk>/', views.DiscussionDetailView.as_view(), name='discussion_detail'),
    
    # Story Submissions
    path('stories/', views.StorySubmissionListView.as_view(), name='stories_list'),
    path('stories/submit/', views.StorySubmissionCreateView.as_view(), name='stories_submit'),
    path('stories/<int:pk>/', views.StorySubmissionDetailView.as_view(), name='story_detail'),
    
    # Events
    path('events/', views.EventListView.as_view(), name='events_list'),
    path('events/<int:pk>/register/', views.event_register, name='event_register'),
    path('events/ticket/<int:pk>/', views.EventTicketView.as_view(), name='event_ticket'),
    path('events/history/', views.EventAttendanceHistoryView.as_view(), name='events_history'),
    
    # Downloads
    path('downloads/', views.ReservedDownloadsView.as_view(), name='downloads_list'),
    path('downloads/<int:pk>/download/', views.document_download, name='document_download'),
    path('downloads/<int:pk>/save/', views.document_save, name='document_save'),
    path('downloads/saved/', views.SavedDocumentsView.as_view(), name='downloads_saved'),
    
    # New Student Assistance
    path('new-student/', views.NewStudentGuideView.as_view(), name='new_student_guide'),
    path('new-student/guide/<slug:slug>/', views.GuideDetailView.as_view(), name='guide_detail'),
    path('new-student/questions/', views.StudentQuestionListView.as_view(), name='student_questions'),
    path('new-student/questions/create/', views.StudentQuestionCreateView.as_view(), name='student_question_create'),
    path('new-student/orientation/', views.OrientationBookingCreateView.as_view(), name='orientation_booking'),
    
    # Mentorship
    path('mentorship/', views.MentorshipDashboardView.as_view(), name='mentorship_dashboard'),
    
    # Personalization
    path('saved-items/', views.SavedItemsView.as_view(), name='saved_items'),
]
