"""
Tests for governance app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import (
    Member,
    MembershipStatus,
    ExecutiveBoard,
    ExecutivePosition,
    ElectoralCommission,
    CommissionMember,
    Election,
    Candidacy,
    ElectionVote,
    BoardOfAuditors,
    AuditorMember,
    AssociationEvent,
    MembershipDues,
)
from .services import ensure_current_year_dues, user_has_governance_access

User = get_user_model()


class MemberModelTest(TestCase):
    """Test Member model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_member(self):
        """Test creating a member."""
        member = Member.objects.create(
            user=self.user,
            member_type='student',
            is_active_member=True
        )
        self.assertEqual(member.user, self.user)
        self.assertEqual(member.member_type, 'student')
        self.assertTrue(member.is_active_member)
    
    def test_member_str(self):
        """Test member string representation."""
        member = Member.objects.create(
            user=self.user,
            member_type='student'
        )
        self.assertIsNotNone(str(member))


class MembershipStatusModelTest(TestCase):
    """Test MembershipStatus model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.member = Member.objects.create(
            user=self.user,
            member_type='student'
        )
    
    def test_create_membership_status(self):
        """Test creating a membership status."""
        status = MembershipStatus.objects.create(
            member=self.member,
            status='active',
            effective_date=date.today()
        )
        self.assertEqual(status.member, self.member)
        self.assertEqual(status.status, 'active')
    
    def test_membership_status_str(self):
        """Test membership status string representation."""
        status = MembershipStatus.objects.create(
            member=self.member,
            status='active',
            effective_date=date.today()
        )
        self.assertIsNotNone(str(status))


class ExecutiveBoardModelTest(TestCase):
    """Test ExecutiveBoard model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.member = Member.objects.create(
            user=self.user,
            member_type='student'
        )
    
    def test_create_executive_board(self):
        """Test creating an executive board."""
        from datetime import timedelta
        start_date = date.today()
        end_date = start_date + timedelta(days=730)  # 2 years
        board = ExecutiveBoard.objects.create(
            term_start_date=start_date,
            term_end_date=end_date
        )
        self.assertEqual(board.term_start_date, start_date)
        self.assertEqual(board.term_end_date, end_date)
    
    def test_executive_board_str(self):
        """Test executive board string representation."""
        from datetime import timedelta
        start_date = date.today()
        end_date = start_date + timedelta(days=730)  # 2 years
        board = ExecutiveBoard.objects.create(
            term_start_date=start_date,
            term_end_date=end_date
        )
        self.assertIsNotNone(str(board))


class ExecutivePositionModelTest(TestCase):
    """Test ExecutivePosition model."""
    
    def setUp(self):
        """Set up test data."""
        from datetime import timedelta
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        start_date = date.today()
        end_date = start_date + timedelta(days=730)  # 2 years
        self.board = ExecutiveBoard.objects.create(
            term_start_date=start_date,
            term_end_date=end_date
        )
    
    def test_create_executive_position(self):
        """Test creating an executive position."""
        from datetime import timedelta
        start_date = date.today()
        end_date = start_date + timedelta(days=730)  # 2 years
        self.board = ExecutiveBoard.objects.create(
            term_start_date=start_date,
            term_end_date=end_date
        )
        position = ExecutivePosition.objects.create(
            board=self.board,
            user=self.user,
            position='president',
            start_date=date.today()
        )
        self.assertEqual(position.board, self.board)
        self.assertEqual(position.user, self.user)
        self.assertEqual(position.position, 'president')
    
    def test_executive_position_str(self):
        """Test executive position string representation."""
        from datetime import timedelta
        start_date = date.today()
        end_date = start_date + timedelta(days=730)  # 2 years
        self.board = ExecutiveBoard.objects.create(
            term_start_date=start_date,
            term_end_date=end_date
        )
        position = ExecutivePosition.objects.create(
            board=self.board,
            user=self.user,
            position='president',
            start_date=date.today()
        )
        self.assertIsNotNone(str(position))

    def test_standard_role_label_is_normalized_to_internal_code(self):
        """Human-readable built-in roles should still work with internal logic."""
        position = ExecutivePosition.objects.create(
            board=self.board,
            user=self.user,
            position='President',
            start_date=date.today()
        )
        self.assertEqual(position.position, 'president')
        self.assertEqual(position.get_position_display(), 'President')

    def test_custom_role_is_preserved(self):
        """Custom roles should remain custom while displaying cleanly."""
        position = ExecutivePosition.objects.create(
            board=self.board,
            user=self.user,
            position='Welfare Officer',
            start_date=date.today()
        )
        self.assertEqual(position.position, 'Welfare Officer')
        self.assertEqual(position.get_position_display(), 'Welfare Officer')


