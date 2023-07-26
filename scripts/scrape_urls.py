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

import logging
from logging import config

if __name__ != '__main__':
    from . import logging_functions as l
    from . import email_functions as e
else:
    import logging_functions as l
    import email_functions as e

def scrape_one_page(current_page, sleep_min=5, sleep_max=7):
    ''' Scrapes urls and dates from single page'''
    # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the file path to the ChromeDriver executable
    chromedriver_path = os.path.join(dir_path,'..','chromedriver_win32', 'chromedriver')

    # Set options to run Chrome in headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # Initialize the Chrome browser using ChromeDriver as Service object
    browser = webdriver.Chrome(service=Service(chromedriver_path), \
        options=chrome_options)
    browser.get(current_page)

    # Wait for the page to load
    sleep(random.uniform(sleep_min, sleep_max))

    # Accept terms of service, if they appear
    
    try:
        accept_button = WebDriverWait(browser, 10).until(
            # Worked until 2022-05-18
            #EC.presence_of_element_located((By.XPATH,
            #    '//button[@data-test="button-accept-all-in-general"]')))
            # Since 2022-05-18
            EC.presence_of_element_located((By.XPATH, \
                '//button[@data-test="button-submitCookie"]')))
        accept_button.click()
    except:
        logger.error('scrape_one_page - Terms of Service button not found'
                         ' - {l.get_exception()}')
        e.error_email('scrape_one_page - Terms of Service button not found')

    # Wait for the page to load
    sleep(random.uniform(sleep_min, sleep_max))

    # Find all the location buttons
    location_buttons = browser.find_elements(By.CSS_SELECTOR,
        'div[data-test="offer-locations-button"]')
    if not location_buttons:
        logger.info(f'No location buttons found in {current_page}')

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
            sleep(random.uniform(sleep_min, sleep_max))
        except:
            logger.error('scrape_one_page - No viewBox objects found'
                         ' - {l.get_exception()}')
            l.save_to_log_file(__name__, __file__, 'No viewBox objects found')

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    # Find all the links starting with 'http'
    http_elements = soup.find_all('a',
        href=re.compile('^https://www.pracuj.pl/praca/'))
    http_links = {x.get('href') for x in http_elements}

    #Find all unique dates
    date_elements = soup.find_all('div',
        {'class': 'JobOfferstyles__FooterText-sc-1rq6ue2-22'})
    unique_dates = set()
    for element in date_elements:
        date_str = element.text.strip().split(': ')[-1]
        date_obj = datetime.datetime.strptime(date_str, '%d %B %Y').date()
        unique_dates.add(date_obj)

    browser.quit()
    logger.info(f'Found {len(http_links)} links on page {current_page}')
    return http_links, unique_dates

def get_cutoff_date(date_file):
    '''Get last logging date
    Assumes file is in folder "text_and_json"'''
    last_date = None
    date_file_path = os.path.join(os.path.dirname(__file__), \
                                  '..','text_and_json', date_file)
    logger.debug(f'get date path: {date_file_path}')

    with open(date_file_path, 'r',encoding='UTF-8') as file:
        line = file.readline()
        last_date = datetime.datetime.strptime(line, '%Y-%m-%d').date()
    # 'last_date - one_day' gives overlam in the search
    cut_off_date = last_date - datetime.timedelta(days=1)
    logger.info(f'Cut-off date: {cut_off_date}')
    return cut_off_date

def scrape_single_skill(cutoff_date, base_url, iterable_url=None, \
    sleep_min=7, sleep_max=23):
    ''' Scrapes urls from given skills since last time.
    Assumes skill name is already build into base_url and iterable_url'''

    # Use base_url if iterable_url was not provided
    iterable_url = iterable_url or base_url

    # Extract urls from base_url
    http_links, unique_dates = scrape_one_page(base_url)
    # Wait to avoid banning
    sleep(random.uniform(sleep_min, sleep_max))

    # Check if all listings are recent, if so start looping using iterable_url
    if all(date > cutoff_date for date in unique_dates):
        page_number = 2
        while True:
            current_page = iterable_url + str(page_number)
            new_http_links, unique_dates = scrape_one_page(current_page)

            if new_http_links:
                http_links = http_links.union(new_http_links)

                if any(date == cutoff_date for date in unique_dates):
                    break
            else:
                break
            page_number += 1
            # Wait to avoid banning
            sleep(random.uniform(sleep_min, sleep_max))
    return http_links

def scrape_all_skills(cutoff_date, skill_set, base_url, iterable_url=None):
    ''' Scrapes urls all skills since last time.
    Assumes base_url and iterable_url can take in skill name with .format()'''

    # Use base_url if iterable_url was not provided
    iterable_url = iterable_url or base_url

    http_links = set()
    for skill in skill_set:
        new_base_url = base_url.format(skill)
        new_iterable_url = iterable_url.format(skill)
        http_links = http_links.union(scrape_single_skill(cutoff_date, \
            new_base_url, new_iterable_url))
    return http_links

def update_file(http_links, urls_file):
    ''' Adds new records, removes old ones
    Assumes file is in folder "text_and_json"'''
    urls_file_path = os.path.join(os.path.dirname(__file__), \
                                  '..', 'text_and_json', urls_file)
  
    with open(urls_file_path, 'r+',encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = http_links - old_records
        logger.info(f'New urls: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')

def update_date_log(date_file):
    ''' Update logging date
    Assumes file is in folder "text_and_json"'''
    date_file_path = os.path.join(os.path.dirname(__file__), \
                                  '..', 'text_and_json', date_file)
        
    with open(date_file_path, 'w',encoding='utf-8') as file:
        file.write(str(datetime.date.today()))

def save_set_to_file(new_set, file_name):
    ''' Saves set to file, each element per line
    Assumes file is in folder "text_and_json"'''
    file_path = os.path.join(os.path.dirname(__file__), \
                                '..', 'text_and_json', file_name)

    with open(file_path, 'a', encoding='utf-8') as file:
        for element in new_set:
            file.write(str(element) + '\n')

def main(date_file, skill_set, urls_file, base_url, iterable_url=None):
    ''' Main method of scrape_urls.py
    Scrape all urls with job offers containing skill set, then save to file'''

    cutoff_date_main = get_cutoff_date(date_file)
    http_links_main = scrape_all_skills(cutoff_date_main, skill_set, \
        base_url, iterable_url)
    update_file(http_links_main, urls_file)
    update_date_log(date_file)

if __name__ == '__main__':
    #Performs basic logging set up
    #Create log file name based on script name
    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    l.get_log_file_name(log_file_name)

    #Configure logging file
    l.configure_logging()
    logger = logging.getLogger(__name__)

    #Actual Script
    _SEARCHED_SET = {'s=data+science', 's=big+data', 'tt=Python', 'tt=SQL', 'tt=R'}
    # Example: https://it.pracuj.pl/?tt=Python&jobBoardVersion=2&pn=1
    _BASE_URL = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn=1'
    _ITERABLE_URL = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn='

    _DATE_FILE = 'last_date.log'
    _URLS_FILE = 'urls_file.txt'

    main(_DATE_FILE, _SEARCHED_SET, _URLS_FILE, _BASE_URL, _ITERABLE_URL)
