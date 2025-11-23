"""
Property scraper for Zoopla listings

This module contains the PropertyScraper class which handles web scraping
of property listings from Zoopla using Playwright.
"""

import time
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from config import (
    HEADLESS, BASE_URL, SELECTORS, VIEWPORT, USER_AGENT,
    BROWSER_ARGS, BASE_WAIT_DURATION, TIMEOUT_SHORT,
    MAX_PAGES_PER_AREA, MAX_LISTINGS_PER_AREA
)
from typing import List
from models import ScrapedItem


class PropertyScraper:
    """
    Web scraper for property listings

    This class handles the scraping of property listings from Zoopla,
    including pagination, cookie acceptance, and detailed property extraction.
    """

    def __init__(self, headless: bool = HEADLESS):
        """
        Initialize the PropertyScraper

        Args:
            headless: Whether to run browser in headless mode (default: from config)
        """
        self.headless = headless
        self.browser = None

    def _create_page(self):
        """
        Create a new browser page with anti-detection settings

        Returns:
            Page: Playwright page object
        """
        page = self.browser.new_page(viewport=VIEWPORT)
        page.set_extra_http_headers({'User-Agent': USER_AGENT})

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        return page

    def _accept_cookies(self, page):
        """
        Accept cookie consent if present

        Args:
            page: Playwright page object
        """
        try:
            page.wait_for_selector(SELECTORS['cookie_accept'], timeout=3000)
            page.click(SELECTORS['cookie_accept'])
            time.sleep(BASE_WAIT_DURATION)
        except:
            pass

    def _search_location(self, page, location: str):
        """
        Navigate to base URL and search for a location

        Args:
            page: Playwright page object
            location: Location string to search for
        """
        page.goto(BASE_URL, wait_until="domcontentloaded")

        self._accept_cookies(page)

        page.wait_for_selector(SELECTORS['search_input'], timeout=TIMEOUT_SHORT)
        page.fill(SELECTORS['search_input'], location)

        page.keyboard.press("Enter")
        time.sleep(BASE_WAIT_DURATION * 2)

    def _collect_listing_urls(self, page) -> List[str]:
        """
        Collect all listing URLs from paginated search results

        Args:
            page: Playwright page object

        Returns:
            List of listing URLs
        """
        all_urls = []
        current_page = 1

        while True:
            page_urls = []

            try:
                page.wait_for_selector(SELECTORS['listing_card'], timeout=TIMEOUT_SHORT)
            except:
                print(f"  No listings found on page {current_page}")
                break

            listings = page.locator(SELECTORS['listing_card']).all()

            for listing in listings:
                link = listing.locator("a").first
                if link.count() > 0:
                    href = link.get_attribute("href")
                    if href:
                        if href.startswith("/"):
                            full_url = f"{BASE_URL}{href}"
                        else:
                            full_url = href
                        page_urls.append(full_url)

            print(f"  Page {current_page}: Found {len(page_urls)} listings")
            all_urls.extend(page_urls)

            if MAX_LISTINGS_PER_AREA and len(all_urls) >= MAX_LISTINGS_PER_AREA:
                print(f"  Reached max listings limit ({MAX_LISTINGS_PER_AREA})")
                break

            if MAX_PAGES_PER_AREA and current_page >= MAX_PAGES_PER_AREA:
                print(f"  Reached max pages limit ({MAX_PAGES_PER_AREA})")
                break

            try:
                pagination = page.locator(SELECTORS['pagination'])
                pagination_links = pagination.all()

                next_page_url = None
                for link in pagination_links:
                    href = link.get_attribute("href")
                    text = link.text_content()

                    if href and (f"pn={current_page + 1}" in href or "next" in text.lower()):
                        # Construct full URL
                        if href.startswith("/"):
                            next_page_url = f"{BASE_URL}{href}"
                        else:
                            next_page_url = href
                        break

                if next_page_url:
                    page.goto(next_page_url, wait_until="domcontentloaded")
                    time.sleep(BASE_WAIT_DURATION * 2)
                    current_page += 1
                else:
                    print(f"  No more pages found")
                    break
            except Exception as e:
                print(f"  Error navigating to next page: {e}")
                break

        return all_urls

    def _scrape_detail_page(self, page, soup: BeautifulSoup, url: str, location: str) -> ScrapedItem:
        """
        Extract property details from a detail page

        Args:
            page: Playwright page object
            soup: BeautifulSoup object of the page HTML
            url: URL of the property
            location: Search location

        Returns:
            ScrapedItem with extracted data
        """
        scraped_item = ScrapedItem()
        scraped_item.url = url
        scraped_item.search_location = location
        scraped_item.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        address_element = soup.select_one(SELECTORS['address'])
        if address_element:
            scraped_item.address = address_element.get_text(strip=True)

        price_element = soup.select_one(SELECTORS['price'])
        if price_element:
            price_text = price_element.get_text(strip=True)
            price_clean = ''.join(filter(str.isdigit, price_text))
            if price_clean:
                scraped_item.price = int(price_clean)

        title_element = soup.select_one(SELECTORS['title'])
        if title_element:
            scraped_item.slur = title_element.get_text(strip=True)

        desc_element = soup.select_one(SELECTORS['description'])
        if desc_element:
            scraped_item.description = desc_element.get_text(strip=True)

        room_elements = soup.select(SELECTORS['room_details'])
        for room_element in room_elements:
            room_text = room_element.get_text(strip=True).lower()
            # Extract number from text
            number = ''.join(filter(str.isdigit, room_text))
            if number:
                if 'bed' in room_text:
                    scraped_item.beds = int(number)
                elif 'bath' in room_text:
                    scraped_item.baths = int(number)
                elif 'reception' in room_text:
                    scraped_item.receptions = int(number)

        epc_element = soup.select_one(SELECTORS['epc_rating'])
        if epc_element:
            scraped_item.epc_rating = epc_element.get_text(strip=True)

        image_element = soup.select_one(SELECTORS['image'])
        if image_element:
            image_src = image_element.get('src', '')
            scraped_item.image = image_src

        tag_elements = soup.select(SELECTORS['tags'])
        for tag_element in tag_elements:
            tag_text = tag_element.get_text(strip=True)
            if tag_text:
                scraped_item.tags.append(tag_text)

        if scraped_item.address:
            import re
            postcode_pattern = r'[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}'
            match = re.search(postcode_pattern, scraped_item.address.upper())
            if match:
                scraped_item.zip_code = match.group(0)

        scraped_item.id = hashlib.md5(url.encode()).hexdigest()

        return scraped_item

    def _scrape_listings(self, page, listing_urls: List[str], location: str) -> List[ScrapedItem]:
        """
        Scrape details from multiple listing URLs

        Args:
            page: Playwright page object
            listing_urls: List of URLs to scrape
            location: Search location

        Returns:
            List of ScrapedItem objects
        """
        scraped_items = []

        for index, listing_url in enumerate(listing_urls, 1):
            try:
                print(f"    Scraping listing {index}/{len(listing_urls)}: {listing_url}")

                page.goto(listing_url, wait_until="domcontentloaded")
                time.sleep(BASE_WAIT_DURATION)

                detail_html = page.inner_html("body")
                detail_soup = BeautifulSoup(detail_html, "html.parser")

                scraped_item = self._scrape_detail_page(page, detail_soup, listing_url, location)
                scraped_items.append(scraped_item)

            except Exception as e:
                print(f"    Error scraping {listing_url}: {e}")
                continue

        return scraped_items

    def scrape_area(self, location: str) -> List[ScrapedItem]:
        """
        Scrape all listings for a single area

        Args:
            location: Location to search for

        Returns:
            List of ScrapedItem objects
        """
        print(f"\n{'='*60}")
        print(f"Scraping area: {location}")
        print(f"{'='*60}\n")

        with sync_playwright() as pw:
            self.browser = pw.chromium.launch(
                headless=self.headless,
                args=BROWSER_ARGS
            )

            page = self._create_page()

            print(f"Searching for location: {location}")
            self._search_location(page, location)

            print(f"Collecting listing URLs...")
            urls = self._collect_listing_urls(page)
            print(f"Found {len(urls)} total listings\n")

            if urls:
                print(f"Scraping listing details...")
                scraped_items = self._scrape_listings(page, urls, location)
                print(f"Successfully scraped {len(scraped_items)} listings")
            else:
                scraped_items = []
                print(f"No listings to scrape")

            self.browser.close()

            return scraped_items

    def scrape_all_areas(self, locations: List[str]) -> List[ScrapedItem]:
        """
        Scrape all listings for multiple areas

        Args:
            locations: List of locations to search for

        Returns:
            List of all ScrapedItem objects
        """
        all_items = []

        for index, location in enumerate(locations, 1):
            print(f"\nLocation {index}/{len(locations)}")
            items = self.scrape_area(location)
            all_items.extend(items)

            if index < len(locations):
                time.sleep(BASE_WAIT_DURATION * 2)

        return all_items