"""Tests for accounts app."""
import re

from allauth.account.models import EmailAddress, get_emailconfirmation_model
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.governance.models import Member

from .models import User, UserDocument

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model."""
    
    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_approved)
        self.assertEqual(user.role, 'student')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_user_role_choices(self):
        """Test user role field."""
        user = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='testpass123'
        )
        user.role = 'mentor'
        user.save()
        self.assertEqual(user.role, 'mentor')
    
    def test_user_language_preference(self):
        """Test user language preference."""
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        user.language_preference = 'fr'
        user.save()
        self.assertEqual(user.language_preference, 'fr')
    
    def test_user_full_name(self):
        """Test user full name field."""
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123',
            full_name='John Doe'
        )
        self.assertEqual(user.full_name, 'John Doe')
    
    def test_user_city_in_lazio(self):
        """Test user city in Lazio field."""
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123',
            city_in_lazio='rome'
        )
        self.assertEqual(user.city_in_lazio, 'rome')
    
    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')


class UserDocumentModelTest(TestCase):
    """Test UserDocument model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_document(self):
        """Test creating a user document."""
        doc = UserDocument.objects.create(
            user=self.user,
            document_type='id_card',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.assertEqual(doc.user, self.user)
        self.assertEqual(doc.document_type, 'id_card')
        self.assertFalse(doc.is_verified)
    
    def test_user_document_str(self):
        """Test user document string representation."""
        doc = UserDocument.objects.create(
            user=self.user,
            document_type='id_card',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.assertIn('testuser', str(doc))


class AccountsViewsTest(TestCase):
    """Test accounts views."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_approved=True
        )
    
    def test_signup_flow_creates_pending_user(self):
        """The public signup flow should create a user pending admin approval."""
        response = self.client.post(
            reverse('account_signup'),
            {
                'username': 'newmember',
                'email': 'newmember@example.com',
                'password1': 'testpass12345',
                'password2': 'testpass12345',
                'phone': '+390000000',
                'role': 'student',
                'language_preference': 'en',
            },
        )
        self.assertEqual(response.status_code, 302)
        verification_sent_url = reverse('account_email_verification_notice')
        self.assertTrue(response.url.startswith(verification_sent_url))
        self.assertIn('email=newmember%40example.com', response.url)
        created_user = User.objects.get(username='newmember')
        self.assertFalse(created_user.is_approved)
        self.assertTrue(created_user.is_active)
        self.assertEqual(created_user.emailaddress_set.count(), 1)
        self.assertFalse(created_user.emailaddress_set.first().verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('confirm', mail.outbox[0].subject.lower())
        self.assertTrue(mail.outbox[0].alternatives)
        signup_html = mail.outbox[0].alternatives[0][0]
        self.assertIn('web-app-manifest-512x512.png', signup_html)
        self.assertIn('Thank you for signing up with ASCAI Lazio.', signup_html)

    def test_login_flow_redirects_approved_user_to_dashboard(self):
        """Approved users should enter through the dashboard route."""
        response = self.client.post(
            reverse('account_login'),
            {'login': 'testuser', 'password': 'testpass123'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires login."""
        url = reverse('accounts:profile')
        response = self.client.get(url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('accounts:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_page_matches_current_session_behavior(self):
        """Remember-me checkbox should only appear when the form actually supports it."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Remember me')

    def test_unprefixed_login_works_with_non_default_language_cookie(self):
        """Bare login URL should remain reachable after a language switch."""
        self.client.cookies.load({'django_language': 'fr'})

        response = self.client.get('/accounts/login/')

        self.assertEqual(response.status_code, 200)

    def test_signup_page_mentions_email_confirmation(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email Confirmation Sent')
        self.assertNotContains(response, 'Account Approval Required')
        self.assertContains(response, 'name="phone"', html=False)
        self.assertContains(response, 'name="role"', html=False)
        self.assertContains(response, 'name="language_preference"', html=False)

    def test_resend_verification_email_sends_confirmation(self):
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='testpass123',
            is_approved=True,
        )
        EmailAddress.objects.create(
            user=unverified_user,
            email=unverified_user.email,
            primary=True,
            verified=False,
        )

        response = self.client.post(
            reverse('accounts:resend_verification_email'),
            {'email': unverified_user.email},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_email_verification_notice'), response.url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('confirm', mail.outbox[0].subject.lower())

    def test_verification_notice_allows_anonymous_resend_entry(self):
        response = self.client.get(reverse('account_email_verification_notice'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resend Verification Email')
        self.assertContains(response, 'name="email"', html=False)

    def test_confirm_email_marks_user_verified(self):
        pending_user = User.objects.create_user(
            username='confirmme',
            email='confirmme@example.com',
            password='testpass123',
            is_approved=True,
        )
        email_address = EmailAddress.objects.create(
            user=pending_user,
            email=pending_user.email,
            primary=True,
            verified=False,
        )
        confirmation = get_emailconfirmation_model().create(email_address)

        get_response = self.client.get(
            reverse('account_confirm_email', args=[confirmation.key])
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Confirm Your Email')

        post_response = self.client.post(
            reverse('account_confirm_email', args=[confirmation.key])
        )
        self.assertEqual(post_response.status_code, 200)

        pending_user.refresh_from_db()
        email_address.refresh_from_db()
        self.assertTrue(pending_user.email_verified)
        self.assertTrue(email_address.verified)
        member = Member.objects.get(user=pending_user)
        self.assertEqual(member.member_type, 'student')
        self.assertFalse(member.is_active_member)
        self.assertContains(post_response, 'Your email has been successfully verified')
        self.assertContains(post_response, 'Your account is ready to use')
        self.assertContains(post_response, 'Sign In')

    def test_approved_mentor_gets_pending_member_profile(self):
        mentor = User.objects.create_user(
            username='mentor_member',
            email='mentor-member@example.com',
            password='testpass123',
            role='mentor',
            is_approved=False,
        )

        self.assertFalse(Member.objects.filter(user=mentor).exists())

        mentor.is_approved = True
        mentor.save()

        member = Member.objects.get(user=mentor)
        self.assertEqual(member.member_type, 'active')
        self.assertFalse(member.is_active_member)

    def test_password_reset_sends_branded_email(self):
        mail.outbox = []
        response = self.client.post(
            reverse('account_reset_password'),
            {'email': self.user.email},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('account_reset_password_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your ASCAI Lazio password', mail.outbox[0].subject)
        self.assertTrue(mail.outbox[0].body.lstrip().startswith('A password reset was requested for your ASCAI Lazio account.'))
        self.assertIn('/accounts/password/reset/key/', mail.outbox[0].body)
        self.assertIn('A password reset was requested for your ASCAI Lazio account.', mail.outbox[0].body)
        self.assertNotIn('Hello', mail.outbox[0].body)
        self.assertTrue(mail.outbox[0].alternatives)
        html_body = mail.outbox[0].alternatives[0][0]
        self.assertIn('web-app-manifest-512x512.png', html_body)
        self.assertIn('Reset Password', html_body)
        self.assertIn('copy and paste this link into your browser', html_body)
        self.assertIn('Use the secure button below to choose a new password.', html_body)
        match = re.search(r'href="([^"]+/accounts/password/reset/key/[^"]+)"', html_body)
        self.assertIsNotNone(match)
        self.assertIn('/accounts/password/reset/key/', match.group(1))
        self.assertTrue(match.group(1).startswith('http://testserver/'))


class AccountsURLsTest(TestCase):
    """Test accounts URLs."""
    
    def test_profile_url(self):
        """Test profile URL resolves."""
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/profile/')

    def test_allauth_login_url_resolves(self):
        self.assertEqual(reverse('account_login'), '/accounts/login/')

    def test_verification_notice_url_resolves(self):
        self.assertEqual(
            reverse('account_email_verification_notice'),
            '/accounts/email-verification-sent/',
        )


class ApprovalEmailBrandingTest(TestCase):
    """Ensure approval emails keep the branded HTML version."""

    def test_approval_email_includes_logo(self):
        user = User.objects.create_user(
            username='pendinguser',
            email='pending@example.com',
            password='testpass123',
            is_approved=False,
        )

        mail.outbox = []
        user.is_approved = True
        user.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].alternatives)
        html_body = mail.outbox[0].alternatives[0][0]
        self.assertIn('<img src="', html_body)
        self.assertIn('web-app-manifest-512x512.png', html_body)

