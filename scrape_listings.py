'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import re
import requests
import json
from time import sleep
from numpy import random
import unicodedata
import traceback
import datetime

import logging
from logging import config
import logging_functions as l

def replace_empty(data_string):
    """ Replace empty dictionaries, lists and strings with None """
    patterns = [r':\s*""', r':\s*\[\]', r':\s*{}', r':\s*,', r':\s*]', r':\s*\}', r':\s*\{\}']
    for pattern in patterns:
        data_string = re.sub(pattern, ':null', data_string)
    return data_string

def add_missing_commas(data_string):
    """ Add missing comas between keys """
    pattern = r'null\s*([^,\]\}])'
    return re.sub(pattern, r'null,\g<1>', data_string)

def scrape_single_listing(url):
    ''' Scrapes job listing details from the url, return a dictionary'''
    # Make a request to the URL and get the HTML response
    response = requests.get(url)
    response.encoding = 'utf-8' # To recognise polish letters
    html = response.text

    # Extract the substring {...} between "window['kansas-offerview'] = "and "<"
    start_string = "window['kansas-offerview'] = "
    end_string = "<"
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]
    # Replace invalid valiable names with null, so i can create dictionary
    substring = re.sub(r'\bundefined\b', '', substring)
    
    # Remove sequences
    substring = re.sub(r'\\n|\\t|\\r|\\"', ' ', substring)
    substring = substring.strip() # remove any trailing or leading white spaces
    substring = re.sub(r'\s+', ' ', substring) # replace consecutive white spaces with a single white space
    substring = replace_empty(substring)
    substring = add_missing_commas(substring)

    # Replace any non-alphanumeric or non-allowed characters with space
    substring = re.sub(r'[^\w,:\.\'"\-(){}\[\]\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+', '', substring)
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


def scrape_listing_from_json(url):
    ''' Scrapes job listing details from JSON to substring'''
    # Make a request to the URL and get the HTML response
    response = requests.get(url)
    response.encoding = 'utf-8' # To recognise polish letters
    html = response.text

    # Extract the JSON from 'window' as string
    start_string = "window['kansas-offerview'] = "
    end_string = "<"
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]
    return substring

