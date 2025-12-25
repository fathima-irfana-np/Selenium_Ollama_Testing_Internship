from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    options = Options()
    # options.add_argument("--headless=new") # Commented out so user can see the navigation
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver

def navigate_menus(start_url, max_links=10):
    driver = setup_driver()
    visited_links = set()
    
    try:
        logger.info(f"Navigating to home page: {start_url}")
        driver.get(start_url)
        time.sleep(2) # Allow initial load
        
        # 1. Find all potential menu links
        # Heuristic: Look for links inside 'nav' tags or with 'menu' in class/id
        potential_links = []
        nav_elements = driver.find_elements(By.TAG_NAME, "nav")
        
        if not nav_elements:
            # Fallback: Look for standard header/menu classes and IDs, including w3schools specific (#topnav, .w3-bar)
            logger.info("No <nav> tag found, searching for common menu classes...")
            # Expanded selectors list
            selectors = [
                "[role='navigation']",
                "#topnav", "#mySidenav", ".w3-bar", # w3schools specific
                ".menu", ".header", "#menu", "#header", ".navbar", ".nav",
                ".main-menu", "#main-menu", ".top-bar"
            ]
            css_query = ", ".join(selectors)
            nav_elements = driver.find_elements(By.CSS_SELECTOR, css_query)

        for nav in nav_elements:
            links = nav.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    if href and text and href not in visited_links:
                        if href.startswith(start_url) or href.startswith("/"): # Keep it somewhat local/relevant
                             potential_links.append((text, href))
                except:
                    continue
        
        # Deduplicate by href
        unique_links = []
        seen_hrefs = set()
        for text, href in potential_links:
            if href not in seen_hrefs:
                unique_links.append((text, href))
                seen_hrefs.add(href)
        
        logger.info(f"Found {len(unique_links)} potential menu links.")
        
        # 2. Iterate and click
        count = 0
        for text, href in unique_links:
            if count >= max_links:
                break
            
            logger.info(f"Processing menu item {count+1}/{max_links}: '{text}' -> {href}")
            
            try:
                driver.get(href)
                
                # Check title to confirm valid load
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.info(f"Successfully loaded: {driver.title}")
                
                time.sleep(1) # Pause to simulate viewing
                count += 1
                visited_links.add(href)
                
            except TimeoutException:
                logger.warning(f"Timeout loading {href}")
            except Exception as e:
                logger.error(f"Error visiting {href}: {e}")
                
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        logger.info("Closing driver...")
        driver.quit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Menu Navigator")
    parser.add_argument("--url", type=str, required=True, help="Website to navigate")
    args = parser.parse_args()
    
    navigate_menus(args.url)