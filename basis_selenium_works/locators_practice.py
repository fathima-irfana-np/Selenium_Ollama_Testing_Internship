from selenium import webdriver
import time

driver = webdriver.Edge()
driver.get("https://www.saucedemo.com/")
driver.maximize_window()
time.sleep(2)

print("Opened SauceDemo")

driver.find_element("id", "user-name").send_keys("standard_user")
print("ID locator: username entered")
time.sleep(1)

driver.find_element("name", "password").send_keys("secret_sauce")
print("Name locator: password entered")
time.sleep(1)

driver.find_element("class name", "submit-button").click()
print("Class name locator: login button clicked")
time.sleep(3)

inputs = driver.find_elements("tag name", "input")
print("Tag name locator: number of input elements =", len(inputs))
time.sleep(2)

driver.find_element("id", "react-burger-menu-btn").click()
time.sleep(2)

driver.find_element("link text", "Logout").click()
print("Link text locator: logout clicked")
time.sleep(3)

input("Press Enter to close browser...")
driver.quit()
