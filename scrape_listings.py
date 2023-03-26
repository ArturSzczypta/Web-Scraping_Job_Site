'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import re
import json
from time import sleep
from numpy import random
import traceback
import datetime

import logging
from logging import config
import logging_functions as l
import requests

def replace_empty(data_string):
    """ Replace empty dictionaries, lists and strings with None """
    patterns = [r':\s*""', r':\s*\[\]', r':\s*{}', r':\s*,', r':\s*]',
    r':\s*\}', r':\s*\{\}']
    for pattern in patterns:
        data_string = re.sub(pattern, ':null', data_string)
    return data_string

def add_missing_commas(data_string):
    """ Add missing comas between keys """
    pattern = r'null\s*([^,\]\}])'
    return re.sub(pattern, r'null,\g<1>', data_string)

def scrape_single_listing(url, timeout=5):
    ''' Scrapes job listing details from the url, return a dictionary'''
    # Make a request to the URL and get the HTML response
    response = requests.get(url, timeout=timeout)
    response.encoding = 'utf-8' # To recognise polish letters

    # Extract the substring {...} between "window['kansas-offerview']="and "<"
    start_string = "window['kansas-offerview'] = "
    end_string = "<"
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]
    # Replace invalid valiable names with null, so i can create dictionary
    substring = re.sub(r'\bundefined\b', '', substring)

    # Remove sequences
    substring = re.sub(r'\\n|\\t|\\r|\\"', ' ', substring)
    substring = substring.strip()
    substring = re.sub(r'\s+', ' ', substring) # keep single white spaces
    substring = replace_empty(substring)
    substring = add_missing_commas(substring)

    # Replace any non-alphanumeric or non-allowed characters with space
    substring = re.sub(r'[^\w,:\.\'"\-(){}\[\]\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+', '',
        substring)
    substring = substring.replace("u002F", " ")
    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    #print(substring)

    # Convert the string to a dictionary using the json module
    my_dict = json.loads(substring)
    #print(json.dumps(my_dict, ensure_ascii=False, indent=2))
    return my_dict

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
    end_string = "<"
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]
    return substring

def skill_patterns(skill_set):
    ''' Create regex pattern for given skill set
    I assume names of languages and technologies names shorter than 3
    have to be search as \b%s\b (R, C)
    Longer names can be part of longer string (PostgreSQL, MySQL for sql)
    Each pattern dinds all instances of upper/lower case and capitalised'''

    skills_schort = []
    skills_long = []
    for skill in skill_set:
        if len(skill) <3:
            skills_schort.append(re.escape(skill))
        else:
            skills_long.append(re.escape(skill))

    pattern_1 = None
    pattern_2 = None
    if len(skills_schort) > 0:
        pattern_1 = '|'.join(skills_schort)
    if len(skills_long) > 0:
        pattern_2 = '|'.join(skills_long)

    if pattern_1 and pattern_2:
        pattern = re.compile(r'\b(%s)\b|(%s)' % (pattern_1, pattern_2),
            re.IGNORECASE)
    elif pattern_1:
        pattern = re.compile(pattern_1, re.IGNORECASE)
    elif pattern_2:
        pattern = re.compile(pattern_2, re.IGNORECASE)
    else:
        pattern = ''

    return pattern

def check_for_skill_set(substring, skill_set):
    ''' Check for elements of skill set in the substring
    Cancel pipeline if none of skills is mentioned'''
    return re.search(skill_patterns(skill_set),substring, flags=re.IGNORECASE)

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

    # Replace unicode for '/' with space
    substring = substring.replace('\\u002F', ' ')
    substring = substring.replace('u002F', ' ')
    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    return substring

def change_str_to_dict(substring):
    '''  Convert the string to a dictionary using the json module'''
    #print(substring)
    my_dict = json.loads(substring)
    #print(json.dumps(my_dict, ensure_ascii=False, indent=2))
    return my_dict

