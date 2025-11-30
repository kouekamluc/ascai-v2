"""
URL configuration for governance app.
"""
from django.urls import path
from . import views

app_name = 'governance'

urlpatterns = [
    # Dashboard
    path('', views.GovernanceDashboardView.as_view(), name='dashboard'),
    
    # User-facing Member Portal
    path('my-membership/', views.MemberPortalView.as_view(), name='member_portal'),
    path('register/', views.MemberSelfRegistrationView.as_view(), name='member_register'),
    path('directory/', views.MemberDirectoryView.as_view(), name='member_directory'),
    path('my-dues/', views.MyDuesView.as_view(), name='my_dues'),
    path('my-dues/<int:dues_id>/request-payment/', views.request_dues_payment, name='request_dues_payment'),
    path('assemblies/<int:pk>/participate/', views.AssemblyParticipationView.as_view(), name='assembly_participate'),
    path('assemblies/<int:assembly_id>/register-attendance/', views.register_attendance, name='register_attendance'),
    path('votes/<int:vote_id>/cast/', views.cast_vote, name='cast_vote'),
    
    # Admin Membership
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('members/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    path('members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='member_edit'),
    
    # Executive Board
    path('executive-board/', views.ExecutiveBoardListView.as_view(), name='executive_board_list'),
    path('executive-board/<int:pk>/', views.ExecutiveBoardDetailView.as_view(), name='executive_board_detail'),
    path('executive-board/create/', views.ExecutiveBoardCreateView.as_view(), name='executive_board_create'),
    path('executive-position/create/', views.ExecutivePositionCreateView.as_view(), name='executive_position_create'),
    path('board-meeting/create/', views.BoardMeetingCreateView.as_view(), name='board_meeting_create'),
    
    # General Assembly
    path('assemblies/', views.GeneralAssemblyListView.as_view(), name='assembly_list'),
    path('assemblies/<int:pk>/', views.GeneralAssemblyDetailView.as_view(), name='assembly_detail'),
    path('assemblies/create/', views.GeneralAssemblyCreateView.as_view(), name='assembly_create'),
    path('agenda-items/create/', views.AgendaItemCreateView.as_view(), name='agenda_item_create'),
    path('assembly-attendance/create/', views.AssemblyAttendanceCreateView.as_view(), name='assembly_attendance_create'),
    path('assembly-votes/create/', views.AssemblyVoteCreateView.as_view(), name='assembly_vote_create'),
    
    # Financial
    path('finances/transactions/', views.FinancialTransactionListView.as_view(), name='financial_transactions'),
    path('finances/transactions/create/', views.FinancialTransactionCreateView.as_view(), name='financial_transaction_create'),
    path('finances/dues/', views.MembershipDuesListView.as_view(), name='membership_dues'),
    path('finances/dues/create/', views.MembershipDuesCreateView.as_view(), name='membership_dues_create'),
    path('finances/expenses/<int:pk>/approve/', views.ExpenseApprovalView.as_view(), name='expense_approval'),
    path('finances/expenses/<int:pk>/sign/', views.approve_expense, name='approve_expense'),
]

