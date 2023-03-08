'''
Web scraping popular polish job site, Pracuj.pl
'''
import os
from time import sleep
import datetime
import re
from numpy import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_uls(webpage):
    ''' Scrapes urls from sigle page'''
    # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the file path to the ChromeDriver executable
    chromedriver_path = os.path.join(dir_path,
        'chromedriver_win32', 'chromedriver')

    # Create a Service object for the ChromeDriver
    service = Service(chromedriver_path)

    # Initialize the Chrome browser using the Service object
    browser = webdriver.Chrome(service=service)
    browser.get(webpage)

    # Wait for the page to load completelye
    sleep(random.uniform(5, 10))

    # Accept terms of service, if they appear
    try:
        accept_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                '//button[@data-test="button-accept-all-in-general"]')))
        accept_button.click()
    except:
        print(f'{webpage} - Could not find or click accept button')

    # Wait for the page to load completelye
    sleep(random.uniform(5, 10))

    # Find all the location buttons
    location_buttons = browser.find_elements(By.CSS_SELECTOR,
        'div[data-test="offer-locations-button"]')
    if not location_buttons:
        print(f'{webpage} - No location buttons found')

    # Click on each viewBox object
    for loc_button in location_buttons:
        try:
            # Scroll to the button to bring it into view
            browser.execute_script('arguments[0].scrollIntoView();',
                loc_button)

            # Wait for the button to become clickable
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[data-test="offer-locations-button"]')))

            # Click on the button
            loc_button.click()

            # Scroll the page down to bring the details into view
            browser.execute_script('window.scrollBy(0, 300);')

            # Wait for the job offer details to load
            sleep(random.uniform(2, 4))
        except:
            print(f'{webpage} - Could not click on button')

    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find all the links starting with 'http'
    http_elements = soup.find_all('a',
        href=re.compile('^https://www.pracuj.pl/praca/'))

    http_links = [x.get('href') for x in http_elements]

    #Find all unique dates
    date_elements = soup.find_all('div',
        {'class': 'JobOfferstyles__FooterText-sc-1rq6ue2-22'})

    def extract_date_from_element(element):
        ''' Extracts date from FooterText class '''
        date_text = element.text.strip().split(': ')[-1]
        return date_text

    unique_dates = set()
    for element in date_elements:
        date_str = extract_date_from_element(element)
        date_obj = datetime.datetime.strptime(date_str, '%d %B %Y').date()
        unique_dates.add(date_obj)

    browser.quit()
    return http_links,unique_dates

def main(webpage):
    '''
    This is the main function of the script.
            
    It scrapes job offer links and dates on site 

    Note: This function is only executed when the script is run directly,
    not when it is imported as a module.
    '''
    new_http_links,unique_dates = scrape_uls(webpage)

    print(f'Links: {len(new_http_links)}\n')
    for link in new_http_links:
        print(link)
    print(f'Dates: {unique_dates}')

if __name__ == '__main__':
    main('https://it.pracuj.pl/')
