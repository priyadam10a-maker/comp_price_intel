#scrape_industrybuying.py

from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from database.db_connection import get_connection
from utils.brand_category import  get_brand_name, get_category_id, clean_price
from utils.db_helpers import get_or_create_brand, save_product

from datetime import datetime
from utils.scrape_logger import log_scrape

PLATFORM_ID = 4

class Command(BaseCommand):
    help = 'Scrape power tools from Industrybuying'

    def handle(self, *args, **kwargs):
        conn = get_connection()
        cursor = conn.cursor()
        browser = None

        start_time = datetime.now()

        status = "FAILED"
        notes = None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto("https://www.industrybuying.com/power-tools-641/",wait_until="domcontentloaded",timeout=60000)
                page.wait_for_timeout(5000)

                rows = page.locator("table tbody tr")
                self.stdout.write(f"Rows found: {rows.count()}")

                for i in range(min(10, rows.count())):
                    row  = rows.nth(i)
                    cols = row.locator("td")

                    if cols.count() < 2:
                        continue

                    name  = cols.nth(0).inner_text().strip()
                    price = clean_price(cols.nth(1).inner_text())

                    if price is None:
                        self.stdout.write(f"Skipping invalid price for: {name}")
                        continue

                    product_url = None

                    brand_name = get_brand_name(name)

                    brand_id = get_or_create_brand(
                        cursor,
                        brand_name
                    )
                    
                    category_id = get_category_id(name)

                    #if brand_id is None:
                     #   self.stdout.write(f"Skipping unknown brand: {name}")
                      #  continue
                    

                    save_product(cursor, name, price, brand_id, category_id, PLATFORM_ID, product_url)

                browser.close()   # ← moved here, inside the with block
                conn.commit()
                status = "SUCCESS"
                self.stdout.write(self.style.SUCCESS("Industrybuying scrape complete!"))

        except Exception as e:
            conn.rollback()
            notes = str(e)
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

        finally:

            end_time = datetime.now()

            try:

                log_scrape(
                    cursor,
                    "IndustryBuying",
                    start_time,
                    end_time,
                    status,
                    notes
                )

                conn.commit()

            except Exception as log_error:

                self.stdout.write(
                    self.style.ERROR(
                        f"Logging error: {log_error}"
                    )
                )

            conn.close()   