"""
Management command to populate forum categories with default categories.
"""
from django.core.management.base import BaseCommand
from apps.community.models import ForumCategory


class Command(BaseCommand):
    help = 'Populate forum categories with default categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing categories before populating',
        )

    def handle(self, *args, **options):
        clear = options.get('clear', False)

        if clear:
            self.stdout.write('Clearing existing forum categories...')
            ForumCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing categories'))

        self.stdout.write('Populating forum categories...')
        
        categories_data = [
            {
                'name': 'General Discussion',
                'description': 'General discussions about life in Lazio, Italy, and the Cameroonian community.',
                'slug': 'general-discussion',
                'order': 1,
            },
            {
                'name': 'Academic Help',
                'description': 'Questions and discussions about universities, courses, exams, and academic life.',
                'slug': 'academic-help',
                'order': 2,
            },
            {
                'name': 'Housing & Accommodation',
                'description': 'Find roommates, housing tips, and accommodation advice.',
                'slug': 'housing-accommodation',
                'order': 3,
            },
            {
                'name': 'Jobs & Career',
                'description': 'Job opportunities, career advice, and professional networking.',
                'slug': 'jobs-career',
                'order': 4,
            },
            {
                'name': 'Legal & Documents',
                'description': 'Questions about residence permits, visas, legal documents, and bureaucracy.',
                'slug': 'legal-documents',
                'order': 5,
            },
            {
                'name': 'Events & Activities',
                'description': 'Upcoming events, activities, and community gatherings.',
                'slug': 'events-activities',
                'order': 6,
            },
            {
                'name': 'Scholarships & Financial Aid',
                'description': 'Information about scholarships, grants, and financial assistance.',
                'slug': 'scholarships-financial-aid',
                'order': 7,
            },
            {
                'name': 'Cultural Exchange',
                'description': 'Cultural discussions, traditions, and sharing experiences.',
                'slug': 'cultural-exchange',
                'order': 8,
            },
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = ForumCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'order': cat_data['order'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created category: {category.name}')
            else:
                # Update existing category
                category.name = cat_data['name']
                category.description = cat_data['description']
                category.order = cat_data['order']
                category.save()
                self.stdout.write(f'  ↻ Updated category: {category.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {ForumCategory.objects.count()} forum categories'
                f' ({created_count} new, {len(categories_data) - created_count} updated)'
            )
        )

