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
    pattern = r'null\s*([^,\]}])'
    return re.sub(pattern, r'null,\g<1>', data_string)

def scrape_single_listing(url):
    ''' Scrapes job listing details from the url, return a dictionary'''
    #sleep(random.uniform(7, 23))
    #try:
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
    #print(substring)
    
    # Remove all unicode escape sequences
    #substring = unicodedata.normalize('NFKD', substring)
    #substring = re.sub(r'\\[uU][0-9a-fA-F]{4}', '', substring)
    # Remove sequences
    substring = re.sub(r'\\n|\\t|\\r', ' ', substring)
    substring = substring.strip() # remove any trailing or leading white spaces
    substring = re.sub(r'\s+', ' ', substring) # replace consecutive white spaces with a single white space
    #substring = substring.replace('\\', '\\\\') # escape any backslashes in the string
    substring = replace_empty(substring)
    substring = add_missing_commas(substring)
    # Remove all quotes inside future dictionary kays and list objects
    #substring = re.sub(r':\s*"([^"]*)"(?=\s*,)', r': "\1"', substring)
    #substring = re.sub(r'\[\s*"([^"]*)"(?=\s*,)', r'[\1', substring)
    #substring = re.sub(r',\s*"([^"]*)"(?=\s*,|\s*\])', r', "\1"', substring)
    #substring = re.sub(r',\s*"([^"]*)"(?=\s*\])', r', \1]', substring)

    # Replace any non-alphanumeric or non-allowed characters with space
    substring = re.sub(r'[^\w,:\.\'"\-(){}\[\]\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+', '', substring)
    substring = substring.replace("u002F", " ")
    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    print(substring)

    # Convert the string to a dictionary using the json module
    my_dict = json.loads(substring)
    print(json.dumps(my_dict, ensure_ascii=False, indent=2))
    print('\n\n')
    return my_dict
    #except:
    print(f'failed to get JSON from url {url}')
    print('\n\n')

def extract_data(my_dict, url):
    ''' Extracts usefull data from the dictionary, creates new dictionary'''
    #Basic listing data
    job_title = my_dict['offerReducer']['offer']['jobTitle']
    country = my_dict['offerReducer']['offer']['workplaces'][0]['country']['name']
    region = my_dict['offerReducer']['offer']['workplaces'][0]['region']['name']
    location = my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location']['name']
    contract_type = my_dict['offerReducer']['offer']['typesOfContracts'][0]['name']
    is_salary = None
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

    # technologies
    tech_expected = [tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][0]['model']['customItems']]
    tech_optional = None
    if len(my_dict['offerReducer']['offer']['sections'][0]['subSections']) > 1:
        tech_optional = [tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][1]['model']['customItems']]
    '''
    # responsibilities
    if my_dict['offerReducer']['offer']['sections'][1]['sectionType'] == 'responsibilities':
        resp_expected = [resp for resp in my_dict['offerReducer']['offer']['sections'][1]['model']['bullets']]
    elif my_dict['offerReducer']['offer']['sections'][2]['sectionType'] == 'responsibilities':
        resp_expected = [resp for resp in my_dict['offerReducer']['offer']['sections'][2]['model']['bullets']]
    else:
        resp_expected = [resp for resp in my_dict['offerReducer']['offer']['sections'][3]['model']['bullets']]

    # requirements
    if my_dict['offerReducer']['offer']['sections'][1]['sectionType'] == 'requirements-expected':
        req_expected = [req for req in my_dict['offerReducer']['offer']['sections'][1]['subSections'][0]['model']['bullets']]
        req_optional = None
        if len(my_dict['offerReducer']['offer']['sections'][1]['subSections']) > 1:
            req_optional = [req for req in my_dict['offerReducer']['offer']['sections'][1]['subSections'][1]['model']['bullets']]
    elif my_dict['offerReducer']['offer']['sections'][2]['sectionType'] == 'requirements-expected':
        req_expected = [req for req in my_dict['offerReducer']['offer']['sections'][2]['subSections'][0]['model']['bullets']]
        req_optional = None
        if len(my_dict['offerReducer']['offer']['sections'][2]['subSections']) > 1:
            req_optional = [req for req in my_dict['offerReducer']['offer']['sections'][2]['subSections'][1]['model']['bullets']]
    else:
        req_expected = [req for req in my_dict['offerReducer']['offer']['sections'][3]['subSections'][0]['model']['bullets']]
        req_optional = None
        if len(my_dict['offerReducer']['offer']['sections'][3]['subSections']) > 1:
            req_optional = [req for req in my_dict['offerReducer']['offer']['sections'][3]['subSections'][1]['model']['bullets']]
    '''
    tech_expected = None
    tech_optional = None
    req_expected = None
    req_optional = None
    dev_practices = None
    responsibilities = None

    for section in my_dict['offerReducer']['offer']['sections']:
        if section['sectionType'] == 'technologies':
            for item in section['subSections']:
                if item['sectionType'] == 'technologies-expected':
                    tech_expected = [tech['name'] for tech in item['model']['customItems']]
                    #print(tech_expected)
                elif item['sectionType'] == 'technologies-optional':
                    tech_optional = [tech['name'] for tech in item['model']['customItems']]
                    #print(tech_optional)
                else:
                    print('check section[sectionType] == technologies')
        
        elif section['sectionType'] == 'requirements':
            #print(section)
            for item in section['subSections']:
                if item['sectionType'] == 'requirements-expected':
                    #print(item['model']['bullets'])
                    req_expected = [req for req in item['model']['bullets']]
                elif item['sectionType'] == 'requirements-optional':
                    req_optional = [req for req in item['model']['bullets']]
                else:
                    print('check section[sectionType] == requirements')
        
        elif section['sectionType'] == 'development-practices':
            dev_practices = [resp for resp in section['model']['items']]

        elif section['sectionType'] == 'responsibilities':
            responsibilities = [resp for resp in section['model']['paragraphs']]

    #Creating a new, simplified dictionary for saving
    new_dict = {}
    #Basic listing data
    new_dict['url'] = url
    new_dict['job_title'] = job_title
    new_dict['country'] = country
    new_dict['region'] = region
    new_dict['location'] = location
    new_dict['contract_type'] = contract_type

    new_dict['is_salary'] = is_salary
    new_dict['salary_from'] = salary_from
    new_dict['salary_to'] = salary_to
    new_dict['salary_currency'] = salary_currency
    new_dict['salary_long_form'] = salary_long_form
    # Assuming both dates always comply to ISO 8601 format, UTC time zone
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
    
    print(json.dumps(new_dict, ensure_ascii=False, indent=2))
    return new_dict

def save_dict(new_dict,file_name):
    ''' Saves dictionary to file'''
    json_str = json.dumps(new_dict, ensure_ascii=False)

    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(json_str + '\n')

def main(url, file_name):
    '''Runs if script called directly'''
    my_dict = scrape_single_listing(url)
    #print(my_dict)
    new_dict = extract_data(my_dict, url)
    #print(new_dict)
    save_dict(new_dict,file_name)

if __name__ == '__main__':
    url = 'https://www.pracuj.pl/praca/bi-developer-wroclaw,oferta,1002411353'
    file_name = 'succesfull extractions.txt'
    main(url, file_name)
    '''
    file_with_extracted = 'succesfull extractions.txt'
    file_with_failed = 'failed extractions.txt'
    # Open the file for reading
    with open('links_to_listings.txt', 'r', encoding='UTF-8') as file:
        # Try to extract each listing. If failed, record in serepate file
        for url in file:
            url = url.strip()
            try:
                main(url, file_with_extracted)
            except:
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