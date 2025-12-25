from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # Added import
import time

# ---------------- CONFIG ----------------

START_URL = "https://www.w3schools.com/"
WAIT_TIME = 5
MAX_LINKS = 8

# ---------------- DRIVER SETUP ----------------

# Use WebDriver Manager to automatically handle ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, WAIT_TIME)

# ---------------- FUNCTION 1 ----------------
# Try to open menu (hamburger) if it exists

def open_menu(driver):
    menu_selectors = [
        "button[aria-label*='menu']",
        "button[class*='menu']",
        "div[class*='menu']",
        "a[class*='menu']"
    ]

    for selector in menu_selectors:
        try:
            menu_button = driver.find_element(By.CSS_SELECTOR, selector)
            if menu_button.is_displayed():
                menu_button.click()
                time.sleep(1)
                break
        except:
            pass   # ignore if selector not found

# ---------------- FUNCTION 2 ----------------
# Collect navigation links

def get_nav_links(driver, domain):
    links = driver.find_elements(By.TAG_NAME, "a")
    nav_links = []

    for link in links:
        text = link.text.strip()
        href = link.get_attribute("href")

        if text and href and domain in href:
            nav_links.append((text, href))

        if len(nav_links) == MAX_LINKS:
            break

    return nav_links

# ---------------- MAIN LOGIC ----------------

try:
    # Step 1: Open home page
    driver.get(START_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Step 2: Open menu if present
    open_menu(driver)

    # Step 3: Extract domain
    domain = START_URL.replace("https://", "").replace("http://", "")

    # Step 4: Collect navigation links
    nav_links = get_nav_links(driver, domain)

    print("Navigation options found:")
    for text, _ in nav_links:
        print("-", text)

    # Step 5: Visit each nav link
    for text, url in nav_links:
        print(f"\n➡️ Opening: {text}")
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        time.sleep(2)   # simulate some work

        print("⬅️ Returning to home")
        driver.get(START_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

finally:
    driver.quit()