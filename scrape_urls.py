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
import logging_functions as l

def scrape_one_page(current_page, sleep_min=5, sleep_max=7):
    ''' Scrapes urls and dates from single page'''
    # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the file path to the ChromeDriver executable
    chromedriver_path = os.path.join(dir_path,
        'chromedriver_win32', 'chromedriver')

    # Set options to run Chrome in headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # Initialize the Chrome browser using ChromeDriver as Service object
    browser = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
    browser.get(current_page)

    # Wait for the page to load
    sleep(random.uniform(sleep_min, sleep_max))

    # Accept terms of service, if they appear
    try:
        accept_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                '//button[@data-test="button-accept-all-in-general"]')))
        accept_button.click()
    except:
        l.log_exception('scrape_one_page','Terms of Service button not found')

    # Wait for the page to load
    sleep(random.uniform(sleep_min, sleep_max))

    # Find all the location buttons
    location_buttons = browser.find_elements(By.CSS_SELECTOR,
        'div[data-test="offer-locations-button"]')
    if not location_buttons:
        print(f'{current_page} - No location buttons found')

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
            l.log_exception('scrape_one_page','No viewBox objects found')

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
    return http_links, unique_dates

def get_cutoff_date(date_file):
    '''Get last logging date'''
    last_date = None
    with open(date_file, 'r',encoding='UTF-8') as file:
        line = file.readline()
        last_date = datetime.datetime.strptime(line, '%Y-%m-%d').date()
    # 'last_date - one_day' gives overlam in the search
    return last_date - datetime.timedelta(days=1)

def scrape_single_skill(cutoff_date, base_url, iterable_url=None, sleep_min=7, sleep_max=23):
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
        http_links = http_links.union(scrape_single_skill(cutoff_date, new_base_url, new_iterable_url))
    return http_links

def update_file(http_links, urls_file):
    ''' Adds new records, removes old ones'''
    with open(urls_file, 'r+',encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = http_links - old_records
        print(f'New: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')

def update_date_log(date_file):
    ''' Update logging date'''
    with open(date_file, 'w',encoding='utf-8') as file:
        file.write(str(datetime.date.today()))

def save_set_to_file(new_set, file_name):
    ''' Saves set to file, each element per line'''
    with open(file_name, 'a', encoding='utf-8') as file:
        for element in new_set:
            file.write(str(element) + '\n')

def main(date_file, skill_set, urls_file, base_url, iterable_url=None):
    ''' Main method of scrape_urls.py
    Scrape all urls with job offers containing my skill set, then save to file'''

    cutoff_date_main = get_cutoff_date(date_file)
    http_links_main = scrape_all_skills(cutoff_date_main, skill_set, base_url, iterable_url)
    update_file(http_links_main, urls_file)
    update_date_log(date_file)

if __name__ == '__main__':
    ''' Performs basic logging set up'''
    l.main()
    
    '''Actual Script'''
    _searched_set = {'s=data+science', 's=big+data', 'tt=Python', 'tt=SQL', 'tt=R'}
    # Example: https://it.pracuj.pl/?tt=Python&jobBoardVersion=2&pn=1
    _base_url = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn=1'
    _iterable_url = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn='

    _date_file = 'last_date.log'
    _urls_file = 'urls_file.txt'

    main(_date_file, _searched_set, _urls_file, _base_url, _iterable_url)
