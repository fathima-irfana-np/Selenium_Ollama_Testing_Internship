from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import logging
import time

class WebScraper:
    def __init__(self, headless=False):
        self.logger = logging.getLogger(__name__)
        self.driver = self._setup_driver(headless)

    def _setup_driver(self, headless):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        # Suppress logging
        options.add_argument("--log-level=3")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30) # 30 seconds page load timeout
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def get_page_content(self, url):
        """
        Navigates to the URL and extracts text content.
        Returns tuple (text_content, soup_object) or (None, None) on failure.
        """
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for body to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give a small buffer for dynamic content (optional but helpful)
            time.sleep(1) 

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove scripts, styles, and navigation to reduce noise
            for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                script.decompose()

            # Smart extraction: Limit to first 2 sections (roughly)
            # Strategy: Collect text from paragraphs and headers until we see the 3rd h2 or hit a length limit.
            content_parts = []
            header_count = 0
            char_count = 0
            MAX_CHARS = 15000 # Hard cap to prevent memory issues before summarization truncates it
            
            # Find the main content area if possible (Wikipedia specific but good generic fallback)
            main_content = soup.find(id="mw-content-text") or soup.find("main") or soup.find("article") or soup.body
            
            if main_content:
                # Iterate over direct children or important tags
                for element in main_content.find_all(['h1', 'h2', 'h3', 'p'], recursive=True):
                    text_chunk = element.get_text(separator=' ', strip=True)
                    
                    # Stop if we encouter a "Stop Keyword" in a header
                    if element.name in ['h1', 'h2', 'h3']:
                        header_text_lower = text_chunk.lower()
                        stop_keywords = ["exercise", "problem", "quiz", "question", "reference", "bibliography", "external link"]
                        if any(keyword in header_text_lower for keyword in stop_keywords):
                            self.logger.info(f"Skipping section: {text_chunk}")
                            continue # Skip this header and potentially subsequent ps if we were smarter, but for now just skip strict sections if we could. 
                            # Actually, a better approach for simple linear scrape:
                            # If we hit an 'Exercise' header, we might want to stop COMPLETELY if it's at the end, 
                            # or just skip this element. 
                            # Given the user's issue, these usually appear at the end. Let's break? 
                            # User said "The article includes... discussion questions at the end." -> BREAK is safer.
                            self.logger.info("Hit pedagogical or footer section. Stopping extraction.")
                            break

                        header_count += 1
                    
                    if text_chunk:
                        content_parts.append(text_chunk)
                        char_count += len(text_chunk)
                    
                    # Stop if we have seen enough sections (Intro + 2 sections = ~3 headers usually)
                    # or if we have enough text.
                    if header_count >= 3 or char_count > MAX_CHARS:
                        self.logger.info(f"Truncating content at {header_count} headers / {char_count} chars.")
                        break
            
            if not content_parts:
                 # Fallback to standard get_text if smart extraction failed
                 text = soup.get_text(separator=' ', strip=True)
            else:
                text = " ".join(content_parts)

            return text, soup
            
        except TimeoutException:
            self.logger.warning(f"Timeout loading page: {url}")
            return None, None
        except WebDriverException as e:
            self.logger.error(f"WebDriver error on {url}: {e}")
            return None, None
        except Exception as e:
            self.logger.error(f"Unexpected error on {url}: {e}")
            return None, None

    def get_links(self, soup, base_url):
        """
        Extracts all valid hrefs from the soup object.
        """
        if not soup:
            return []
            
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Basic filtering
            if href.startswith('http'):
                links.append(href)
            elif href.startswith('/'):
                # Handle relative URLs
                from urllib.parse import urljoin
                full_url = urljoin(base_url, href)
                links.append(full_url)
                
        # Remove duplicates
        return list(set(links))

    def close(self):
        if self.driver:
            self.driver.quit()
