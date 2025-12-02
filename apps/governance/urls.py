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
    path('elections/', views.MemberElectionListView.as_view(), name='member_elections'),
    path('assemblies/<int:pk>/participate/', views.AssemblyParticipationView.as_view(), name='assembly_participate'),
    path('assemblies/<int:assembly_id>/register-attendance/', views.register_attendance, name='register_attendance'),
    path('votes/<int:vote_id>/cast/', views.cast_vote, name='cast_vote'),
    
    # Admin Membership
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('members/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    path('members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='member_edit'),
    path('members/<int:member_id>/verify/', views.verify_member, name='verify_member'),
    path('dues/<int:dues_id>/mark-paid/', views.mark_dues_paid, name='mark_dues_paid'),
    
    # Executive Board
    path('executive-board/', views.ExecutiveBoardListView.as_view(), name='executive_board_list'),
    path('executive-board/<int:pk>/', views.ExecutiveBoardDetailView.as_view(), name='executive_board_detail'),
    path('executive-board/create/', views.ExecutiveBoardCreateView.as_view(), name='executive_board_create'),
    path('executive-board/<int:pk>/edit/', views.ExecutiveBoardUpdateView.as_view(), name='executive_board_edit'),
    path('executive-board/<int:pk>/delete/', views.ExecutiveBoardDeleteView.as_view(), name='executive_board_delete'),
    path('executive-position/create/', views.ExecutivePositionCreateView.as_view(), name='executive_position_create'),
    path('executive-position/<int:pk>/edit/', views.ExecutivePositionUpdateView.as_view(), name='executive_position_edit'),
    path('executive-position/<int:pk>/delete/', views.ExecutivePositionDeleteView.as_view(), name='executive_position_delete'),
    path('board-meeting/create/', views.BoardMeetingCreateView.as_view(), name='board_meeting_create'),
    path('board-meeting/<int:pk>/edit/', views.BoardMeetingUpdateView.as_view(), name='board_meeting_edit'),
    path('board-meeting/<int:pk>/delete/', views.BoardMeetingDeleteView.as_view(), name='board_meeting_delete'),
    
    # General Assembly
    path('assemblies/', views.GeneralAssemblyListView.as_view(), name='assembly_list'),
    path('assemblies/<int:pk>/', views.GeneralAssemblyDetailView.as_view(), name='assembly_detail'),
    path('assemblies/create/', views.GeneralAssemblyCreateView.as_view(), name='assembly_create'),
    path('assemblies/<int:pk>/edit/', views.GeneralAssemblyUpdateView.as_view(), name='assembly_edit'),
    path('assemblies/<int:pk>/delete/', views.GeneralAssemblyDeleteView.as_view(), name='assembly_delete'),
    path('assemblies/<int:assembly_id>/update-status/', views.update_assembly_status, name='update_assembly_status'),
    path('agenda-items/create/', views.AgendaItemCreateView.as_view(), name='agenda_item_create'),
    path('agenda-items/<int:pk>/edit/', views.AgendaItemUpdateView.as_view(), name='agenda_item_edit'),
    path('agenda-items/<int:pk>/delete/', views.AgendaItemDeleteView.as_view(), name='agenda_item_delete'),
    path('assembly-attendance/create/', views.AssemblyAttendanceCreateView.as_view(), name='assembly_attendance_create'),
    path('assembly-attendance/<int:pk>/edit/', views.AssemblyAttendanceUpdateView.as_view(), name='assembly_attendance_edit'),
    path('assembly-attendance/<int:pk>/delete/', views.AssemblyAttendanceDeleteView.as_view(), name='assembly_attendance_delete'),
    path('assembly-votes/create/', views.AssemblyVoteCreateView.as_view(), name='assembly_vote_create'),
    path('assembly-votes/<int:pk>/edit/', views.AssemblyVoteUpdateView.as_view(), name='assembly_vote_edit'),
    path('assembly-votes/<int:pk>/delete/', views.AssemblyVoteDeleteView.as_view(), name='assembly_vote_delete'),
    
    # Financial
    path('finances/transactions/', views.FinancialTransactionListView.as_view(), name='financial_transactions'),
    path('finances/transactions/create/', views.FinancialTransactionCreateView.as_view(), name='financial_transaction_create'),
    path('finances/transactions/<int:pk>/edit/', views.FinancialTransactionUpdateView.as_view(), name='financial_transaction_edit'),
    path('finances/transactions/<int:pk>/delete/', views.FinancialTransactionDeleteView.as_view(), name='financial_transaction_delete'),
    path('finances/dues/', views.MembershipDuesListView.as_view(), name='membership_dues'),
    path('finances/dues/create/', views.MembershipDuesCreateView.as_view(), name='membership_dues_create'),
    path('finances/dues/<int:pk>/edit/', views.MembershipDuesUpdateView.as_view(), name='membership_dues_edit'),
    path('finances/dues/<int:pk>/delete/', views.MembershipDuesDeleteView.as_view(), name='membership_dues_delete'),
    path('finances/expenses/<int:pk>/approve/', views.ExpenseApprovalView.as_view(), name='expense_approval'),
    path('finances/expenses/<int:pk>/sign/', views.approve_expense, name='approve_expense'),
    path('finances/reports/', views.FinancialReportListView.as_view(), name='financial_report_list'),
    path('finances/reports/create/', views.FinancialReportCreateView.as_view(), name='financial_report_create'),
    path('finances/reports/<int:pk>/edit/', views.FinancialReportUpdateView.as_view(), name='financial_report_edit'),
    path('finances/reports/<int:pk>/delete/', views.FinancialReportDeleteView.as_view(), name='financial_report_delete'),
    
    # Electoral System
    path('elections/commissions/', views.ElectoralCommissionListView.as_view(), name='electoral_commission_list'),
    path('elections/commissions/<int:pk>/', views.ElectoralCommissionDetailView.as_view(), name='electoral_commission_detail'),
    path('elections/commissions/create/', views.ElectoralCommissionCreateView.as_view(), name='electoral_commission_create'),
    path('elections/commissions/<int:pk>/edit/', views.ElectoralCommissionUpdateView.as_view(), name='electoral_commission_edit'),
    path('elections/commissions/<int:pk>/delete/', views.ElectoralCommissionDeleteView.as_view(), name='electoral_commission_delete'),
    path('elections/commission-members/create/', views.CommissionMemberCreateView.as_view(), name='commission_member_create'),
    path('elections/commission-members/<int:pk>/edit/', views.CommissionMemberUpdateView.as_view(), name='commission_member_edit'),
    path('elections/commission-members/<int:pk>/delete/', views.CommissionMemberDeleteView.as_view(), name='commission_member_delete'),
    path('elections/', views.ElectionListView.as_view(), name='election_list'),
    path('elections/<int:pk>/', views.ElectionDetailView.as_view(), name='election_detail'),
    path('elections/create/', views.ElectionCreateView.as_view(), name='election_create'),
    path('elections/<int:pk>/edit/', views.ElectionUpdateView.as_view(), name='election_edit'),
    path('elections/<int:pk>/delete/', views.ElectionDeleteView.as_view(), name='election_delete'),
    path('elections/<int:election_id>/update-status/', views.update_election_status, name='update_election_status'),
    path('elections/<int:election_id>/vote/', views.ElectionVoteView.as_view(), name='election_vote'),
    path('elections/<int:election_id>/cast-vote/', views.cast_election_vote, name='cast_election_vote'),
    path('candidacies/', views.CandidacyListView.as_view(), name='candidacy_list'),
    path('candidacies/apply/', views.CandidacyCreateView.as_view(), name='candidacy_apply'),
    path('candidacies/<int:candidacy_id>/approve/', views.approve_candidacy, name='approve_candidacy'),
    
    # Board of Auditors
    path('auditors/boards/', views.BoardOfAuditorsListView.as_view(), name='board_of_auditors_list'),
    path('auditors/boards/<int:pk>/', views.BoardOfAuditorsDetailView.as_view(), name='board_of_auditors_detail'),
    path('auditors/boards/create/', views.BoardOfAuditorsCreateView.as_view(), name='board_of_auditors_create'),
    path('auditors/boards/<int:pk>/edit/', views.BoardOfAuditorsUpdateView.as_view(), name='board_of_auditors_edit'),
    path('auditors/boards/<int:pk>/delete/', views.BoardOfAuditorsDeleteView.as_view(), name='board_of_auditors_delete'),
    path('auditors/members/create/', views.AuditorMemberCreateView.as_view(), name='auditor_member_create'),
    path('auditors/members/<int:pk>/edit/', views.AuditorMemberUpdateView.as_view(), name='auditor_member_edit'),
    path('auditors/members/<int:pk>/delete/', views.AuditorMemberDeleteView.as_view(), name='auditor_member_delete'),
    path('auditors/reports/', views.AuditReportListView.as_view(), name='audit_report_list'),
    path('auditors/reports/create/', views.AuditReportCreateView.as_view(), name='audit_report_create'),
    path('auditors/reports/<int:pk>/edit/', views.AuditReportUpdateView.as_view(), name='audit_report_edit'),
    path('auditors/reports/<int:pk>/delete/', views.AuditReportDeleteView.as_view(), name='audit_report_delete'),
    
    # Disciplinary System
    path('disciplinary/cases/', views.DisciplinaryCaseListView.as_view(), name='disciplinary_case_list'),
    path('disciplinary/cases/<int:pk>/', views.DisciplinaryCaseDetailView.as_view(), name='disciplinary_case_detail'),
    path('disciplinary/cases/create/', views.DisciplinaryCaseCreateView.as_view(), name='disciplinary_case_create'),
    path('disciplinary/cases/<int:pk>/edit/', views.DisciplinaryCaseUpdateView.as_view(), name='disciplinary_case_edit'),
    path('disciplinary/cases/<int:pk>/delete/', views.DisciplinaryCaseDeleteView.as_view(), name='disciplinary_case_delete'),
    path('disciplinary/cases/<int:case_id>/update-status/', views.update_case_status, name='update_case_status'),
    path('disciplinary/sanctions/create/', views.DisciplinarySanctionCreateView.as_view(), name='disciplinary_sanction_create'),
    
    # Association Events
    path('events/', views.AssociationEventListView.as_view(), name='association_event_list'),
    path('events/<int:pk>/', views.AssociationEventDetailView.as_view(), name='association_event_detail'),
    path('events/create/', views.AssociationEventCreateView.as_view(), name='association_event_create'),
    path('events/<int:pk>/edit/', views.AssociationEventUpdateView.as_view(), name='association_event_edit'),
    path('events/<int:pk>/delete/', views.AssociationEventDeleteView.as_view(), name='association_event_delete'),
    
    # Communications
    path('communications/', views.CommunicationListView.as_view(), name='communication_list'),
    path('communications/<int:pk>/', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('communications/create/', views.CommunicationCreateView.as_view(), name='communication_create'),
    path('communications/<int:pk>/edit/', views.CommunicationUpdateView.as_view(), name='communication_edit'),
    path('communications/<int:pk>/delete/', views.CommunicationDeleteView.as_view(), name='communication_delete'),
    path('communications/<int:communication_id>/approve/', views.approve_communication, name='approve_communication'),
    path('communications/<int:communication_id>/publish/', views.publish_communication, name='publish_communication'),
    
    # Association Documents
    path('documents/', views.AssociationDocumentListView.as_view(), name='association_document_list'),
    path('documents/create/', views.AssociationDocumentCreateView.as_view(), name='association_document_create'),
    path('documents/<int:pk>/edit/', views.AssociationDocumentUpdateView.as_view(), name='association_document_edit'),
    path('documents/<int:pk>/delete/', views.AssociationDocumentDeleteView.as_view(), name='association_document_delete'),
    
    # Additional Functionality
    path('assemblies/propose-agenda-item/', views.propose_agenda_item, name='propose_agenda_item'),
    path('assemblies/request-extraordinary/', views.request_extraordinary_assembly, name='request_extraordinary_assembly'),
    path('votes/<int:vote_id>/publish/', views.publish_vote_results, name='publish_vote_results'),
    
    # Rules of Procedure Amendments (Article 47)
    path('amendments/', views.RulesOfProcedureAmendmentListView.as_view(), name='amendment_list'),
    path('amendments/<int:pk>/', views.RulesOfProcedureAmendmentDetailView.as_view(), name='amendment_detail'),
    path('amendments/propose/', views.RulesOfProcedureAmendmentCreateView.as_view(), name='amendment_propose'),
    path('amendments/<int:pk>/edit/', views.RulesOfProcedureAmendmentUpdateView.as_view(), name='amendment_edit'),
    path('amendments/<int:pk>/delete/', views.RulesOfProcedureAmendmentDeleteView.as_view(), name='amendment_delete'),
]

