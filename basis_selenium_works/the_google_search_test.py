
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

QUERY = "wikipedia"
WAIT_TIME = 5

driver = webdriver.Edge()
wait = WebDriverWait(driver, WAIT_TIME)

try:
    driver.get("https://www.google.com")

    search_box = wait.until(
        EC.presence_of_element_located((By.NAME, "q"))
    )

    search_box.send_keys(QUERY + Keys.ENTER)

    link = wait.until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Wikipedia"))
    )
    link.click()

finally:
    driver.quit()
