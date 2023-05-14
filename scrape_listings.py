'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import re
import json
from time import sleep
from numpy import random
import requests

import logging
from logging import config
import logging_functions as l


def save_dict(new_dict, file_name):
    ''' Saves dictionary to file'''
    json_str = json.dumps(new_dict, ensure_ascii=False)

    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(json_str + '\n')

def scrape_listing_from_json(url, timeout=5):
    ''' Scrapes job listing details from JSON to substring'''
    # Make a request to the URL and get the HTML response
    response = requests.get(url, timeout=timeout)
    response.encoding = 'utf-8' # To recognise polish letters

    # Extract the JSON from 'window' as string
    start_string = "window['kansas-offerview'] = "
    end_string = '<'
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]
    return substring

def clean_listing_string(substring):
    ''' Cleans substring from problematic symbols, patterns, sequences'''
    substring = substring.strip()
    #print(substring)
    #print('\n\n\n')

    patterns = [
    r'\bundefined\b', # incorrect null value
    r'\\n|\\t|\\r|\\b|\\f|\\"', # sequences
    r'[^\w,:\.\'"\-(){}\[\]\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+' # not allowed characters
    ]
    for pattern in patterns:
        substring = re.sub(pattern,' ',substring)

    missing_nulls = r':\s*(,|"\s*"|\]|\[\s*\]|\}|\{\s*\})'
    substring = re.sub(missing_nulls, ':null', substring)

    missing_commas = r'null\s*([^,\]\}])'
    substring =  re.sub(missing_commas, r'null,\g<1>', substring)
    missing_commas_2 = r'(\w+)\s+,\s*"'
    substring =  re.sub(missing_commas_2, r'\1","', substring)

    # Replace unicode for '/' with space
    substring = substring.replace('\\u002F', ' ')
    substring = substring.replace('u002F', ' ')
    substring = substring.replace('\\u003E', ' ')
    substring = substring.replace('u003E', ' ')
    substring = substring.replace('--', ' ')
    substring = substring.replace(', \"\"', ' ')
    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    return substring

def change_str_to_dict(substring):
    '''  Convert the string to a dictionary using the json module'''
    #print(substring)
    my_dict = json.loads(substring)
    #print(json.dumps(my_dict, ensure_ascii=False, indent=2))
    return my_dict

def clean_region(region_name):
    ''' Keap only proper voivodeships names'''
    voivodeships_pl = ['dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 
                    'łódzkie', 'małopolskie', 'mazowieckie', 'opolskie', 'podkarpackie', 
                    'podlaskie', 'pomorskie', 'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie', 
                    'wielkopolskie', 'zachodniopomorskie']
    voivodeships_en_1 = ['lower silesia', 'kuyavian-pomerania', 'lublin', 'lubusz', 'łódź', 
                       'lesser poland', 'masovia', 'opole', 'subcarpathia', 
                       'podlaskie', 'pomerania', 'silesia', 'holy cross', 'warmian-masuria',
                       'greater poland', 'west pomerania']
    voivodeships_en_2 = ['lower silesian', 'kuyavian-pomeranian', 'lublin', 'lubusz', 'łódź', 
                       'lesser poland', 'masovian', 'opole', 'subcarpathian', 
                       'podlaskie', 'pomeranian', 'silesian', 'holy cross', 'warmian-masurian',
                       'greater poland', 'west pomeranian']
    if region_name is None or region_name == '' or region_name == ' ':
        return None
    
    temp_name = region_name.lower()
    # If name is in polish, return it in lower case
    if temp_name in voivodeships_pl:
        return temp_name
    # If name is in english, return polish name
    if temp_name in voivodeships_en_1:
        return voivodeships_pl[voivodeships_en_1.index(temp_name)]
    if temp_name in voivodeships_en_2:
        return voivodeships_pl[voivodeships_en_2.index(temp_name)]
    if temp_name in ['warmia-mazuria', 'warmia-mazurian']:
        return 'warmińsko-mazurskie'
    if temp_name in ['kuyavia-pomerania', 'kuyavia-pomeranian']:
        return 'kujawsko-pomorskie'
    # If abroad, return None
    if region_name in ['abroad', 'zagranica']:
        return None
    return region_name

def clean_contract_type(contract_type):
    '''Clean the contract_type field'''
    contract_pl = ['umowa o pracę', 'umowa zlecenie', 'umowa o dzieło', 
                   'umowa na zastępstwo', 'umowa o pracę tymczasową', 'kontrakt B2B', 
                   'umowa o staż praktyki', 'umowa agencyjna']
    contract_en = ['contract of employment', 'contract of mandate', 'contract for specific work', 
                   'replacement contract', 'temporary employment contract', 'B2B contract', 
                   'internship apprenticeship contract', 'agency agreement']
    if contract_type is None or contract_type == '' or contract_type == ' ':
        return None
    if contract_type in contract_pl:
        return contract_type
    if contract_type in contract_en:
        return contract_pl[contract_en.index(contract_type)]
    return contract_type

