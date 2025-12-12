"""
Management command to populate universities data.
Can fetch from API or use sample Italian university data for Lazio region.
"""
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.universities.models import University, UniversityProgram
from decimal import Decimal
import json


class Command(BaseCommand):
    help = 'Populate universities data from API or sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-api',
            action='store_true',
            help='Try to fetch data from Universities List API',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing universities before populating',
        )

    def handle(self, *args, **options):
        use_api = options.get('use_api', False)
        clear = options.get('clear', False)

        if clear:
            self.stdout.write('Clearing existing universities...')
            University.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing universities'))

        if use_api:
            self.stdout.write('Attempting to fetch from API...')
            try:
                self.fetch_from_api()
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'API fetch failed: {e}. Using sample data instead.')
                )
                self.populate_sample_data()
        else:
            self.stdout.write('Using sample Italian university data for Lazio region...')
            self.populate_sample_data()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {University.objects.count()} universities'
            )
        )

    def fetch_from_api(self):
        """Fetch universities from Universities List API."""
        # Try to fetch from a generic universities API
        # Note: Most free APIs are US-focused, so this may not work well for Italian universities
        try:
            # Example: Universities List API (may need API key)
            url = 'http://universities.hipolabs.com/search?country=Italy'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            created_count = 0
            with transaction.atomic():
                for uni_data in data:
                    # Filter for Lazio region cities
                    name = uni_data.get('name', '')
                    # Map common Italian university names to Lazio cities
                    city_mapping = self._map_university_to_city(name)
                    if not city_mapping:
                        continue

                    city, address = city_mapping
                    
                    # Create university
                    university, created = University.objects.get_or_create(
                        name=name,
                        defaults={
                            'city': city,
                            'address': address or f'{city}, Lazio, Italy',
                            'website': uni_data.get('web_pages', [None])[0] if uni_data.get('web_pages') else None,
                            'description': f'University located in {city}, Lazio region, Italy.',
                            'tuition_range_min': Decimal('1000.00'),
                            'tuition_range_max': Decimal('5000.00'),
                            'languages': ['Italian', 'English'],
                            'degree_types': ['Bachelor', 'Master', 'PhD'],
                            'fields_of_study': ['Engineering', 'Medicine', 'Law', 'Business', 'Arts', 'Sciences'],
                        }
                    )
                    if created:
                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'✓ Created {created_count} universities from API')
            )
        except Exception as e:
            raise Exception(f'API fetch error: {str(e)}')

    def _map_university_to_city(self, name):
        """Map university name to Lazio city."""
        name_lower = name.lower()
        
        # Rome universities
        if any(keyword in name_lower for keyword in ['sapienza', 'roma tre', 'tor vergata', 'luiss', 'cattolica']):
            return ('rome', 'Rome, Lazio, Italy')
        
        # Other Lazio cities
        if 'cassino' in name_lower:
            return ('cassino', 'Cassino, Lazio, Italy')
        if 'viterbo' in name_lower or 'tuscia' in name_lower:
            return ('viterbo', 'Viterbo, Lazio, Italy')
        if 'latina' in name_lower:
            return ('latina', 'Latina, Lazio, Italy')
        if 'frosinone' in name_lower:
            return ('frosinone', 'Frosinone, Lazio, Italy')
        if 'rieti' in name_lower:
            return ('rieti', 'Rieti, Lazio, Italy')
        
        return None

    def populate_sample_data(self):
        """Populate with sample Italian university data for Lazio region."""
        universities_data = [
            {
                'name': 'Sapienza University of Rome',
                'city': 'rome',
                'address': 'Piazzale Aldo Moro, 5, 00185 Roma RM, Italy',
                'website': 'https://www.uniroma1.it',
                'email': 'info@uniroma1.it',
                'phone': '+39 06 49911',
                'description': 'Sapienza University of Rome is one of the oldest and largest universities in Europe, founded in 1303. It offers a wide range of programs in various fields.',
                'tuition_range_min': Decimal('1000.00'),
                'tuition_range_max': Decimal('3000.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master', 'PhD'],
                'fields_of_study': ['Engineering', 'Medicine', 'Law', 'Business', 'Arts', 'Sciences', 'Architecture'],
            },
            {
                'name': 'University of Rome Tor Vergata',
                'city': 'rome',
                'address': 'Via Orazio Raimondo, 18, 00173 Roma RM, Italy',
                'website': 'https://www.uniroma2.it',
                'email': 'info@uniroma2.it',
                'phone': '+39 06 72591',
                'description': 'Tor Vergata is a public research university located in Rome. It is known for its strong programs in economics, engineering, and medicine.',
                'tuition_range_min': Decimal('1000.00'),
                'tuition_range_max': Decimal('2800.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master', 'PhD'],
                'fields_of_study': ['Engineering', 'Medicine', 'Economics', 'Business', 'Sciences'],
            },
            {
                'name': 'Roma Tre University',
                'city': 'rome',
                'address': 'Via della Vasca Navale, 79, 00146 Roma RM, Italy',
                'website': 'https://www.uniroma3.it',
                'email': 'info@uniroma3.it',
                'phone': '+39 06 5733 1',
                'description': 'Roma Tre University is a public university in Rome, established in 1992. It offers modern facilities and innovative programs.',
                'tuition_range_min': Decimal('1000.00'),
                'tuition_range_max': Decimal('2500.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master', 'PhD'],
                'fields_of_study': ['Engineering', 'Architecture', 'Law', 'Economics', 'Arts', 'Sciences'],
            },
            {
                'name': 'LUISS Guido Carli',
                'city': 'rome',
                'address': 'Viale Pola, 12, 00198 Roma RM, Italy',
                'website': 'https://www.luiss.edu',
                'email': 'info@luiss.it',
                'phone': '+39 06 852251',
                'description': 'LUISS is a private university specializing in business, economics, law, and political science. It offers programs in English and Italian.',
                'tuition_range_min': Decimal('8000.00'),
                'tuition_range_max': Decimal('15000.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master', 'PhD'],
                'fields_of_study': ['Business', 'Economics', 'Law', 'Political Science'],
            },
            {
                'name': 'University of Cassino and Southern Lazio',
                'city': 'cassino',
                'address': 'Via G. Di Biasio, 43, 03043 Cassino FR, Italy',
                'website': 'https://www.unicas.it',
                'email': 'info@unicas.it',
                'phone': '+39 0776 2991',
                'description': 'The University of Cassino and Southern Lazio offers programs in engineering, economics, law, and humanities in the historic city of Cassino.',
                'tuition_range_min': Decimal('800.00'),
                'tuition_range_max': Decimal('2000.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master', 'PhD'],
                'fields_of_study': ['Engineering', 'Economics', 'Law', 'Humanities', 'Sciences'],
            },
            {
                'name': 'University of Tuscia',
                'city': 'viterbo',
                'address': 'Via S. Maria in Gradi, 4, 01100 Viterbo VT, Italy',
                'website': 'https://www.unitus.it',
                'email': 'info@unitus.it',
                'phone': '+39 0761 3571',
                'description': 'The University of Tuscia is located in Viterbo and offers programs in agriculture, forestry, economics, and cultural heritage.',
                'tuition_range_min': Decimal('900.00'),
                'tuition_range_max': Decimal('2200.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master', 'PhD'],
                'fields_of_study': ['Agriculture', 'Forestry', 'Economics', 'Cultural Heritage', 'Sciences'],
            },
            {
                'name': 'University of Cassino - Latina Campus',
                'city': 'latina',
                'address': 'Corso della Repubblica, 79, 04100 Latina LT, Italy',
                'website': 'https://www.unicas.it',
                'email': 'latina@unicas.it',
                'phone': '+39 0773 6521',
                'description': 'The Latina campus of the University of Cassino offers programs in economics, engineering, and humanities.',
                'tuition_range_min': Decimal('800.00'),
                'tuition_range_max': Decimal('2000.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master'],
                'fields_of_study': ['Economics', 'Engineering', 'Humanities'],
            },
            {
                'name': 'University of Cassino - Frosinone Campus',
                'city': 'frosinone',
                'address': 'Via G. Di Biasio, 43, 03100 Frosinone FR, Italy',
                'website': 'https://www.unicas.it',
                'email': 'frosinone@unicas.it',
                'phone': '+39 0775 2351',
                'description': 'The Frosinone campus offers programs in engineering, economics, and law.',
                'tuition_range_min': Decimal('800.00'),
                'tuition_range_max': Decimal('2000.00'),
                'languages': ['Italian', 'English'],
                'degree_types': ['Bachelor', 'Master'],
                'fields_of_study': ['Engineering', 'Economics', 'Law'],
            },
        ]

        programs_data = {
            'Sapienza University of Rome': [
                {'name': 'Computer Engineering', 'degree_type': 'bachelor', 'field': 'Engineering', 'duration_years': 3, 'language': 'italian', 'tuition': Decimal('1500.00')},
                {'name': 'Medicine and Surgery', 'degree_type': 'bachelor', 'field': 'Medicine', 'duration_years': 6, 'language': 'italian', 'tuition': Decimal('2000.00')},
                {'name': 'International Business', 'degree_type': 'master', 'field': 'Business', 'duration_years': 2, 'language': 'english', 'tuition': Decimal('2500.00')},
            ],
            'University of Rome Tor Vergata': [
                {'name': 'Economics and Management', 'degree_type': 'bachelor', 'field': 'Business', 'duration_years': 3, 'language': 'italian', 'tuition': Decimal('1200.00')},
                {'name': 'Biomedical Engineering', 'degree_type': 'master', 'field': 'Engineering', 'duration_years': 2, 'language': 'english', 'tuition': Decimal('2200.00')},
            ],
            'Roma Tre University': [
                {'name': 'Architecture', 'degree_type': 'bachelor', 'field': 'Architecture', 'duration_years': 5, 'language': 'italian', 'tuition': Decimal('1300.00')},
                {'name': 'Law', 'degree_type': 'bachelor', 'field': 'Law', 'duration_years': 5, 'language': 'italian', 'tuition': Decimal('1400.00')},
            ],
            'LUISS Guido Carli': [
                {'name': 'Business Administration', 'degree_type': 'bachelor', 'field': 'Business', 'duration_years': 3, 'language': 'english', 'tuition': Decimal('12000.00')},
                {'name': 'International Relations', 'degree_type': 'master', 'field': 'Political Science', 'duration_years': 2, 'language': 'english', 'tuition': Decimal('14000.00')},
            ],
        }

        created_count = 0
        with transaction.atomic():
            for uni_data in universities_data:
                university, created = University.objects.get_or_create(
                    name=uni_data['name'],
                    defaults=uni_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {university.name}')

                # Add programs if they exist
                if university.name in programs_data:
                    for prog_data in programs_data[university.name]:
                        UniversityProgram.objects.get_or_create(
                            university=university,
                            name=prog_data['name'],
                            defaults=prog_data
                        )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created {created_count} new universities')
        )










