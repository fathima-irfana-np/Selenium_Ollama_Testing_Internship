from selenium import webdriver
import time
driver = webdriver.Edge()

driver.get("https://www.bookmyshow.com/")
# driver.get("https://www.southindianbank.bank.in/")
# driver.get("https://www.google.com/search?q=test")
print("Waiting for page to load and manual interaction...")
time.sleep(15)

# Get current URL
current_url = driver.current_url
print("Current URL:", current_url)
print(driver.title)
if "southindianbank.bank.in" in current_url:
    print("✅ Successfully opened South Indian Bank website.")
else:
    print("❌ Navigation issue or redirection occurred.")

input("Press Enter to close browser...")
driver.quit()