def simplify_dictionary(my_dict, url, tech_found):
    ''' Extracts usefull data from the dictionary, creates new dictionary'''

    #Basic listing data
    job_title = my_dict['offerReducer']['offer']['jobTitle']
    country = my_dict['offerReducer']['offer']['workplaces'][0]['country']['name']
    region = my_dict['offerReducer']['offer']['workplaces'][0]['region']['name']
    # Clean region name
    region = clean_region(region)

    location = None
    if my_dict['offerReducer']['offer']['workplaces'][0].get('inlandLocation') and \
    my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation'].get('location') and \
    my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location'].get('name'):
        location = my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location']['name']
    
    

    contract_type = my_dict['offerReducer']['offer']['typesOfContracts'][0]['name']
    # Clean contract type
    contract_type = clean_contract_type(contract_type)

    # Salary specific
    is_salary = True
    if my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary'] is None:
        is_salary = False
        salary_from, salary_to, salary_currency, salary_long_form = (None, None, None, None)
    else:
        is_salary = True
        salary_from = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']['from']
        salary_to = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']['to']
        salary_currency = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']['currency']['code']
        salary_long_form = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']['timeUnit']['longForm']['name']

    # Assuming both dates always comply to ISO 8601 format, UTC time zone, scraping only YYYY-mm-dd
    publication_date = my_dict['offerReducer']['offer']['dateOfInitialPublication'][:10]
    publication_month = publication_date[:7] + '-01'
    expiration_date = my_dict['offerReducer']['offer']['expirationDate'][:10]

    tech_expected = []
    tech_optional = []
    req_expected = []
    req_optional = []
    dev_practices = None
    responsibilities = []

    for section in my_dict['offerReducer']['offer']['sections']:
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

    #Loading data to simplified dictionary
    new_dict = {}
    #Basic listing data
    new_dict['url'] = url
    new_dict['job_title'] = job_title
    new_dict['country'] = country
    new_dict['region'] = region
    new_dict['location'] = location
    new_dict['contract_type'] = contract_type
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

    #print(json.dumps(new_dict, ensure_ascii=False, indent=2))
    return new_dict

def extract_tech_set(file_with_tech):
    ''' Extract all technologies in file to a set'''
    tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file:
        for line in file:
            tech_set.add(line.strip())
    return tech_set

def extract_all_tech(substring, tech_set):
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

def save_dict_to_file(new_dict, file_name):
    ''' Saves dictionary to file'''
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(json.dumps(new_dict, ensure_ascii=False) + '\n')

def save_str_to_file(new_dict, file_name):
    ''' Saves string to file'''
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(new_dict + '\n')

def get_url_count(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return len(lines)
    
def update_file(new_set, urls_file):
    ''' Adds new records, removes old ones'''
    with open(urls_file, 'r+',encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)
        new_records = new_set - old_records
        print(f'New: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')

def listing_pipeline_main(url, tech_set, file_name):
    ''' Pipeline saves listing details to file'''
    substring = scrape_listing_from_json(url)
    substring = clean_listing_string(substring)
    tech_found = extract_all_tech(substring, tech_set)
    my_dict = change_str_to_dict(substring)
    new_dict = simplify_dictionary(my_dict, url, tech_found)
    save_dict_to_file(new_dict, file_name)

def main(scraped_urls, file_with_tech, succesfull_file, failed_file,
    sleep_min=4, sleep_max=8):
    ''' Main method of scrape_listings.py
    Runs if script called directly'''
    succeses = 0
    failures = 0
    url_count = get_url_count(scraped_urls)
    _tech_set = extract_tech_set(file_with_tech)

    with open(scraped_urls, 'r', encoding='UTF-8') as file:
        # Record Listing using pipeline. If failed, record in serepate file
        for url in file:
            url = url.strip()
            try:
                listing_pipeline_main(url, _tech_set, succesfull_file)
                succeses += 1
            except:
                save_str_to_file(url, failed_file)
                failures += 1
                l.log_exception('scrape_listings - main',f'Scraping failed {url}')
            finally:
                progress = round((succeses+failures)/url_count*100, 3)
                print(f'Successes: {succeses:4}   '
                    f'Failures: {failures:4}   '
                    f'Progress: {progress:5}%')
                sleep(random.uniform(sleep_min, sleep_max))

if __name__ == '__main__':
    #Performs basic logging set up
    #Get this script name
    log_file_name = __file__.split('\\')
    log_file_name = f'{log_file_name[-1][:-3]}_log.log'

    l.get_log_file_name(log_file_name)

    #Configure logging file
    l.configure_logging()
    logger = logging.getLogger('main')

    # Actual Script
    _scraped_urls = 'urls_file_today.txt'
    _file_with_tech = 'technologies.txt'
    _succesfull_temp = 'succesfull_extractions_temp.txt'
    _succesfull_final = 'succesfull_extractions.txt'
    _failed = 'failed_extractions.txt'
    main(_scraped_urls, _file_with_tech, _succesfull_temp, _succesfull_final, _failed)
