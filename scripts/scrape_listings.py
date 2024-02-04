'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import os
import re
import json
from time import sleep, gmtime, strftime
from numpy import random
import requests
import copy

import logging
from logging import config

if __name__ != '__main__':
    from . import logging_functions as l
    from . import email_functions as e
else:
    import logging_functions as l
    import email_functions as e

# Configure logging file
l.configure_logging()
logger = logging.getLogger(__name__)


def save_dict(new_dict: dict, file_path: str) -> None:
    ''' Saves dictionary to file'''
    json_str = json.dumps(new_dict, ensure_ascii=False)
    # file_path = os.path.join(os.path.dirname(__file__), '..', 'text_and_json', file_name)

    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(json_str + '\n')


def scrape_listing_from_json(url: str, timeout=5) -> str:
    ''' Scrapes job listing details from JSON to substring'''
    # Make a request to the URL and get the HTML response
    response = requests.get(url, timeout=timeout)
    response.encoding = 'utf-8'  # To recognise polish letters

    # Extract the JSON from 'window' as string
    start_string = "window['kansas-offerview'] = "
    end_string = '<'
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]
    return substring


def clean_listing_string(substring: str) -> str:
    ''' Cleans substring from problematic symbols, patterns, sequences'''

    substring = substring.strip()

    patterns = [r'\bundefined\b',  # incorrect null value
                r'\\n|\\t|\\r|\\b|\\f|\\"',  # sequences
                r'[^\w,:\.\'"\-(){}\[\]\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+'  # not polish
                ]
    for pattern in patterns:
        substring = re.sub(pattern, ' ', substring)

    missing_nulls = r':\s*(,|"\s*"|\]|\[\s*\]|\}|\{\s*\})'
    substring = re.sub(missing_nulls, ':null', substring)

    missing_commas_1 = r'null\s*([^,\]\}])'
    substring = re.sub(missing_commas_1, r'null,\g<1>', substring)
    missing_commas_2 = r'(\w+)\s+,\s*"'
    substring = re.sub(missing_commas_2, r'\1","', substring)

    extra_char_1 = r'(?<=",)\s*",(?=")'
    substring = re.sub(extra_char_1, '', substring)
    # extra_char_2 = r'(?<=,")\s*"(?=,")'
    # substring = re.sub(extra_char_2, '',substring)

    # Replace unicode for '/' with space
    substring = substring.replace('\\u002F', ' ')
    substring = substring.replace('u002F', ' ')
    substring = substring.replace('\\u003E', ' ')
    substring = substring.replace('u003E', ' ')
    substring = substring.replace('--', ' ')
    substring = substring.replace(', \"\"', ' ')

    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    substring = re.sub(r'\s*"\s*', '"', substring)

    # Add missing curly Brackets
    opening_braces = len(re.findall(r'{', substring))
    closing_braces = len(re.findall(r'}', substring))
    if opening_braces > closing_braces:
        substring += '}'*(opening_braces-closing_braces)
    return substring


def change_str_to_dict(substring: str) -> dict:
    '''  Convert the string to a dictionary using the json module'''
    logger.debug(substring)
    my_dict = json.loads(substring)
    logger.debug(json.dumps(my_dict, ensure_ascii=False, indent=2))
    return my_dict


def clean_region(region_name: str) -> str:
    ''' Keap only proper voivodeships names'''
    voivodeships_pl = ['dolnośląskie', 'kujawsko-pomorskie', 'lubelskie',
                       'lubuskie', 'łódzkie', 'małopolskie', 'mazowieckie',
                       'opolskie', 'podkarpackie', 'podlaskie', 'pomorskie',
                       'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie',
                       'wielkopolskie', 'zachodniopomorskie']
    voivodeships_en_1 = ['lower silesia', 'kuyavian-pomerania', 'lublin',
                         'lubusz', 'łódź', 'lesser poland', 'masovia', 'opole',
                         'subcarpathia', 'podlaskie', 'pomerania', 'silesia',
                         'holy cross', 'warmian-masuria', 'greater poland',
                         'west pomerania']
    voivodeships_en_2 = ['lower silesian', 'kuyavian-pomeranian', 'lublin',
                         'lubusz', 'łódź', 'lesser poland', 'masovian',
                         'opole', 'subcarpathian', 'podlaskie', 'pomeranian',
                         'silesian', 'holy cross', 'warmian-masurian',
                         'greater poland', 'west pomeranian']

    if region_name is None or region_name == '' or region_name == ' ':
        return None

    temp_name = region_name.lower()
    if temp_name in voivodeships_pl:
        return temp_name
    # If name is in english, return the polish name
    if temp_name in voivodeships_en_1:
        return voivodeships_pl[voivodeships_en_1.index(temp_name)]
    if temp_name in voivodeships_en_2:
        return voivodeships_pl[voivodeships_en_2.index(temp_name)]
    if temp_name in ['warmia-mazuria', 'warmia-mazurian', 'warmian-mazurian']:
        return 'warmińsko-mazurskie'
    if temp_name in ['kuyavia-pomerania', 'kuyavia-pomeranian']:
        return 'kujawsko-pomorskie'
    if temp_name in ['Łódź']:
        return 'łódzkie'
    # Clean region name
    if region_name in ['', ' ', 'abroad', 'zagranica']:
        return None
    return region_name


