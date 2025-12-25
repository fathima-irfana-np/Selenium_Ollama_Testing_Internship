import argparse
import json
import logging
import os
import time
from urllib.parse import urlparse

from ollama_client import OllamaClient
from scraper import WebScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

MAX_PAGES = 10

def is_valid_url(url, base_domain):
    """
    Checks if a URL is valid and belongs to the same domain (to prevent crawling the entire web).
    """
    try:
        parsed_url = urlparse(url)
        # Ensure it's http or https
        if parsed_url.scheme not in ('http', 'https'):
            return False
            
        # Optional: Strict domain constraint.
        # For this task, "recursively navigates a website" usually implies staying on that site.
        if base_domain not in parsed_url.netloc:
             return False
             
        return True
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Recursive Selenium Web Scraper with Ollama Summarization")
    parser.add_argument("--url", type=str, required=True, help="Base URL to start scraping from")
    parser.add_argument("--model", type=str, default="mistral", help="Ollama model to use (default: mistral)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--depth", type=int, default=10, help="Max unique pages to visit (default: 10)")
    
    args = parser.parse_args()
    
    start_url = args.url
    base_domain = urlparse(start_url).netloc
    
    # Initialize components
    ollama = OllamaClient(model=args.model)
    if not ollama.check_connection():
        logger.critical("Ollama is not accessible. Please ensure 'ollama serve' is running.")
        return

    scraper = WebScraper(headless=args.headless)
    
    visited_urls = set()
    urls_to_visit = [start_url]
    results = {}
    
    logger.info("Starting scrape process...")
    
    try:
        while urls_to_visit and len(visited_urls) < args.depth:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            logger.info(f"Processing ({len(visited_urls)}/{args.depth}): {current_url}")
            
            # Scrape content
            text_content, soup = scraper.get_page_content(current_url)
            
            if not text_content:
                logger.warning(f"No content found for {current_url}")
                results[current_url] = "Error: Could not extract content."
                continue
                
            # Summarize content
            logger.info(f"Summarizing content for {current_url}...")
            summary = ollama.generate_summary(text_content)
            results[current_url] = summary
            logger.info("Summary generated.")
            
            # Find new links
            if soup:
                links = scraper.get_links(soup, current_url)
                for link in links:
                    if link not in visited_urls and is_valid_url(link, base_domain):
                        urls_to_visit.append(link)
    
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user.")
    except Exception as e:
        logger.error(f"Critical error in main loop: {e}")
    finally:
        scraper.close()
        
        # Save results
        output_file = "summary_report.json"
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=4)

        # Save results as TXT
        txt_output_file = "summary_report.txt"
        with open(txt_output_file, "w", encoding='utf-8') as f:
             for url, summary in results.items():
                f.write(f"URL: {url}\n")
                f.write(f"SUMMARY:\n{summary}\n")
                f.write("-" * 80 + "\n\n")
            
        logger.info(f"Scraping complete. Visited {len(visited_urls)} pages.")
        logger.info(f"Results saved to {output_file}")
        
        # Print a preview
        print("\n--- Scrape Summary Preview ---")
        for i, (url, summary) in enumerate(list(results.items())[:3]):
            print(f"\nURL: {url}")
            print(f"Summary: {summary[:150]}...")

if __name__ == "__main__":
    main()
