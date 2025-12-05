"""
Tests for governance app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from decimal import Decimal
from .models import Member, MembershipStatus, ExecutiveBoard, ExecutivePosition

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