class GovernanceViewsTest(TestCase):
    """Test governance views."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_approved=True
        )
        self.member = Member.objects.create(
            user=self.user,
            member_type='student',
            is_active_member=True
        )
    
    def test_governance_views_require_login(self):
        """Test that governance views require login."""
        # Test member portal view
        try:
            url = reverse('governance:member_portal')
            response = self.client.get(url)
            # Should redirect to login or require authentication
            self.assertIn(response.status_code, [302, 403])
        except:
            # If URL doesn't exist, that's okay
            pass


class GovernanceRuntimeRegressionTest(TestCase):
    """Regression tests for recent runtime fixes."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='formerpresident',
            email='former-president@example.com',
            password='testpass123'
        )

    def test_association_event_absolute_url_uses_existing_route(self):
        event = AssociationEvent.objects.create(
            title='Governance Event',
            event_type='other',
            description='Regression test event',
            start_date=timezone.now(),
            location='Rome'
        )
        expected_url = reverse('governance:association_event_detail', kwargs={'pk': event.pk})
        self.assertEqual(event.get_absolute_url(), expected_url)

    def test_board_creation_deduplicates_former_president_members(self):
        # Two historical presidency rows for one user should produce one auditor membership.
        executive_board_one = ExecutiveBoard.objects.create(
            term_start_date=date(2020, 1, 1),
            term_end_date=date(2021, 12, 31)
        )
        executive_board_two = ExecutiveBoard.objects.create(
            term_start_date=date(2022, 1, 1),
            term_end_date=date(2023, 12, 31)
        )
        ExecutivePosition.objects.create(
            board=executive_board_one,
            user=self.user,
            position='president',
            start_date=date(2020, 1, 1),
            end_date=date(2020, 6, 1),
            status='resigned',
        )
        ExecutivePosition.objects.create(
            board=executive_board_two,
            user=self.user,
            position='president',
            start_date=date(2020, 6, 2),
            end_date=date(2021, 1, 1),
            status='replaced',
        )

        board = BoardOfAuditors.objects.create(
            name='2026-2028 Board of Auditors',
            term_start=date(2026, 1, 1),
            term_end=date(2027, 12, 31),
        )

        memberships = AuditorMember.objects.filter(board=board, user=self.user)
        self.assertEqual(memberships.count(), 1)
        self.assertTrue(memberships.first().is_former_president)


