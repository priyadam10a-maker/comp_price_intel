#scrape_flipkart.py

from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from database.db_connection import get_connection
from utils.brand_category import (
    get_brand_name,
    get_category_id,
    clean_price
)

from utils.db_helpers import (
    save_product,
    get_or_create_brand
)

from datetime import datetime
from utils.scrape_logger import log_scrape

PLATFORM_ID = 2

class Command(BaseCommand):
    help = 'Scrape power tools from Flipkart'

    def handle(self, *args, **kwargs):
        self.stdout.write("DEBUG: NEW FLIPKART SCRAPER RUNNING")

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

                page.goto(
                    "https://www.flipkart.com/search?q=ingco+bosch+makita+power+tools&marketplace=FLIPKART",
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page.wait_for_timeout(4000)

                # Close login popup if it appears
                try:
                    close_btn = page.locator('button._2KpZ6l, button.VkIAEw, [class*="close"]').first
                    if close_btn.is_visible():
                        close_btn.click()
                        page.wait_for_timeout(1000)
                except:
                    pass

                # Scroll to load products
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                page.wait_for_timeout(2000)

                # Try multiple known Flipkart product card selectors
                # These change — inspect the page if count is 0
                selectors_to_try = [
                    'div[data-id]',
                    'div._1AtVbE',
                    'div._13oc-S',
                    'div.tUxRFH',
                    'div.slAVV4',
                ]

                items = None
                for selector in selectors_to_try:
                    candidate = page.locator(selector)
                    count = candidate.count()
                    self.stdout.write(f"Trying selector '{selector}': {count} found")
                    if count > 2:
                        items = candidate
                        break

                if items is None or items.count() == 0:
                    self.stdout.write(self.style.ERROR(
                        "No products found. Open browser and inspect Flipkart product card class name."
                    ))
                    browser.close()
                    return

                self.stdout.write(f"Using {items.count()} product cards")

                for i in range(min(15, items.count())):
                    item = items.nth(i)

                    # Try multiple name selectors
                    name = None
                    for name_sel in [
                        "a.pIpigb",
                        "div.KzDlHZ",
                        "a.s1Q9rs",
                        "a[title]"
                    ]:
                        el = item.locator(name_sel).first
                        if el.count() and el.is_visible():
                            name = el.inner_text().strip()
                            break

                    # Try multiple price selectors
                    price = None

                    for price_sel in [
                        "div.hZ3P6w",
                        "div.QiMO5r div.hZ3P6w"
                    ]:
                        try:
                            el = item.locator(price_sel).first

                            if el.count():
                                raw_price = el.inner_text().strip()
                                price = clean_price(raw_price)

                                if price:
                                    break

                        except:
                            pass

                    #URL extractor
                    product_url = None

                    try:
                        link_el = item.locator("a.pIpigb").first

                        if link_el.count():
                            href = link_el.get_attribute("href")

                            if href:
                                product_url = (
                                    "https://www.flipkart.com"
                                    + href
                                )

                    except Exception:
                        pass

                    if not name:
                        print("No name found")
                        continue
                    
                    if not price:
                        print(f"No price found for: {name}")
                        continue

                    category_id = get_category_id(name)

                    brand_name = get_brand_name(name)

                    brand_id = get_or_create_brand(
                        cursor,
                        brand_name
                    )

                    print(f"Name: {name}")
                    print(f"Price: {price}")
                    print(f"Brand: {brand_name}")
                    print("URL:", product_url)
                    print("-" * 50)

                    save_product(
                        cursor,
                        name,
                        price,
                        brand_id,
                        category_id,
                        PLATFORM_ID,
                        product_url
                    )

                browser.close()
                conn.commit()
                status = "SUCCESS"
                self.stdout.write(self.style.SUCCESS("Flipkart scrape complete!"))

        except Exception as e:
            conn.rollback()
            notes = str(e)
            self.stdout.write(self.style.ERROR(f"Flipkart error: {e}"))

        finally:

            end_time = datetime.now()

            try:

                log_scrape(
                    cursor,
                    "Flipkart",
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