def clean_location(location_name: str) -> str:
    ''' Clean the location field by addind None or by removing the county
    or shire name inside the parentheses'''
    if location_name == '' or location_name == ' ':
        return None
    pattern = r'^(.*?)\s+\('
    match = re.search(pattern, location_name)
    if match:
        location_name = match.group(1)
    return location_name


def clean_contract_type(contract_type) -> str:
    '''Clean the contract_type field'''
    contract_pl = ['umowa o pracę', 'umowa zlecenie', 'umowa o dzieło',
                   'umowa na zastępstwo', 'umowa o pracę tymczasową',
                   'kontrakt B2B', 'umowa o staż praktyki', 'umowa agencyjna']
    contract_en = ['contract of employment', 'contract of mandate',
                   'contract for specific work', 'replacement contract',
                   'temporary employment contract', 'B2B contract',
                   'internship apprenticeship contract', 'agency agreement']
    if contract_type is None or contract_type == '' or contract_type == ' ':
        return None
    if contract_type in contract_pl:
        return contract_type
    if contract_type in contract_en:
        return contract_pl[contract_en.index(contract_type)]
    return contract_type


def simplify_dictionary(my_dict, tech_found) -> dict:
    ''' Extracts usefull data from the dictionary, creates new dictionary'''

    my_dict = my_dict['userReducer']['offerReducer']['offer']
    # Basic listing data
    job_title = my_dict['jobTitle']
    country = my_dict['workplaces'][0]['country']['name']
    region = my_dict['workplaces'][0]['region']['name']
    region = clean_region(region)

    # Work Schedule
    work_schedule = my_dict['workSchedules']
    position_level = my_dict['positionLevelsName']
    work_modes = [item['code'] for item in my_dict['workModes']]

    location = None
    if my_dict['workplaces'][0].get('inlandLocation') and \
            my_dict['workplaces'][0]['inlandLocation'].get('location') and \
            my_dict['workplaces'][0]['inlandLocation']['location'].get('name'):
        location = my_dict['workplaces'][0]['inlandLocation']['location']['name']
        location = clean_location(location)

    contract_type = my_dict['typesOfContracts'][0]['name']
    # Clean contract type
    contract_type = clean_contract_type(contract_type)

    # Salary specific
    is_salary = True
    if my_dict['typesOfContracts'][0]['salary'] is None:
        is_salary = False
        salary_from, salary_to = (None, None)
        salary_currency, salary_long_form = (None, None)
    else:
        is_salary = True
        salary_from = my_dict['typesOfContracts'][0]['salary']['from']
        salary_to = my_dict['typesOfContracts'][0]['salary']['to']
        salary_currency = my_dict['typesOfContracts'][0]['salary']['currency']['code']
        salary_long_form = my_dict['typesOfContracts'][0]['salary']['timeUnit']['longForm']['name']

    # Assuming both dates always comply to ISO 8601 format, UTC time zone,
    # scraping only YYYY-mm-dd
    publication_date = my_dict['dateOfInitialPublication'][:10]
    publication_month = publication_date[:7] + '-01'
    expiration_date = my_dict['expirationDate'][:10]
    expiration_month = expiration_date[:7] + '-01'

    tech_expected = []
    tech_optional = []
    req_expected = []
    req_optional = []
    dev_practices = None
    responsibilities = []

    for section in my_dict['sections']:
        if section['sectionType'] == 'technologies':
            for item in section['subSections']:
                if item['sectionType'] == 'technologies-expected':
                    tech_expected += [tech['name'] for tech in item['model']['customItems']]
                elif item['sectionType'] == 'technologies-optional':
                    tech_optional += [tech['name'] for tech in item['model']['customItems']]
        if section['sectionType'] == 'requirements':
            for item in section['subSections']:
                if item['sectionType'] == 'requirements-expected':
                    if 'paragraphs' in item['model']:
                        req_expected += list(item['model']['paragraphs'])
                    elif 'bullets' in item['model']:
                        req_expected += list(item['model']['bullets'])
                elif item['sectionType'] == 'requirements-optional':
                    if 'paragraphs' in item['model']:
                        req_optional += list(item['model']['paragraphs'])
                    elif 'bullets' in item['model']:
                        req_optional += list(item['model']['bullets'])

        elif section['sectionType'] == 'development-practices':
            dev_practices = [item['primaryTargetSiteName'] for item in section['model']['items']]

        elif section['sectionType'] == 'responsibilities':
            if 'bullets' in section['model']:
                responsibilities += list(section['model']['bullets'])
            elif 'paragraphs' in section['model']:
                responsibilities += list(section['model']['paragraphs'])

    # Remplace empty list with None
    tech_expected = tech_expected if len(tech_expected) > 0 else None
    tech_optional = tech_optional if len(tech_optional) > 0 else None
    req_expected = req_expected if len(req_expected) > 0 else None
    req_optional = req_optional if len(req_optional) > 0 else None
    responsibilities = responsibilities if len(responsibilities) > 0 else None

    # Loading data to simplified dictionary
    new_dict = {}
    # Basic listing data
    new_dict['job_title'] = job_title
    new_dict['country'] = country
    new_dict['region'] = region
    new_dict['location'] = location
    new_dict['contract_type'] = contract_type
    new_dict['work_schedule'] = work_schedule
    new_dict['position_level'] = position_level
    new_dict['work_modes'] = work_modes
    # Salary specific
    new_dict['is_salary'] = is_salary
    if is_salary:
        new_dict['salary'] = {
                 'min': salary_from,
                 'max': salary_to,
                 'currency': salary_currency,
                 'pay_period': salary_long_form
                 }
    # Dates
    new_dict['publication_date'] = publication_date
    new_dict['publication_month'] = publication_month
    new_dict['expiration_date'] = expiration_date
    new_dict['expiration month'] = expiration_month
    # technologies
    new_dict['technologies'] = {
             'expected': tech_expected,
             'optional': tech_optional,
             'found': tech_found
             }
    # requirements
    new_dict['requirements'] = {
             'expected': req_expected,
             'optional': req_optional
             }
    # development-practices
    new_dict['dev_practices'] = dev_practices
    # responsibilities
    new_dict['responsibilities'] = responsibilities

    # print(json.dumps(new_dict, ensure_ascii=False, indent=2))
    return new_dict