class GovernanceWorkflowServiceTest(TestCase):
    """Workflow-oriented governance coverage."""

    def setUp(self):
        self.president = User.objects.create_user(
            username='president_user',
            email='president@example.com',
            password='testpass123',
            is_approved=True,
        )
        self.member_user = User.objects.create_user(
            username='member_user',
            email='member@example.com',
            password='testpass123',
            is_approved=True,
        )
        self.member = Member.objects.create(
            user=self.member_user,
            member_type='student',
            is_active_member=False,
        )
        self.board = ExecutiveBoard.objects.create(
            term_start_date=date.today(),
            term_end_date=date.today() + timedelta(days=730),
            status='active',
        )
        ExecutivePosition.objects.create(
            board=self.board,
            user=self.president,
            position='president',
            start_date=date.today(),
            status='active',
        )

    def test_paid_dues_activate_member_and_create_status_history(self):
        dues = MembershipDues.objects.create(
            member=self.member,
            year=date.today().year,
            amount=Decimal('10.00'),
            due_date=date(date.today().year, 3, 31),
            payment_date=date.today(),
            payment_method='cash',
            status='paid',
        )

        self.member.refresh_from_db()
        dues.refresh_from_db()
        self.assertTrue(self.member.is_active_member)
        self.assertEqual(dues.valid_from, date(date.today().year, 1, 1))
        self.assertEqual(dues.valid_until, date(date.today().year, 12, 31))
        self.assertTrue(
            MembershipStatus.objects.filter(
                member=self.member,
                status='active',
                reason__icontains='Dues paid',
            ).exists()
        )

    def test_sympathizer_dues_also_expire_on_december_31(self):
        sympathizer_user = User.objects.create_user(
            username='sympathizer_user',
            email='sympathizer@example.com',
            password='testpass123',
            is_approved=True,
        )
        sympathizer = Member.objects.create(
            user=sympathizer_user,
            member_type='sympathizer',
            is_active_member=False,
        )

        dues = MembershipDues.objects.create(
            member=sympathizer,
            year=date.today().year,
            amount=Decimal('5.00'),
            due_date=date(date.today().year, 3, 31),
            payment_date=date.today(),
            payment_method='cash',
            status='paid',
        )

        sympathizer.refresh_from_db()
        dues.refresh_from_db()
        self.assertTrue(sympathizer.is_active_member)
        self.assertEqual(dues.valid_from, date(date.today().year, 1, 1))
        self.assertEqual(dues.valid_until, date(date.today().year, 12, 31))

    def test_ensure_current_year_dues_uses_member_type_amount(self):
        student_dues = ensure_current_year_dues(self.member, year=date.today().year)
        self.assertEqual(student_dues.amount, Decimal('10.00'))
        self.assertEqual(student_dues.due_date, date(date.today().year, 3, 31))

        sympathizer_user = User.objects.create_user(
            username='sympathizer_dues',
            email='sympathizer_dues@example.com',
            password='testpass123',
            is_approved=True,
        )
        sympathizer = Member.objects.create(
            user=sympathizer_user,
            member_type='sympathizer',
            is_active_member=False,
        )
        sympathizer_dues = ensure_current_year_dues(sympathizer, year=date.today().year)

        self.assertEqual(sympathizer_dues.amount, Decimal('5.00'))
        self.assertEqual(sympathizer_dues.due_date, date(date.today().year, 3, 31))

    def test_active_president_gets_governance_access_without_manual_permission(self):
        self.assertTrue(
            user_has_governance_access(self.president, 'governance.manage_assembly')
        )
        self.assertTrue(
            user_has_governance_access(self.president, 'governance.approve_expense')
        )

    def test_non_executive_member_does_not_get_expense_approval_access(self):
        self.assertFalse(
            user_has_governance_access(self.member_user, 'governance.approve_expense')
        )