def extract_data(my_dict, url):
    ''' Extracts usefull data from the dictionary, creates new dictionary'''

    #Basic listing data
    job_title = my_dict['offerReducer']['offer']['jobTitle']
    country = my_dict['offerReducer']['offer']['workplaces'][0]['country']['name']
    region = my_dict['offerReducer']['offer']['workplaces'][0]['region']['name']

    location = None
    if my_dict['offerReducer']['offer']['workplaces'][0].get('inlandLocation') and \
    my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation'].get('location') and \
    my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location'].get('name'):
        location = my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location']['name']

    contract_type = my_dict['offerReducer']['offer']['typesOfContracts'][0]['name']

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

    # Assuming both dates always comply to ISO 8601 format, UTC time zone
    publication_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['dateOfInitialPublication']).date()
    expiration_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['expirationDate']).date()

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
            dev_practices = list(section['model']['items'])

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
        'salary_from': salary_from
        'salary_to': salary_to
        'salary_currency': salary_currency
        'salary_long_form': salary_long_form
        }  
    # Dates
    new_dict['publication_date'] = str(publication_date)
    new_dict['expiration_date'] = str(expiration_date)
    # technologies
    
    new_dict['tech_expected'] = tech_expected
    new_dict['tech_optional'] = tech_optional
    # requirements
    new_dict['req_expected'] = req_expected
    new_dict['req_optional'] = req_optional
    # development-practices
    new_dict['dev_practices'] = dev_practices
    # responsibilities
    new_dict['responsibilities'] = responsibilities

    #print(json.dumps(new_dict, ensure_ascii=False, indent=2))
    return new_dict

def save_to_file(new_dict, file_name):
    ''' Saves dictionary to file'''
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(json.dumps(new_dict, ensure_ascii=False) + '\n')

def get_url_count(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return len(lines)

def listing_pipeline_main(url,file_name):
    ''' Pipeline saves listing details to file'''
    substring = scrape_listing_from_json(url)
    substring = clean_listing_string(substring)
    my_dict = change_str_to_dict(substring)
    new_dict = extract_data(my_dict, url)
    save_to_file(new_dict, file_name)

def listing_pipeline_mongodb(url,file_name):
    ''' Pipeline saves listing details to file'''
    substring = scrape_listing_from_json(url)
    substring = clean_listing_string(substring)
    my_dict = change_str_to_dict(substring)
    new_dict = extract_data(my_dict, url)
    

def main(scraped_urls, succesfull, failed, sleep_min=4, sleep_max=8):
    ''' Main method of scrape_listings.py
    Runs if script called directly'''
    succeses = 0
    failures = 0
    url_count = get_url_count(scraped_urls)

    with open(scraped_urls, 'r', encoding='UTF-8') as file:
        # Record Listing using pipeline. If failed, record in serepate file
        for url in file:
            url = url.strip()
            try:
                listing_pipeline_main(url, succesfull)
                succeses += 1
            except:
                failures += 1
                with open(failed, 'a', encoding='UTF-8') as file_2:
                    file_2.write(url + '\n')
            finally:
                progress = round((succeses+failures)/url_count*100, 3)
                print(f'Successes: {succeses:4}   '
                    f'Failures: {failures:4}   '
                    f'Progress: {progress:5}%')
                sleep(random.uniform(sleep_min, sleep_max))

def save_to_mongodb_atlas(scraped_urls, succesfull, failed, sleep_min=4, sleep_max=8):
    ''' Main method of scrape_listings.py
    Runs if script called directly'''
    succeses = 0
    failures = 0
    url_count = get_url_count(scraped_urls)

    with open(scraped_urls, 'r', encoding='UTF-8') as file:
        # Record Listing using pipeline. If failed, record in serepate file
        for url in file:
            url = url.strip()
            try:
                new_dict = listing_pipeline_mongodb(url, succesfull)
                # Save to MongoDB Atlas - Web_Scraping_Job_Site.Job_Listings


                succeses += 1
            except:
                failures += 1
                # Save to MongoDB Atlas - Web_Scraping_Job_Site.Failed_Urls


            finally:
                progress = round((succeses+failures)/url_count*100, 3)
                print(f'Successes: {succeses:4}   '
                    f'Failures: {failures:4}   '
                    f'Progress: {progress:5}%')
                sleep(random.uniform(sleep_min, sleep_max))

if __name__ == '__main__':
    ''' Performs basic logging set up'''
    l.main()

    ''' Actual Script'''
    _scraped_urls = 'scraped_urls_1.txt'
    _succesfull = 'file_succesfull.txt'
    _failed = 'file_failed.txt'
    main(_scraped_urls, _succesfull, _failed)