def extract_tech_set(file_with_tech) -> set:
    ''' Extract all technologies in file to a set'''
    tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file:
        for line in file:
            tech_set.add(line.strip())
    return tech_set


def extract_all_tech(substring, tech_set) -> list:
    ''' Extract all technologies/languages/annrevations from string
    Returns found tech list'''
    tech_found = []
    for tech in tech_set:
        tech_escaped = re.escape(tech)
        pattern = re.compile(r'\b(%s)\b' % tech_escaped, re.IGNORECASE)
        if pattern.search(substring):
            tech_found.append(tech)
    tech_found.sort()
    return tech_found


def save_dict_to_file(new_dict, file_path) -> None:
    ''' Saves dictionary to file'''
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(json.dumps(new_dict, ensure_ascii=False) + '\n')


def save_str_to_file(str, file_path) -> None:
    ''' Saves string to file'''
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(str + '\n')


def get_url_count(file_path) -> int:
    ''' Returns number of lines in file'''
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return len(lines)


def update_file(new_set, file_path) -> None:
    ''' Removes old records from file and saves new ones'''
    with open(file_path, 'r+', encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = new_set - old_records
        logger.info(f'New listings: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')


def listing_pipeline_main(substring, tech_set, file_name) -> None:
    ''' Pipeline saves listing details to file'''
    substring = clean_listing_string(substring)
    tech_found = extract_all_tech(substring, tech_set)
    my_dict = change_str_to_dict(substring)
    new_dict = simplify_dictionary(my_dict, tech_found)
    save_dict_to_file(new_dict, file_name)


def main(scraped_urls, file_with_tech, succesfull_urls, failed_urls,
         succesfull_file, failed_file, sleep_min=4, sleep_max=7) -> None:
    ''' Main method of scrape_listings.py
    Runs if script called directly'''
    succeses = 0
    failures = 0
    progress = 0
    last_progress = 0
    url_count = get_url_count(scraped_urls)
    progress_per_url = 1 / url_count * 100

    # Calculate estimated time
    aver_sleep = (sleep_min + sleep_max) / 2
    seconds_left = url_count * aver_sleep
    days_left = seconds_left // 86400
    time_left = strftime("%H:%M:%S", gmtime(int(seconds_left)))
    print(f'Listing Scraping - Estimated time: {days_left:2} '
          f'days and {time_left:8}')

    # Extract all technologies in file to a set
    _tech_set = extract_tech_set(file_with_tech)

    # Get the level of the console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_level = console_handler.level
    print(f'Console level: {console_level}')

    with open(scraped_urls, 'r', encoding='utf-8') as file:
        # Attempts scraping all urls from file. Record succeses and failures

        for url in file:
            url = url.strip()
            progress += progress_per_url
            seconds_left -= aver_sleep

            try:
                substring = scrape_listing_from_json(url)
                save_str_to_file(url, succesfull_urls)
            except:
                save_str_to_file(url, failed_urls)
                failures += 1
                logger.error(f'Opening url failed: {url}')
                l.save_to_log_file(__name__, __file__,
                                   f'Opening url failed: {url}')
                sleep(random.uniform(sleep_min, sleep_max))
                continue

            try:
                listing_pipeline_main(substring, _tech_set, succesfull_file)
                succeses += 1
            except:
                save_str_to_file(substring, failed_file)
                failures += 1
                logger.error(f'Cleaning listing failed: {url}')
                l.save_to_log_file(__name__, __file__,
                                   f'Cleaning listing failed: {url}')
            finally:
                # Print progress if console is set to INFO or DEBUG
                if console_level < 30:
                    days_left = int(seconds_left // 86400)
                    time_left = strftime("%H:%M:%S", gmtime(int(seconds_left)))

                    if console_level == 10:
                        print(f'Successes: {succeses:5}     '
                              f'Failures: {failures:5}     '
                              f'Progress: {progress:6}%     '
                              f'Time left: {days_left:2} days and {time_left:8}')

                    if console_level == 20 and \
                            int(progress) > last_progress:
                        last_progress = copy.deepcopy(int(progress))
                        print(f'Successes: {succeses:5}     '
                              f'Failures: {failures:5}     '
                              f'Progress: {progress:5.1f}%     '
                              f'Time left: {days_left:2} days and {time_left:8}')
                sleep(random.uniform(sleep_min, sleep_max))
        

if __name__ == '__main__':
    # Performs basic logging set up
    # Create log file name based on script name
    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    l.get_log_file_name(log_file_name)

    # Configure logging file
    l.configure_logging()
    logger = logging.getLogger(__name__)

    # Required files

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    TXT_DIR = os.path.join(PARENT_DIR, 'txt_files')
    SCRAPPED_URLS = os.path.join(TXT_DIR, 'scrapped_urls.txt')
    TECH_SEARCHED_FOR = os.path.join(TXT_DIR, 'technologies.txt')
    SUCCESFULL_URLS = os.path.join(TXT_DIR, 'succesfull_urls.txt')
    FAILED_URLS = os.path.join(TXT_DIR, 'failed_urls.txt')
    SUCCESFULL_EXTRACTIONS = os.path.join(TXT_DIR, 'succesfull_extractions.txt')
    FAILED_EXTRACTIONS = os.path.join(TXT_DIR, 'failed_extractions.txt')

    # Scraping job listings from job site
    main(SCRAPPED_URLS, TECH_SEARCHED_FOR, SUCCESFULL_URLS, FAILED_URLS,
         SUCCESFULL_EXTRACTIONS, FAILED_EXTRACTIONS)
