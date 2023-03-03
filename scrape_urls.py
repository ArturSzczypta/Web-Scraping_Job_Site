'''
Web scraping popular polish job site, Pracuj.pl
'''
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pprint

from bs4 import BeautifulSoup

from time import sleep

import re
from numpy import random

CUTOFF_DATE  = date_to_compare = datetime(2023, 1, 1)

# Get the directory path of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Construct the file path to the ChromeDriver executable
chromedriver_path = os.path.join(dir_path, 'chromedriver_win32', 'chromedriver')

# Create a Service object for the ChromeDriver
service = Service(chromedriver_path)

# Initialize the Chrome browser using the Service object
browser = webdriver.Chrome(service=service)

browser.get('https://it.pracuj.pl/')

# Wait for the page to load completely
sleep(random.uniform(5, 10))


# Find all the location buttons
location_buttons = browser.find_elements(By.CSS_SELECTOR, 'div[data-test="offer-locations-button"]')

if not location_buttons:
    print("No location buttons found")

# Click on each viewBox object
for loc_button in location_buttons:
    try:

        # Scroll to the button to bring it into view
        browser.execute_script("arguments[0].scrollIntoView();", loc_button)
        
        # Wait for the button to become clickable
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-test="offer-locations-button"]')))
        
        # Click on the button
        loc_button.click()

        # Scroll the page down to bring the details into view
        browser.execute_script("window.scrollBy(0, 300);")

        # Wait for the job offer details to load
        sleep(random.uniform(2, 4))
    except:
            print("Could not click on button")

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

#
date_str = job_offer.find('span', {'class': 'offer-actions__date'}).text.strip()
job_date = datetime.strptime(date_str, 'opublikowana: %B %d, %Y')


# Find all the links starting with 'http'
http_links = soup.find_all('a', href=re.compile('^https://www.pracuj.pl/praca/'))

# Print all the http links
print('links, total: ', len(http_links))
for link in http_links:
    print(link.get('href'))
browser.quit()