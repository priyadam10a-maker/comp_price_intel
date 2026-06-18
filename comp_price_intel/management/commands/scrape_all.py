#scrape_all.py

from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run all scrapers sequentially'

    def handle(self, *args, **kwargs):
        scrapers = [
            'scrape_industrybuying',
            'scrape_amazon',
            'scrape_flipkart',
            'scrape_toolsvilla',
        ]
        for scraper in scrapers:
            self.stdout.write(f"\n{'='*40}")
            self.stdout.write(f"Running: {scraper}")
            self.stdout.write('='*40)
            try:
                call_command(scraper)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{scraper} failed: {e}"))