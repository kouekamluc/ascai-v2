"""
Audit live content and workflow readiness for production polish.
"""
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone

from apps.core.models import AssociationSettings, ServicePartner
from apps.dashboard.models import EventWaitlistEntry, OrientationSession, StudentQuestion, SupportTicket
from apps.diaspora.models import Event, News
from apps.downloads.models import Document
from apps.governance.models import Candidacy, Election, ExecutiveBoard, Member
from apps.mentorship.models import MentorProfile
from apps.scholarships.models import Scholarship
from apps.students.models import StudentGuideSection
from apps.universities.models import University


class Command(BaseCommand):
    help = "Check live-site content and workflow readiness."

    def handle(self, *args, **options):
        now = timezone.now()
        warnings = []
        notices = []

        try:
            settings = AssociationSettings.load()
        except (OperationalError, ProgrammingError) as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"Live readiness could not inspect the database ({exc}). "
                    "Run migrations first, then run this command again."
                )
            )
            return
        if not settings.public_email:
            warnings.append("Association public email is not configured.")
        if not settings.public_location:
            warnings.append("Association public location is not configured.")
        if not settings.map_embed_url and not settings.map_link_url:
            notices.append("Contact map is not configured; contact page will show a text fallback.")

        if not ExecutiveBoard.objects.filter(status="active").exists():
            warnings.append("No active executive board is configured for the leadership page.")

        if University.objects.count() == 0:
            warnings.append("No universities are published in the university directory.")
        if Scholarship.objects.count() == 0:
            warnings.append("No scholarships are available.")
        if Document.objects.filter(is_active=True).count() == 0:
            warnings.append("No active downloads/resources are available.")
        if StudentGuideSection.objects.filter(is_active=True).count() == 0:
            warnings.append("No published student guide sections are available.")
        if News.objects.filter(is_published=True).count() == 0:
            notices.append("No published news articles are available.")
        if Event.objects.filter(is_published=True, end_datetime__gte=now).count() == 0:
            notices.append("No upcoming published events are available.")
        if MentorProfile.objects.filter(is_approved=True).count() == 0:
            warnings.append("No approved mentor profiles are visible.")
        if ServicePartner.objects.filter(is_active=True, verification_status="verified").count() == 0:
            notices.append("No verified service partners are visible.")

        open_elections = Election.objects.filter(status="in_progress")
        for election in open_elections:
            approved_count = Candidacy.objects.filter(election=election, status="approved").count()
            if approved_count == 0:
                warnings.append(f"Election #{election.pk} is open but has no approved candidacies.")

        active_members = Member.objects.filter(is_active_member=True).count()
        if open_elections.exists() and active_members == 0:
            warnings.append("There are open elections but no active members eligible to vote.")

        pending_orientation = OrientationSession.objects.filter(is_confirmed=False).count()
        unresolved_questions = StudentQuestion.objects.filter(is_resolved=False).count()
        open_tickets = SupportTicket.objects.filter(status__in=["open", "pending"]).count()
        active_waitlist = EventWaitlistEntry.objects.filter(status="waiting").count()

        if pending_orientation:
            notices.append(f"{pending_orientation} orientation request(s) need review.")
        if unresolved_questions:
            notices.append(f"{unresolved_questions} student question(s) need response.")
        if open_tickets:
            notices.append(f"{open_tickets} support ticket(s) are open or pending.")
        if active_waitlist:
            notices.append(f"{active_waitlist} event waitlist entry/entries are active.")

        if warnings:
            self.stdout.write(self.style.WARNING("Live readiness warnings:"))
            for warning in warnings:
                self.stdout.write(f" - {warning}")
        else:
            self.stdout.write(self.style.SUCCESS("No blocking live readiness warnings found."))

        if notices:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Operational notices:"))
            for notice in notices:
                self.stdout.write(f" - {notice}")

        if not warnings and not notices:
            self.stdout.write(self.style.SUCCESS("Live workflows and content look polished."))
