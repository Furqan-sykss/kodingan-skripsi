from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
CHROMEDRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
options = Options()
options.add_argument('--headless')  # opsional
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.google.com")
print(driver.title)
driver.quit()