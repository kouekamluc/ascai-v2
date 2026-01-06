"""
Management command to populate initial news articles and events.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.diaspora.models import News, Event

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate initial news articles and events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing news and events before populating',
        )

    def handle(self, *args, **options):
        clear = options.get('clear', False)

        # Get or create admin user for author
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ascailazio.org',
                'is_staff': True,
                'is_superuser': True,
                'is_approved': True,
            }
        )

        if clear:
            self.stdout.write('Clearing existing news and events...')
            News.objects.all().delete()
            Event.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing content'))

        self.stdout.write('Populating initial content...')

        # Create sample news articles
        news_data = [
            {
                'title': 'Welcome to ASCAI Lazio Platform',
                'content': '''<p>Welcome to the official platform of the Association of Cameroonian Students and Academics in the Lazio Region (ASCAI Lazio).</p>
                <p>This platform serves as a digital hub for our community, providing resources, information, and opportunities for connection.</p>
                <p>We are excited to have you here and look forward to building a stronger community together.</p>''',
                'category': 'announcement',
                'language': 'en',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=1),
            },
            {
                'title': 'Bienvenue sur la Plateforme ASCAI Lazio',
                'content': '''<p>Bienvenue sur la plateforme officielle de l'Association des Étudiants et Universitaires Camerounais de la Région du Latium (ASCAI Lazio).</p>
                <p>Cette plateforme sert de centre numérique pour notre communauté, offrant des ressources, des informations et des opportunités de connexion.</p>
                <p>Nous sommes ravis de vous avoir ici et nous réjouissons de construire une communauté plus forte ensemble.</p>''',
                'category': 'announcement',
                'language': 'fr',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=1),
            },
            {
                'title': 'Upcoming General Assembly Meeting',
                'content': '''<p>We are pleased to announce our upcoming General Assembly meeting.</p>
                <p>All members are invited to attend and participate in important discussions about the future of our association.</p>
                <p>Details about the date, time, and location will be communicated soon.</p>''',
                'category': 'announcement',
                'language': 'en',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=2),
            },
            {
                'title': 'Scholarship Opportunities Available',
                'content': '''<p>We are happy to share information about available scholarship opportunities for Cameroonian students in Lazio.</p>
                <p>Check our scholarships section for detailed information about DISCO Lazio and other available scholarships.</p>
                <p>Application deadlines vary, so please check each scholarship carefully.</p>''',
                'category': 'academic',
                'language': 'en',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=3),
            },
            {
                'title': 'Mentorship Program Launch',
                'content': '''<p>We are excited to launch our mentorship program!</p>
                <p>Experienced members are available to provide guidance and support to new students and community members.</p>
                <p>If you are looking for a mentor or would like to become a mentor, please visit our mentorship section.</p>''',
                'category': 'general',
                'language': 'en',
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=4),
            },
        ]

        created_news = 0
        for news_item in news_data:
            from django.utils.text import slugify
            slug = slugify(news_item['title'])
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{slugify(news_item['title'])}-{counter}"
                counter += 1
            
            news, created = News.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': news_item['title'],
                    'content': news_item['content'],
                    'category': news_item['category'],
                    'language': news_item['language'],
                    'is_published': news_item['is_published'],
                    'published_at': news_item['published_at'],
                    'author': admin_user,
                }
            )
            if created:
                created_news += 1
                self.stdout.write(f'  ✓ Created news: {news.title}')
            else:
                self.stdout.write(f'  ↻ News already exists: {news.title}')

        # Create sample events
        events_data = [
            {
                'title': 'ASCAI Lazio Welcome Event',
                'description': '''<p>Join us for our annual welcome event for new students and community members!</p>
                <p>This is a great opportunity to meet other members, learn about the association, and get connected with resources.</p>
                <p>Food and refreshments will be provided.</p>''',
                'location': 'Rome, Italy (TBA)',
                'start_datetime': timezone.now() + timedelta(days=30),
                'end_datetime': timezone.now() + timedelta(days=30, hours=3),
                'language': 'en',
                'is_published': True,
                'registration_required': True,
                'max_participants': 100,
            },
            {
                'title': 'Événement de Bienvenue ASCAI Lazio',
                'description': '''<p>Rejoignez-nous pour notre événement de bienvenue annuel pour les nouveaux étudiants et membres de la communauté !</p>
                <p>C'est une excellente occasion de rencontrer d'autres membres, d'en apprendre davantage sur l'association et de se connecter avec des ressources.</p>
                <p>Nourriture et rafraîchissements seront fournis.</p>''',
                'location': 'Rome, Italie (À confirmer)',
                'start_datetime': timezone.now() + timedelta(days=30),
                'end_datetime': timezone.now() + timedelta(days=30, hours=3),
                'language': 'fr',
                'is_published': True,
                'registration_required': True,
                'max_participants': 100,
            },
            {
                'title': 'Academic Success Workshop',
                'description': '''<p>Learn strategies for academic success in Italian universities.</p>
                <p>Topics covered include study techniques, exam preparation, and navigating the Italian academic system.</p>
                <p>Open to all students.</p>''',
                'location': 'Online (Zoom)',
                'start_datetime': timezone.now() + timedelta(days=45),
                'end_datetime': timezone.now() + timedelta(days=45, hours=2),
                'language': 'en',
                'is_published': True,
                'registration_required': True,
                'max_participants': 50,
            },
        ]

        created_events = 0
        for event_item in events_data:
            # Generate slug manually
            from django.utils.text import slugify
            slug = slugify(event_item['title'])
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{slugify(event_item['title'])}-{counter}"
                counter += 1

            event, created = Event.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': event_item['title'],
                    'description': event_item['description'],
                    'location': event_item['location'],
                    'start_datetime': event_item['start_datetime'],
                    'end_datetime': event_item['end_datetime'],
                    'language': event_item['language'],
                    'is_published': event_item['is_published'],
                    'registration_required': event_item['registration_required'],
                    'max_participants': event_item['max_participants'],
                    'organizer': admin_user,
                }
            )
            if created:
                created_events += 1
                self.stdout.write(f'  ✓ Created event: {event.title}')
            else:
                self.stdout.write(f'  ↻ Event already exists: {event.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated content:'
                f'\n  - {created_news} new news articles (total: {News.objects.count()})'
                f'\n  - {created_events} new events (total: {Event.objects.count()})'
            )
        )

