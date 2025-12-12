"""
Management command to update the Site domain for email confirmation URLs.
Run this after deployment to ensure email links use the correct domain.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Update the Site domain to match ALLOWED_HOSTS for email confirmation URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain to set (e.g., your-app.up.railway.app). If not provided, uses first non-wildcard from ALLOWED_HOSTS',
        )

    def handle(self, *args, **options):
        domain = options.get('domain')
        
        if not domain:
            # Get the primary domain from ALLOWED_HOSTS (first non-wildcard domain)
            for host in settings.ALLOWED_HOSTS:
                if not host.startswith('.') and host not in ['healthcheck.railway.app']:
                    domain = host
                    break
        
        if not domain:
            self.stdout.write(
                self.style.ERROR(
                    'Could not determine domain. Please provide --domain or set ALLOWED_HOSTS.'
                )
            )
            return
        
        try:
            site = Site.objects.get(pk=settings.SITE_ID)
            old_domain = site.domain
            site.domain = domain
            site.name = 'ASCAI Lazio'
            site.save(update_fields=['domain', 'name'])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated Site domain from "{old_domain}" to "{domain}"'
                )
            )
            self.stdout.write(
                f'Email confirmation URLs will now use: https://{domain}'
            )
        except Site.DoesNotExist:
            # Create the site if it doesn't exist
            site = Site.objects.create(
                pk=settings.SITE_ID,
                domain=domain,
                name='ASCAI Lazio'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created Site with domain: {domain}'
                )
            )





















