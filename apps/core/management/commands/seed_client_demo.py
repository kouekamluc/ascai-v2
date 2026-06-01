"""
Seed a realistic client-demo dataset for the ASCAI delivery walkthrough.
"""
from datetime import timedelta

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.dashboard.models import BureauMessage, CommunityGroup, EventRegistration
from apps.diaspora.models import Event, News
from apps.downloads.models import Document
from apps.governance.models import Member, MembershipDues
from apps.governance.services import get_expected_dues_amount, get_membership_due_date
from apps.mentorship.models import MentorProfile, MentorshipRequest
from apps.scholarships.models import Scholarship
from apps.universities.models import SavedUniversity, University, UniversityProgram


User = get_user_model()


class Command(BaseCommand):
    help = "Create labelled demo users and records for client delivery walkthroughs."

    def handle(self, *args, **options):
        admin = self._user(
            username="demo_bureau",
            email="demo.bureau@ascai.local",
            role="admin",
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            is_approved=True,
            full_name="ASCAI Bureau Demo",
        )
        student = self._user(
            username="demo_student",
            email="demo.student@ascai.local",
            role="student",
            email_verified=True,
            is_approved=True,
            full_name="Demo Student",
            city_in_lazio="rome",
            field_of_study="Computer Science",
        )
        mentor_user = self._user(
            username="demo_mentor",
            email="demo.mentor@ascai.local",
            role="mentor",
            email_verified=True,
            is_approved=True,
            full_name="Demo Mentor",
            city_in_lazio="rome",
            profession="Graduate mentor",
        )
        unverified = self._user(
            username="demo_unverified",
            email="demo.unverified@ascai.local",
            role="student",
            email_verified=False,
            is_approved=False,
            full_name="Demo Unverified Signup",
        )

        self._email_address(admin, True)
        self._email_address(student, True)
        self._email_address(mentor_user, True)
        self._email_address(unverified, False)

        university, _ = University.objects.update_or_create(
            name="Sapienza University of Rome",
            defaults={
                "city": "rome",
                "address": "Piazzale Aldo Moro 5, Rome",
                "website": "https://www.uniroma1.it/",
                "email": "demo@sapienza.example",
                "description": "Demo university record used for client walkthroughs.",
                "languages": ["Italian", "English"],
                "degree_types": ["Bachelor", "Master", "PhD"],
                "fields_of_study": ["Computer Science", "Engineering", "Medicine"],
            },
        )
        UniversityProgram.objects.update_or_create(
            university=university,
            name="Computer Science Demo Track",
            defaults={
                "degree_type": "master",
                "field": "Computer Science",
                "duration_years": 2,
                "language": "english",
                "tuition": "1200.00",
                "description": "Demo program for the client delivery walkthrough.",
                "requirements": "Bachelor degree, transcript, language proof.",
            },
        )
        student.university = university
        student.save(update_fields=["university"])
        SavedUniversity.objects.get_or_create(user=student, university=university)

        Scholarship.objects.update_or_create(
            title="Demo DISCO Lazio Scholarship",
            defaults={
                "provider": "DISCO Lazio",
                "description": "Demo funding opportunity for the client walkthrough.",
                "amount": "2500.00",
                "currency": "EUR",
                "eligibility_criteria": "Students enrolled in Lazio with required documentation.",
                "application_deadline": timezone.now().date() + timedelta(days=45),
                "application_url": "https://example.com/demo-scholarship",
                "level": "all",
                "region": "lazio",
                "is_disco_lazio": True,
                "status": "active",
            },
        )

        document, _ = Document.objects.update_or_create(
            title="Demo Residence Permit Checklist",
            defaults={
                "description": "A demo member resource for residence permit preparation.",
                "category": "guidelines",
                "tags": "demo, residence permit, checklist",
                "is_active": True,
                "is_reserved": True,
                "uploaded_by": admin,
            },
        )
        if not document.file:
            document.file.save(
                "demo-residence-permit-checklist.txt",
                ContentFile("Demo checklist for residence permit preparation."),
                save=True,
            )

        event, _ = Event.objects.update_or_create(
            title="Demo ASCAI Welcome Session",
            defaults={
                "description": "Demo event showing registrations and tickets.",
                "location": "Rome",
                "start_datetime": timezone.now() + timedelta(days=14),
                "end_datetime": timezone.now() + timedelta(days=14, hours=2),
                "event_type": "workshop",
                "organizer": admin,
                "is_published": True,
                "registration_required": True,
                "capacity": 30,
                "waitlist_enabled": True,
            },
        )
        EventRegistration.objects.get_or_create(user=student, event=event)

        News.objects.update_or_create(
            title="Demo: ASCAI prepares a new student support cycle",
            defaults={
                "content": "Demo news item for the client delivery walkthrough.",
                "author": admin,
                "category": "announcement",
                "is_published": True,
                "published_at": timezone.now(),
                "language": "en",
            },
        )

        group, _ = CommunityGroup.objects.update_or_create(
            name="Demo New Students Lazio",
            defaults={
                "category": "new_students",
                "description": "Demo group for new students preparing arrival and documents.",
                "is_public": True,
                "featured": True,
                "created_by": admin,
            },
        )
        group.members.add(student)

        mentor_profile = mentor_user.mentor_profile
        mentor_profile.specialization = "University applications and settlement"
        mentor_profile.years_experience = 5
        mentor_profile.bio = "Demo mentor profile for client walkthroughs."
        mentor_profile.availability_status = "available"
        mentor_profile.response_time = "Within 24 hours"
        mentor_profile.is_approved = True
        mentor_profile.save()

        member = student.member_profile
        member.member_type = "student"
        member.lazio_residence_verified = True
        member.cameroonian_origin_verified = True
        member.is_active_member = False
        member.save()
        dues, _ = MembershipDues.objects.update_or_create(
            member=member,
            year=timezone.now().year,
            defaults={
                "amount": get_expected_dues_amount(member),
                "due_date": get_membership_due_date(timezone.now().year),
                "status": "pending",
                "notes": "[Demo] Payment requested by user. Use admin to mark paid.",
            },
        )

        MentorshipRequest.objects.get_or_create(
            student=student,
            mentor=mentor_profile,
            subject="Demo mentorship request",
            defaults={
                "message": "I would like help understanding university enrollment steps.",
                "status": "pending",
            },
        )

        BureauMessage.objects.update_or_create(
            recipient=student,
            subject="Demo membership payment follow-up",
            defaults={
                "sender": admin,
                "body": "<p>Please upload or bring your dues receipt so the bureau can confirm payment.</p>",
                "allow_reply": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Client demo data is ready."))
        self.stdout.write(f"Student: {student.username} / demo-password")
        self.stdout.write(f"Mentor: {mentor_user.username} / demo-password")
        self.stdout.write(f"Bureau: {admin.username} / demo-password")
        self.stdout.write(f"Pending dues record: {dues.pk}")

    def _user(self, username, email, role, **defaults):
        password = "demo-password"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": role,
                **defaults,
            },
        )
        for field, value in {"email": email, "role": role, **defaults}.items():
            setattr(user, field, value)
        user.set_password(password)
        user.save()
        return user

    def _email_address(self, user, verified):
        EmailAddress.objects.update_or_create(
            user=user,
            email=user.email,
            defaults={"verified": verified, "primary": True},
        )
