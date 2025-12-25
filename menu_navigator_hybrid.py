from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from urllib.parse import urljoin, urlparse
import time
import logging

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------- DRIVER SETUP ----------------

def setup_driver():
    options = Options()
    # options.add_argument("--headless=new")  # enable if needed
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver

# ---------------- MAIN LOGIC ----------------

def navigate_menus(start_url, max_links=10):
    driver = setup_driver()
    visited = set()

    try:
        logger.info(f"Opening: {start_url}")
        driver.get(start_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        parsed = urlparse(start_url)
        domain = parsed.netloc

        collected_links = []

        # ==================================================
        # STEP 1: MENU-BASED EXTRACTION (YOUR LOGIC)
        # ==================================================

        logger.info("Trying menu-based navigation detection")

        nav_elements = driver.find_elements(By.TAG_NAME, "nav")

        if not nav_elements:
            selectors = [
                "[role='navigation']",
                "#topnav", "#mySidenav", ".w3-bar",
                ".menu", ".navbar", ".nav",
                ".main-menu", "#main-menu", ".top-bar"
            ]
            nav_elements = driver.find_elements(
                By.CSS_SELECTOR, ", ".join(selectors)
            )

        for nav in nav_elements:
            anchors = nav.find_elements(By.TAG_NAME, "a")
            for a in anchors:
                text = a.text.strip()
                href = a.get_attribute("href")

                if not text or not href:
                    continue
                if href == "#" or href.startswith("javascript"):
                    continue

                full_url = urljoin(start_url, href)

                if domain in full_url and full_url not in visited:
                    collected_links.append((text, full_url))

        # ==================================================
        # STEP 2: FALLBACK — GLOBAL <a> SCAN (FRIEND LOGIC)
        # ==================================================

        if not collected_links:
            logger.info("Menu detection failed — using global link scan")

            all_links = driver.find_elements(By.TAG_NAME, "a")
            for a in all_links:
                text = a.text.strip()
                href = a.get_attribute("href")

                if not text or not href:
                    continue
                if href == "#" or href.startswith("javascript"):
                    continue

                full_url = urljoin(start_url, href)

                if domain in full_url and full_url not in visited:
                    collected_links.append((text, full_url))

                if len(collected_links) >= max_links:
                    break

        # ==================================================
        # STEP 3: DEDUPLICATION
        # ==================================================

        seen = set()
        final_links = []
        for text, url in collected_links:
            if url not in seen:
                final_links.append((text, url))
                seen.add(url)

        logger.info(f"Total navigation links found: {len(final_links)}")

        # ==================================================
        # STEP 4: VISIT LINKS
        # ==================================================

        for idx, (text, url) in enumerate(final_links[:max_links], start=1):
            logger.info(f"[{idx}] Visiting: {text} -> {url}")

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                visited.add(url)
                time.sleep(1)

            except TimeoutException:
                logger.warning(f"Timeout loading: {url}")
            except Exception as e:
                logger.warning(f"Failed to load {url}: {e}")

    finally:
        logger.info("Closing browser")
        driver.quit()

# ---------------- ENTRY POINT ----------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid Menu Navigator")
    parser.add_argument("--url", required=True, help="Start URL")
    parser.add_argument("--max", type=int, default=10, help="Max links to visit")

    args = parser.parse_args()

    navigate_menus(args.url, args.max)
