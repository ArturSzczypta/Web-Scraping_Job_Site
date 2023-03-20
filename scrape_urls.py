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

def scrape_one_page(webpage):
    ''' Scrapes urls and dates from single page'''
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
    http_links = set(http_links)

    #Find all unique dates
    date_elements = soup.find_all('div',
        {'class': 'JobOfferstyles__FooterText-sc-1rq6ue2-22'})

    unique_dates = set()
    for element in date_elements:
        date_str = element.text.strip().split(': ')[-1]
        date_obj = datetime.datetime.strptime(date_str, '%d %B %Y').date()
        unique_dates.add(date_obj)

    browser.quit()
    return http_links,unique_dates

def scrape_since_last():
    ''' Scrapes urls all pages since last time'''
    last_date = None
    with open('last_date.log', 'r',encoding='UTF-8') as date_file:
        line = date_file.readline()
        last_date = datetime.datetime.strptime(line, '%Y-%m-%d').date()

    # 'last_date - one_day' gives overlam in the search
    last_date = last_date - datetime.timedelta(days=1)

    webpage = 'https://it.pracuj.pl/'
    http_links, unique_dates = scrape_uls(webpage)

    # check if all listings are recent, if so start looking to other pages
    if any(date == last_date for date in unique_dates):
        page_number = 2
        while True:
            webpage = f'https://it.pracuj.pl/?pn={page_number}'
            new_http_links, unique_dates = scrape_uls(webpage)
            http_links = http_links.union(new_http_links)

            if all(date == date_today or date == last_date for date in unique_dates):
                page_number += 1
            else:
                print(f'Dates: {unique_dates}')
                break
    else:
        print(f'Dates: {unique_dates}')

    # Append file containing all job listing
    with open('links_to_listings.txt', 'a+',encoding='UTF-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = http_links - old_records
        print(f'New: {len(new_records)}')
        for link in new_records:
            file.write(link + '\n')



def main(webpage):
    ''' Main method of scrape_urls.py
    Scrapes job offer links since last scraping'''
    new_http_links,unique_dates = scrape_uls(webpage)

    print(f'Links: {len(new_http_links)}\n')
    for link in new_http_links:
        print(link)
    print(f'Dates: {unique_dates}')

if __name__ == '__main__':
    main('https://it.pracuj.pl/')
