#scrape_toolsvilla.py

from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from database.db_connection import get_connection
from utils.brand_category import get_brand_name,get_category_id, clean_price
from utils.db_helpers import (
    save_product,
    get_or_create_brand
)
from datetime import datetime
from utils.scrape_logger import log_scrape


PLATFORM_ID = 3

class Command(BaseCommand):
    help = 'Scrape power tools from Toolsvilla'

    def handle(self, *args, **kwargs):
        conn = get_connection()
        cursor = conn.cursor()

        start_time = datetime.now()

        status = "FAILED"
        notes = None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                })

                page.goto("https://www.toolsvilla.com/category/workshop",wait_until="domcontentloaded",timeout=60000) 

                # Wait for Angular to render product cards
                page.wait_for_selector("mat-card.product-item", timeout=30000)
                page.wait_for_timeout(3000)

                # Scroll to load more lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                page.wait_for_timeout(2000)

                items = page.locator("mat-card.product-item")
                self.stdout.write(f"Products found: {items.count()}")

                for i in range(min(20, items.count())):
                    item = items.nth(i)

                    # Name
                    name_el = item.locator("a.title.newTitle").first
                    if not name_el.count():
                        continue
                    name = name_el.inner_text().strip()
                    if not name:
                        continue

                    # Price
                    price_el = item.locator("span.new-price").first
                    if not price_el.count():
                        self.stdout.write(f"No price for: {name}")
                        continue
                    price = clean_price(price_el.inner_text())
                    if price is None:
                        continue

                    # Product URL
                    link_el = item.locator("a.image-link").first
                    product_url = None
                    if link_el.count():
                        href = link_el.get_attribute("href")
                        if href:
                            product_url = f"https://www.toolsvilla.com{href}"

                    
                    category_id = get_category_id(name)

                    brand_name = get_brand_name(name)

                    brand_id = get_or_create_brand(
                        cursor,
                        brand_name
                    )

                    save_product(cursor, name, price, brand_id, category_id, PLATFORM_ID, product_url)
                    self.stdout.write(f"  URL: {product_url}")

                browser.close()
                conn.commit()
                self.stdout.write(self.style.SUCCESS("Toolsvilla scrape complete!"))
                status = "SUCCESS"

        except Exception as e:
            conn.rollback()
            notes = str(e)
            self.stdout.write(self.style.ERROR(f"Toolsvilla error: {e}"))

        finally:

            end_time = datetime.now()

            try:

                log_scrape(
                    cursor,
                    "Toolsvilla",
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