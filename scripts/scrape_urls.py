'''Web scraping popular polish job site, Pracuj.pl'''
import os
from pathlib import Path
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
import logging_functions as lf


def scrape_one_page(current_page, sleep_min=6, sleep_max=10) -> tuple:
    ''' Scrapes urls and dates from single page'''

    # Construct the file path to the ChromeDriver executable
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver_win32',
                                     'chromedriver')

    # Set options to run Chrome in headless mode
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')

    # Initialize the Chrome browser using ChromeDriver as Service object
    browser = webdriver.Chrome(service=Service(chromedriver_path),
                               options=chrome_options)

    browser.get(current_page)

    # Wait for the page to load
    sleep(random.uniform(sleep_min*2, sleep_max*2))

    # Accept terms of service, if they appear
    try:
        accept_button = WebDriverWait(browser, 10).until(
            # Worked until 2022-05-18
            # EC.presence_of_element_located((By.XPATH,
            # '//button[@data-test="button-accept-all-in-general"]')))
            # Since 2022-05-18
            EC.presence_of_element_located((By.XPATH, '//button[@data-test="button-submitCookie"]')))
        accept_button.click()
    except Exception as e:
        logging.error(f'Terms of Service button not found - {repr(e)}')

    # Wait for the page to load
    sleep(random.uniform(sleep_min*2, sleep_max*2))

    # pattern to match number of "lokalizacje" or "lokalizacji"
    pattern = r'(\d+\s*(lokalizacje|lokalizacji))'

    # Find all elements with multiple localisations
    all_elements = browser.find_elements(By.XPATH,
                                         '//*[contains(@data-test,"text-region")]')
    elements_to_click = []
    for element in all_elements:
        if re.search(pattern, element.text):
            parent_element = element.find_element(By.XPATH, '..')
            grandparent_element = parent_element.find_element(By.XPATH, '..')
            grand_grandparent_element = grandparent_element.find_element(By.XPATH, '..')
            elements_to_click.append(grand_grandparent_element)

            # Wait for the page to load
            sleep(random.uniform(sleep_min*2, sleep_max*2))

    if elements_to_click != []:
        logging.info(f'Found {len(elements_to_click)}'
                     '"lokalizacje" elements in {current_page}')
    else:
        logging.info(f'No "lokalizacje" elements found in {current_page}')

    # Click on each element
    for element in elements_to_click:
        try:
            # Scroll to the element to bring it into view
            browser.execute_script('arguments[0].scrollIntoView();', element)

            # Wait for scrolling to finish
            sleep(random.uniform(sleep_min, sleep_max))

            # Click on the element using JavaScript
            browser.execute_script('arguments[0].click();', element)
            logging.debug(f'Clicked on element {element.text}')

            # Scroll the page down to bring the details into view
            browser.execute_script('window.scrollBy(0, 300);')

            # Wait for the job offer details to load
            sleep(random.uniform(sleep_min, sleep_max))

        except Exception as e:
            logging.error(f'Unable to click localisation element - {repr(e)}')

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    # Find all the links starting with 'http'
    http_elements = soup.find_all('a', href=re.compile('^https://www.pracuj.pl/praca/'))
    http_links = {x.get('href') for x in http_elements}

    # Find all unique dates
    date_elements = soup.find_all('div', {'class': 'JobOfferstyles__FooterText-sc-1rq6ue2-22'})
    unique_dates = set()
    for element in date_elements:
        date_str = element.text.strip().split(': ')[-1]
        date_obj = datetime.datetime.strptime(date_str, '%d %B %Y').date()
        unique_dates.add(date_obj)
    browser.quit()
    logging.info(f'Found {len(http_links)} links on page {current_page}')

    return http_links, unique_dates


def combine_files(manual_files_path) -> str:
    '''Combines files created manually into one file'''

    combined_file = os.path.join(manual_files_path, 'combined_files.txt')

    # Get a list of all file paths in the directory that are text files
    files = os.listdir(manual_files_path)
    files = [item for item in files if item.endswith('.txt')]
    files = [os.path.join(manual_files_path, item) for item in files]

    # Combine the contents of all text files into one file
    with open(combined_file, 'w', encoding='utf-8') as outfile:
        for file in files:
            with open(file, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)
    logging.debug(f'Combined text files into {combined_file}')
    return combined_file