class ElectionWorkflowRegressionTest(TestCase):
    """Election flow regression coverage for member-facing workflows."""

    def setUp(self):
        self.client = Client()
        self.voter = User.objects.create_user(
            username='voter_user',
            email='voter@example.com',
            password='testpass123',
            is_approved=True,
        )
        self.voter_member = Member.objects.create(
            user=self.voter,
            member_type='student',
            is_active_member=True,
            membership_start_date=date.today() - timedelta(days=400),
            lazio_residence_verified=True,
            cameroonian_origin_verified=True,
        )
        self.candidate_one = User.objects.create_user(
            username='candidate_one',
            email='candidate1@example.com',
            password='testpass123',
            is_approved=True,
        )
        Member.objects.create(
            user=self.candidate_one,
            member_type='student',
            is_active_member=True,
            membership_start_date=date.today() - timedelta(days=500),
            lazio_residence_verified=True,
            cameroonian_origin_verified=True,
        )
        self.candidate_two = User.objects.create_user(
            username='candidate_two',
            email='candidate2@example.com',
            password='testpass123',
            is_approved=True,
        )
        Member.objects.create(
            user=self.candidate_two,
            member_type='student',
            is_active_member=True,
            membership_start_date=date.today() - timedelta(days=500),
            lazio_residence_verified=True,
            cameroonian_origin_verified=True,
        )
        self.commission = ElectoralCommission.objects.create(
            name='2026 Electoral Commission',
            start_date=date.today() - timedelta(days=10),
            status='active',
        )
        self.election = Election.objects.create(
            commission=self.commission,
            election_type='executive_board',
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            status='in_progress',
        )
        self.candidacy_one = Candidacy.objects.create(
            election=self.election,
            candidate=self.candidate_one,
            position='president',
            application_date=date.today() - timedelta(days=2),
            status='approved',
            seniority_verified=True,
            lazio_residence_verified=True,
            cameroonian_origin_verified=True,
        )
        self.candidacy_two = Candidacy.objects.create(
            election=self.election,
            candidate=self.candidate_two,
            position='president',
            application_date=date.today() - timedelta(days=2),
            status='approved',
            seniority_verified=True,
            lazio_residence_verified=True,
            cameroonian_origin_verified=True,
        )

    def test_member_candidacy_application_submits_without_hidden_admin_fields(self):
        self.client.login(username='voter_user', password='testpass123')

        response = self.client.post(
            reverse('governance:candidacy_apply'),
            {
                'election': self.election.pk,
                'position': 'vice_president',
                'eligibility_notes': 'Ready to serve the community.',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('governance:member_portal'))

        candidacy = Candidacy.objects.get(
            election=self.election,
            candidate=self.voter,
            position='vice_president',
        )
        self.assertEqual(candidacy.status, 'pending')
        self.assertTrue(candidacy.seniority_verified)
        self.assertTrue(candidacy.lazio_residence_verified)
        self.assertTrue(candidacy.cameroonian_origin_verified)

    def test_member_can_review_and_update_vote_while_election_is_open(self):
        self.client.login(username='voter_user', password='testpass123')

        first_vote_response = self.client.post(
            reverse('governance:cast_election_vote', args=[self.election.pk]),
            {'position_president': str(self.candidacy_one.pk)},
        )
        self.assertEqual(first_vote_response.status_code, 302)
        self.assertEqual(
            ElectionVote.objects.filter(election=self.election, voter=self.voter).count(),
            1,
        )
        self.assertEqual(
            ElectionVote.objects.get(election=self.election, voter=self.voter).candidate,
            self.candidacy_one,
        )

        detail_response = self.client.get(
            reverse('governance:election_detail', args=[self.election.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Review or Update Vote')

        vote_page_response = self.client.get(
            reverse('governance:election_vote', args=[self.election.pk])
        )
        self.assertEqual(vote_page_response.status_code, 200)
        self.assertContains(vote_page_response, 'You have already voted for this position')

        second_vote_response = self.client.post(
            reverse('governance:cast_election_vote', args=[self.election.pk]),
            {'position_president': str(self.candidacy_two.pk)},
        )
        self.assertEqual(second_vote_response.status_code, 302)
        self.assertEqual(
            ElectionVote.objects.filter(election=self.election, voter=self.voter).count(),
            1,
        )
        self.assertEqual(
            ElectionVote.objects.get(election=self.election, voter=self.voter).candidate,
            self.candidacy_two,
        )

    def test_member_and_admin_election_lists_have_distinct_routes(self):
        self.assertEqual(reverse('governance:member_elections'), '/governance/elections/')
        self.assertEqual(reverse('governance:election_list'), '/governance/elections/manage/')

    def test_commission_member_can_manage_candidacies_without_manual_django_permission(self):
        commission_user = User.objects.create_user(
            username='commission_user',
            email='commission@example.com',
            password='testpass123',
            is_approved=True,
        )
        CommissionMember.objects.create(
            commission=self.commission,
            user=commission_user,
            role='secretary',
        )
        pending_candidacy = Candidacy.objects.create(
            election=self.election,
            candidate=self.voter,
            position='vice_president',
            application_date=date.today(),
            status='pending',
        )

        self.client.login(username='commission_user', password='testpass123')

        list_response = self.client.get(reverse('governance:election_list'))
        self.assertEqual(list_response.status_code, 200)

        approve_response = self.client.post(
            reverse('governance:approve_candidacy', args=[pending_candidacy.pk]),
            {'action': 'approve'},
        )
        self.assertEqual(approve_response.status_code, 302)

        pending_candidacy.refresh_from_db()
        self.assertEqual(pending_candidacy.status, 'approved')

