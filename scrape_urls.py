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

def scrape_one_page(current_page, sleep_min=2, sleep_max=4):
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
    browser.get(current_url)

    # Wait for the page to load
    sleep(random.uniform(sleep_min, sleep_max))

    # Accept terms of service, if they appear
    try:
        accept_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                '//button[@data-test="button-accept-all-in-general"]')))
        accept_button.click()
    except:
        print(f'{current_url} - Could not find or click accept button')

    # Wait for the page to load
    sleep(random.uniform(sleep_min, sleep_max))

    # Find all the location buttons
    location_buttons = browser.find_elements(By.CSS_SELECTOR,
        'div[data-test="offer-locations-button"]')
    if not location_buttons:
        print(f'{current_url} - No location buttons found')

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
            print(f'{current_url} - Could not click on button')

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

def get_cutoff_date(date_file)
    '''Get last logging date'''
    last_date = None
    with open(date_file, 'r',encoding='UTF-8') as file:
        line = file.readline()
        last_date = datetime.datetime.strptime(line, '%Y-%m-%d').date()
    # 'last_date - one_day' gives overlam in the search
    
    return last_date - datetime.timedelta(days=1)

def create_pages(skill, base_url_front, base_url_end, sec_url_front=None, sec_url_end=None)
    ''' Create page adresses fot given skill'''
    base_url = base_url_front + '{}' + base_url_end
    if sec_url_front and sec_url_end:
        secondary_url = sec_url_front + '{}' + sec_url_end
    else:
        secondary_url = base_url  
    return base_url.format(skill), secondary_url.format(skill)

def scrape_single_skill(cutoff_date, base_url, secondary_url=None, sleep_min=7, sleep_max=23):
    ''' Scrapes urls from given skills since last time.
    Assumes skill name is already build into base_url and secondary_url'''

    # Use base_url if secondary_url was not provided
    secondary_url = secondary_url or base_url
    
    # Extract urls from base_url
    http_links, unique_dates = scrape_one_page(base_url)
    # Wait to avoid banning
    sleep(random.uniform(sleep_min, sleep_max))

    # Check if all listings are recent, if so start looping using secondary_url
    if all(date > cutoff_date for date in unique_dates):
        page_number = 2
        while True:
            current_page = secondary_url + str(page_number)
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

def scrape_all_skills(cutoff_date, base_url, secondary_url=None, skill_set)
    ''' Scrapes urlsfor given skills since last time.
    Assumes base_url and secondary_url can take in skill name with .format()'''

    # Use base_url if secondary_url was not provided
    secondary_url = secondary_url or base_url

    http_links = {}
    for skill in skill_set:
        base_url, secondary_url = create_pages(skill, base_url_front, base_url_end, sec_url_front=None, sec_url_end=None)
        http_links.union(scrape_single_skill(cutoff_date, base_url, secondary_url=None, sleep_min=7, sleep_max=23))





def save_set_to_file(new_set, file_name):
    ''' Saves set to file, each element per line'''
    with open(file_name, 'a', encoding='utf-8') as file:
        for element in new_set:
            file.write(str(element) + '\n')

def update_file(new_set, file_name)
    ''' Adds new records, removes old ones'''
    with open('links_to_listings.txt', 'w+',encoding='UTF-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = new_set - old_records
        print(f'New: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for link in new_records:
            file.write(link + '\n')





def url_pipeline(date_file):
    ''' Pipeline scrapes listings for each skill in skill set'''
    pipeline = (get_cutoff_date(date_file)
        | get_pages
        | Filter(lambda x: check_for_skill_set(x, skill_set))
        | clean_listing_string
        | change_str_to_dict
        | extract_data(url)
        | save_to_file(file_name))
    return pipeline


















def main(current_page):
    ''' Main method of scrape_urls.py
    Scrape all urls with job offers containing my skill set'''
    

if __name__ == '__main__':
    skill_set = {'Python', 'SQL', 'R'}
    # Example: https://it.pracuj.pl/?tt=Python&jobBoardVersion=2&pn=1
    url_front = 'https://it.pracuj.pl/?tt='
    url_end = '&jobBoardVersion=2&pn=1'
    sec_url_front = 'https://it.pracuj.pl/?tt='
    sec_url_end = '&jobBoardVersion=2&pn='

    sec_url_front, sec_url_end

    date_file = 'last_date.log'
    file_with_urls = 'file_with_urls.txt'
    initial_page = 'https://it.pracuj.pl/'
    next_pages = 'https://it.pracuj.pl/?pn='