def clean_listing_string(substring)
    ''' Cleans substring from problematic symbols, patterns, sequences'''
    substring = substring.strip()

    patterns = [
    r'\bundefined\b', # incorrect null value
    r'\\n|\\t|\\r|\\b|\\f|"', # sequences
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
    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    return substring

def change_str_to_dict(substring)
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
                        req_expected += [req for req in item['model']['paragraphs']]
                    elif 'bullets' in item['model']:
                        
                        req_expected += [req for req in item['model']['bullets']]
                elif item['sectionType'] == 'requirements-optional':
                    if 'paragraphs' in item['model']:
                        req_optional += [req for req in item['model']['paragraphs']]
                    elif 'bullets' in item['model']:
                        req_optional += [req for req in item['model']['bullets']]
        
        elif section['sectionType'] == 'development-practices':
            dev_practices = [resp for resp in section['model']['items']]

        elif section['sectionType'] == 'responsibilities':
            if 'bullets' in section['model']:
                responsibilities += [resp for resp in section['model']['bullets']]
            elif 'paragraphs' in section['model']:
                responsibilities += [resp for resp in section['model']['paragraphs']]
            
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
    new_dict['salary_from'] = salary_from
    new_dict['salary_to'] = salary_to
    new_dict['salary_currency'] = salary_currency
    new_dict['salary_long_form'] = salary_long_form
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

def listing_pipeline(url,file_name):
    ''' Pipeline saves listing details to file'''
    pipeline = (scrape_listing_from_json(url)
        | clean_listing_string
        | change_str_to_dict
        | extract_data(url)
        | save_to_file(file_name))
    return pipeline





def main(url, file_name):
    '''Runs if script called directly'''
    my_dict = scrape_single_listing(url)
    #print(my_dict)
    new_dict = extract_data(my_dict, url)
    #print(new_dict)
    save_dict(new_dict,file_name)

if __name__ == '__main__':
    
    
    url = 'https://www.pracuj.pl/praca/mlodszy-specjalista-mlodsza-specjalistka-ds-helpdesk-warszawa,oferta,1002430993'
    listings_data = 'listings_data.txt'
    failed_urls = 'failed_urls.txt'
    count_succes = 0
    count_failure = 0

    with open(listings_data, 'r', encoding='UTF-8') as file:
    

    with open('failed extractions.txt', 'r', encoding='UTF-8') as file:
        # Try to extract each listing using pipeline. If failed, record in serepate file  
        for url in file:
            url = url.strip()
            sleep(random.uniform(7, 23))
            try:
                result = listing_pipeline(url, file_name)()
                count_succes += 1
                print(f'Success: {count_succes}')
            except:
                count_failure += 1
                print(f'Failures: {count_failure}')
                with open(failed_urls, 'a', encoding='UTF-8') as file_2:
                    file_2.write(url + '\n')


    '''
    url = 'https://www.pracuj.pl/praca/mlodszy-specjalista-mlodsza-specjalistka-ds-helpdesk-warszawa,oferta,1002430993'
    file_name = 'succesfull extractions_2.txt'
    main(url, file_name)
    '''
    '''

    file_with_extracted = 'succesfull extractions_2.txt'
    file_with_failed = 'failed extractions_2.txt'
    #restarting_extraction = 'https://www.pracuj.pl/praca/konsultant-ds-wdrozen-oprogramowania-mazowieckie,oferta,9756334'
    count_succes = 0
    count_failure = 0
    # Open the file for reading
    with open('failed extractions.txt', 'r', encoding='UTF-8') as file:
        # Try to extract each listing. If failed, record in serepate file
        
        for line in file:
            line = line.strip()
            if restarting_extraction in line:
                # Found the specific content, start iterating from this line
                break
        
        for url in file:
            url = url.strip()
            sleep(random.uniform(7, 23))
            try:
                main(url, file_with_extracted)
                count_succes += 1
                print(f'Success: {count_succes}')
            except:
                count_failure += 1
                print(f'Failures: {count_failure}')
                with open(file_with_failed, 'a', encoding='UTF-8') as file:
                    file.write(url + '\n')
    '''


'''
def scrape_all_listings_data():
    Scrapes json data about job listings, save to text file
    unique_links = set()
    finished_links = set()
    finished_count = 0

    # Open the file for reading
    with open('links_to_listings.txt', 'r', encoding='UTF-8') as file:
            # Read the lines into a set, removing any leading or trailing whitespace
            unique_links = set(line.strip() for line in file)

    # Open the file for reading
    with open('finished_listings.txt', 'r', encoding='UTF-8') as file:
            # Read the lines into a set, removing any leading or trailing whitespace
            finished_links = set(line.strip() for line in file)

    #Remaining links to do
    remaining_listings = unique_links - finished_links
    total = len(remaining_listings)
    one_percent = int(total / 100)

    for link in remaining_listings:
        sleep(random.uniform(2, 5))
        
        # Append file containing all job listing
        with open('listings_json_data.txt', 'a',encoding='UTF-8') as file:
                    file.write(scrape_single_listing(link) + '\n')
        with open('finished_listings.txt', 'a',encoding='UTF-8') as file:
                    file.write(link + '\n')
        
        #Print if a round percent is finished
        finished_count += 1
        if finished_count % one_percent == 0:
            print(finished_count / one_percent)

def extract_usefull_listings(skills_list):
    Extract listings that have my skills
    # Patterns for skills_slist = ['Python', 'SQL', 'R']
    # Designed to find SQL
    pattern_1 = r'%s'
    # Designed to find R language
    pattern_2 = r'\b%s\b'

    patterns_list = [pattern_1 % skills_list[0], pattern_1 % skills_list[1],
    pattern_2 % skills_list[2]]

    with open('listings_json_data.txt', 'r',encoding='UTF-8') as input_file, \
    open('listings_matching_skills.txt', 'a',encoding='UTF-8') as output_file:
        #Find all JSON that contain my skills
        matches = set()
        for pattern in patterns_list:
            # Set comprehensioin to filter out listings with my skills
            new_matches = {line for line in input_file if re.search(pattern, line)}
            
            # Merge the sets of matches
            matches |= new_matches

            # Reset the input file pointer to the beginning
            input_file.seek(0)

            # Print the number of unique matches for this pattern
            print(f"Pattern {pattern}: {len(new_matches)} unique matches")
        # Write the matching lines to the output file
        for match in matches:
            output_file.write(match)
'''