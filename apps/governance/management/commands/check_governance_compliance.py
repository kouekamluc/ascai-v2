"""
Management command to check governance compliance and process automatic actions.
Checks for:
- Executive Board automatic resignations (Article 13)
- Vote publication deadlines (Article 24)
- 6-month general reports (Article 45)
- Assembly frequency compliance (Article 2)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.governance.models import (
    ExecutiveBoard, ExecutivePosition, GeneralAssembly, AssemblyAttendance,
    BoardMeeting, AssemblyVote, FinancialReport
)
from apps.governance.utils import (
    check_executive_board_vacancy, check_assembly_frequency_compliance,
    check_general_report_requirement
)


class Command(BaseCommand):
    help = 'Check governance compliance and process automatic actions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-resign',
            action='store_true',
            help='Automatically process resignations for excessive absences',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting governance compliance check...'))
        
        # Check Executive Board automatic resignations (Article 13)
        self.check_executive_board_resignations(options.get('auto_resign', False))
        
        # Check vote publication deadlines (Article 24)
        self.check_vote_publication_deadlines()
        
        # Check 6-month general reports (Article 45)
        self.check_general_reports()
        
        # Check assembly frequency compliance (Article 2)
        self.check_assembly_frequency()
        
        self.stdout.write(self.style.SUCCESS('Governance compliance check completed!'))

    def check_executive_board_resignations(self, auto_resign=False):
        """Check and process automatic resignations for Executive Board (Article 13)."""
        self.stdout.write('\n--- Checking Executive Board Resignations (Article 13) ---')
        
        active_boards = ExecutiveBoard.objects.filter(status='active')
        total_checked = 0
        total_resigned = 0
        
        for board in active_boards:
            positions = board.positions.filter(status='active')
            for position in positions:
                if position.user:
                    total_checked += 1
                    vacancy_check = check_executive_board_vacancy(board, position.position)
                    
                    if vacancy_check.get('auto_resigned'):
                        total_resigned += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ✓ Auto-resigned: {position.user.get_display_name()} '
                                f'({position.get_position_display()}) - {vacancy_check["reason"]}'
                            )
                        )
                    elif vacancy_check['is_vacant']:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ Vacant: {position.get_position_display()} - {vacancy_check["reason"]}'
                            )
                        )
        
        self.stdout.write(f'  Checked {total_checked} positions, {total_resigned} auto-resigned')

    def check_vote_publication_deadlines(self):
        """Check vote publication deadlines (Article 24 - 30 days)."""
        self.stdout.write('\n--- Checking Vote Publication Deadlines (Article 24) ---')
        
        unpublished_votes = AssemblyVote.objects.filter(is_published=False)
        overdue_count = 0
        approaching_count = 0
        
        for vote in unpublished_votes:
            if vote.is_publication_overdue:
                overdue_count += 1
                days_overdue = vote.days_since_assembly - 30
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ OVERDUE: {vote.assembly} - "{vote.question[:50]}..." '
                        f'({days_overdue} days overdue)'
                    )
                )
            elif vote.days_until_publication_deadline is not None and vote.days_until_publication_deadline <= 7:
                approaching_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ APPROACHING: {vote.assembly} - "{vote.question[:50]}..." '
                        f'({vote.days_until_publication_deadline} days remaining)'
                    )
                )
        
        self.stdout.write(f'  {overdue_count} overdue, {approaching_count} approaching deadline')

    def check_general_reports(self):
        """Check 6-month general report requirement (Article 45)."""
        self.stdout.write('\n--- Checking General Reports (Article 45) ---')
        
        report_status = check_general_report_requirement()
        
        if report_status['compliant']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Compliant: Last report {report_status["last_report_date"]}, '
                    f'next due {report_status["next_due_date"]}'
                )
            )
        else:
            if report_status['days_overdue']:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ OVERDUE: {report_status["days_overdue"]} days overdue. '
                        f'Last report: {report_status["last_report_date"]}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ {report_status["message"]}'
                    )
                )

    def check_assembly_frequency(self):
        """Check assembly frequency compliance (Article 2)."""
        self.stdout.write('\n--- Checking Assembly Frequency (Article 2) ---')
        
        frequency_status = check_assembly_frequency_compliance()
        
        if frequency_status['compliant']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Compliant: {frequency_status["assembly_count"]} assemblies in last year'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠ {frequency_status["message"]}'
                )
            )