def scrape_from_file(combined_file) -> set:
    '''Scrapes urls and dates from files created manually'''

    http_links = set()

    with open(combined_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Define the regular expression pattern to match URLs
    http_pattern = r'https://www\.pracuj\.pl/praca/[^"]*'

    # Find all URLs in the text
    http_matches = re.findall(http_pattern, text)

    # Add the URLs to the set
    http_links.update(http_matches)

    for link in http_links:
        print(f'Found link: {link}')
    return http_links


def get_cut_off_date(date_file) -> datetime.date:
    '''Get last logging date from file'''
    last_date = None
    logging.debug(f'get date path: {date_file}')

    with open(date_file, 'r', encoding='UTF-8') as file:
        line = file.readline()
        last_date = datetime.datetime.strptime(line, '%Y-%m-%d').date()

    # To prevent gaps, set cut-off date to day before 'last_date'
    cut_off_date = last_date - datetime.timedelta(days=1)
    logging.info(f'Cut-off date: {cut_off_date}')
    return cut_off_date


def scrape_single_skill(cut_off_date, base_url, iterable_url, searched_id,
                        sleep_min=7, sleep_max=23) -> set:
    ''' Scrapes urls from given skills since last time.'''

    # Extract urls from base_url
    new_base_url = base_url.format(searched_id)
    http_links, unique_dates = scrape_one_page(new_base_url)

    # Wait to avoid banning
    sleep(random.uniform(sleep_min, sleep_max))

    # Check if all listings are recent, if so start looping using iterable_url
    if all(date > cut_off_date for date in unique_dates):
        page_number = 2
        while True:
            current_page = iterable_url.format(page_number, searched_id)
            new_http_links, unique_dates = scrape_one_page(current_page)

            if new_http_links:
                http_links = http_links.union(new_http_links)

                if any(date == cut_off_date for date in unique_dates):
                    break
            else:
                break
            page_number += 1
            # Wait to avoid banning
            sleep(random.uniform(sleep_min, sleep_max))
    return http_links


def scrape_all_skills(cut_off_date, skill_set,
                      base_url, iterable_url=None) -> set:
    ''' Scrapes urls all skills since last time.'''

    http_links = set()
    for searched_id in skill_set:
        http_links = http_links.union(scrape_single_skill(cut_off_date,
                                      base_url, iterable_url, searched_id))
    return http_links


def update_file(http_links, urls_file) -> None:
    ''' Adds new records, removes old ones'''
    with open(urls_file, 'r+', encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = http_links - old_records
        logging.info(f'New urls: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')


def update_date_log(date_file) -> None:
    ''' Update logging date file'''
    with open(date_file, 'w', encoding='utf-8') as file:
        file.write(str(datetime.date.today()))


def save_set_to_file(new_set, file_path) -> None:
    ''' Saves set to file, each element per line'''
    with open(file_path, 'a', encoding='utf-8') as file:
        for element in new_set:
            file.write(str(element) + '\n')


def main(date_file, skill_set, urls_file, base_url, manual_ulrs_path,
         iterable_url=None, manual_files_exist=False):
    '''Scrape all urls with job offers and save them to file'''

    if manual_files_exist:
        combined_file = combine_files(manual_ulrs_path)
        http_links_main = scrape_from_file(combined_file)

    else:
        cut_off_date_main = get_cut_off_date(date_file)
        http_links_main = scrape_all_skills(cut_off_date_main, skill_set,
                                            base_url, iterable_url)
        update_date_log(date_file)
    update_file(http_links_main, urls_file)


if __name__ == '__main__':
    current_file_name = Path(__file__).stem
    log_file_name = f'{current_file_name}_log.log'

    BASE_DIR = Path(__file__).parent.parent
    LOGGING_FILE = BASE_DIR / 'logging_files' / log_file_name
    LOGGING_JSON = BASE_DIR / 'logging_files' / 'logging_config.json'

    lf.configure_logging(LOGGING_JSON, LOGGING_FILE)
    logging.error('Testing saving logs to file.')

    # Scrape just SQL and Python as an example
    searched_set = {'itth=36', 'itth=37'}

    TXT_DIR = BASE_DIR / 'txt_files'
    FOR_SEARCH = TXT_DIR / 'for_search.csv'
    LAST_DATE_LOG = TXT_DIR / 'last_date.log'
    SCRAPPED_URLS = TXT_DIR / 'scrapped_urls.txt'
    MANUAL_URLS = TXT_DIR / 'manual_url_scraping'

    manual_files = Path(MANUAL_URLS).iterdir()
    manual_files_exist = any(file.is_file() for file in manual_files)

    # For Search, _BASE_URL will be used first, then _ITERABLE_URL untill end
    BASE_URL = 'https://it.pracuj.pl/praca?{}'
    ITERABLE_URL = 'https://it.pracuj.pl/praca?pn={}&{}'

    main(LAST_DATE_LOG, searched_set, SCRAPPED_URLS, BASE_URL, MANUAL_URLS,
         ITERABLE_URL, manual_files_exist)
