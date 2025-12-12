"""
Management command to populate scholarships data.
Uses sample scholarship data for Italian/Lazio region scholarships.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from apps.scholarships.models import Scholarship
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate scholarships data with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing scholarships before populating',
        )

    def handle(self, *args, **options):
        clear = options.get('clear', False)

        if clear:
            self.stdout.write('Clearing existing scholarships...')
            Scholarship.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing scholarships'))

        self.stdout.write('Populating scholarships data...')
        self.populate_sample_data()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {Scholarship.objects.count()} scholarships'
            )
        )

    def populate_sample_data(self):
        """Populate with sample scholarship data."""
        today = timezone.now().date()
        
        scholarships_data = [
            {
                'title': 'DISCO Lazio Scholarship for International Students',
                'provider': 'DISCO Lazio',
                'description': 'The DISCO Lazio scholarship program provides financial support to international students studying in the Lazio region. This scholarship covers tuition fees and provides a monthly stipend for living expenses.',
                'amount': Decimal('5000.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Open to all international students enrolled in a university in the Lazio region. Applicants must demonstrate financial need and academic excellence. Must be enrolled in a Bachelor\'s, Master\'s, or PhD program.',
                'application_deadline': today + timedelta(days=60),
                'application_url': 'https://www.discolazio.it/scholarships',
                'level': 'all',
                'region': 'lazio',
                'is_disco_lazio': True,
                'status': 'active',
            },
            {
                'title': 'Lazio Region Merit Scholarship',
                'provider': 'Regione Lazio',
                'description': 'Merit-based scholarship for outstanding students in the Lazio region. Awarded based on academic performance and achievements.',
                'amount': Decimal('3000.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Students with GPA above 3.5/4.0 or equivalent. Must be enrolled in a Lazio region university. Open to all degree levels.',
                'application_deadline': today + timedelta(days=45),
                'application_url': 'https://www.regione.lazio.it/scholarships',
                'level': 'all',
                'region': 'lazio',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'Sapienza University Excellence Scholarship',
                'provider': 'Sapienza University of Rome',
                'description': 'Scholarship for excellent international students at Sapienza University. Covers full tuition and provides accommodation support.',
                'amount': Decimal('8000.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'International students applying to Master\'s or PhD programs at Sapienza. Must have outstanding academic records. English or Italian language proficiency required.',
                'application_deadline': today + timedelta(days=90),
                'application_url': 'https://www.uniroma1.it/en/scholarships',
                'level': 'master',
                'region': 'lazio',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'Italian Government Scholarships for Foreign Students',
                'provider': 'Italian Ministry of Foreign Affairs',
                'description': 'Scholarships offered by the Italian government to foreign students for study and research in Italy. Available for all degree levels.',
                'amount': Decimal('900.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Foreign students from eligible countries. Must be enrolled or planning to enroll in an Italian university. Age limits apply (varies by program level).',
                'application_deadline': today + timedelta(days=120),
                'application_url': 'https://studyinitaly.esteri.it/en/call-for-procedure',
                'level': 'all',
                'region': 'all',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'Erasmus+ Mobility Grant',
                'provider': 'European Commission',
                'description': 'Erasmus+ provides grants for students to study, train, or volunteer abroad in Europe. Includes monthly allowance and travel support.',
                'amount': Decimal('400.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Students enrolled in a participating university. Must be studying in an EU country or partner country. Duration: 3-12 months.',
                'application_deadline': today + timedelta(days=30),
                'application_url': 'https://erasmus-plus.ec.europa.eu/',
                'level': 'all',
                'region': 'all',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'DISCO Lazio PhD Research Grant',
                'provider': 'DISCO Lazio',
                'description': 'Research grant for PhD students conducting research in the Lazio region. Supports research expenses and provides a monthly stipend.',
                'amount': Decimal('1200.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'PhD students enrolled in a Lazio region university. Research must be relevant to regional development. Must have research proposal approved by supervisor.',
                'application_deadline': today + timedelta(days=75),
                'application_url': 'https://www.discolazio.it/phd-grants',
                'level': 'phd',
                'region': 'lazio',
                'is_disco_lazio': True,
                'status': 'active',
            },
            {
                'title': 'Engineering Excellence Scholarship',
                'provider': 'Lazio Engineering Association',
                'description': 'Scholarship for students pursuing engineering degrees in the Lazio region. Focus on innovation and technology.',
                'amount': Decimal('2500.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Students enrolled in engineering programs at Lazio universities. Must demonstrate interest in innovation and technology. Open to Bachelor\'s and Master\'s students.',
                'application_deadline': today + timedelta(days=50),
                'application_url': 'https://www.engineeringlazio.it/scholarships',
                'level': 'bachelor',
                'region': 'lazio',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'Women in STEM Scholarship',
                'provider': 'Lazio Women in Tech',
                'description': 'Scholarship program to encourage women to pursue studies in Science, Technology, Engineering, and Mathematics in the Lazio region.',
                'amount': Decimal('3500.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Female students enrolled in STEM programs at Lazio universities. Must demonstrate academic excellence and commitment to STEM fields.',
                'application_deadline': today + timedelta(days=65),
                'application_url': 'https://www.womenintechlazio.it/scholarships',
                'level': 'all',
                'region': 'lazio',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'International Student Housing Grant',
                'provider': 'Lazio Student Services',
                'description': 'Financial support for international students to cover housing costs in the Lazio region. Helps with accommodation expenses.',
                'amount': Decimal('2000.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'International students enrolled in Lazio universities. Must demonstrate financial need. Priority given to students from developing countries.',
                'application_deadline': today + timedelta(days=40),
                'application_url': 'https://www.laziostudentservices.it/housing-grant',
                'level': 'all',
                'region': 'lazio',
                'is_disco_lazio': False,
                'status': 'active',
            },
            {
                'title': 'Cultural Exchange Scholarship',
                'provider': 'Lazio Cultural Foundation',
                'description': 'Scholarship for students interested in cultural exchange and promoting diversity in the Lazio region.',
                'amount': Decimal('1800.00'),
                'currency': 'EUR',
                'eligibility_criteria': 'Students enrolled in humanities, arts, or cultural studies programs. Must demonstrate involvement in cultural activities. Open to all degree levels.',
                'application_deadline': today + timedelta(days=55),
                'application_url': 'https://www.lazioculture.it/scholarships',
                'level': 'all',
                'region': 'lazio',
                'is_disco_lazio': False,
                'status': 'active',
            },
        ]

        created_count = 0
        with transaction.atomic():
            for scholarship_data in scholarships_data:
                scholarship, created = Scholarship.objects.get_or_create(
                    title=scholarship_data['title'],
                    defaults=scholarship_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {scholarship.title}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created {created_count} new scholarships')
        )










