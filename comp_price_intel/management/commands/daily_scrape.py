from django.core.management.base import BaseCommand
from comp_price_intel.models import Product
from comp_price_intel.views import run_real_scrape

class Command(BaseCommand):
    help = 'Runs the automated daily scrape for all products'

    def handle(self, *args, **options):
        products = Product.objects.all()
        self.stdout.write(f"Starting daily scrape for {products.count()} products...")
        
        for product in products:
            self.stdout.write(f"Scraping Product: {product.product_name} (ID: {product.product_id})")
            try:
                run_real_scrape(product.product_id)
                self.stdout.write(self.style.SUCCESS(f"Successfully scraped {product.product_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error scraping {product.product_name}: {str(e)}"))
                
        self.stdout.write(self.style.SUCCESS("Daily scrape completed!"))
