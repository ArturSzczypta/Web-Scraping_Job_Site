'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import os
from pathlib import Path
import re
import json
from time import sleep, gmtime, strftime
from numpy import random
import requests
import copy
import datetime as dt
import logging
import logging_functions as lf


def save_dict(new_dict: dict, file_path: str) -> None:
    ''' Saves dictionary to file'''
    json_str = json.dumps(new_dict, ensure_ascii=False)
    # file_path = os.path.join(os.path.dirname(__file__),\
    # '..', 'text_and_json', file_name)

    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(json_str + '\n')


def scrape_listing(url: str, timeout=5) -> str:
    ''' Scrapes job listing details from JSON to substring'''
    response = requests.get(url, timeout=timeout)
    substring = response.content.decode('utf-8', errors='ignore')
    return substring


def clean_listing_string(substring: str) -> str:
    ''' Cleans substring from problematic symbols, patterns, sequences'''

    substring = substring.strip()

    sequences = r'\\n|\\t|\\r|\\b|\\f|\\"'
    substring = re.sub(sequences, ' ', substring)

    not_polish = r'[^\w,:\.\'"\-(){}\[\]%\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+'
    substring = re.sub(not_polish, ' ', substring)

    incorrect_null = r'\bundefined\b'
    substring = re.sub(incorrect_null, 'null', substring)

    missing_nulls = r':\s*(,|"\s*"|\]|\[\s*\]|\}|\{\s*\})'
    substring = re.sub(missing_nulls, ':null', substring)

    missing_commas_1 = r'null\s*([^,\]\}])'
    substring = re.sub(missing_commas_1, r'null,\g<1>', substring)
    missing_commas_2 = r'(\w+)\s+,\s*"'
    substring = re.sub(missing_commas_2, r'\1","', substring)

    extra_char_1 = r'(?<=",)\s*",(?=")'
    substring = re.sub(extra_char_1, '', substring)

    # Remove special whitespace characters
    substring = re.sub(r'\s', ' ', substring)

    substring = substring.replace('u002F', ' ')
    substring = substring.replace('u003E', ' ')
    substring = substring.replace('--', ' ')
    substring = substring.replace(', \"\"', ' ')

    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    substring = re.sub(r'\s*"\s*', '"', substring)

    return substring


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


def string_to_mumer(num_str):
    '''Convert string to int or float, depending on content'''
    if ',' in num_str:
        num_str = num_str.replace(',', '.')

    # If the string has '.' now, convert to float
    if '.' in num_str:
        try:
            return float(num_str)
        except ValueError:
            logging.error(f'Unable to change {num_str} to float')
    else:
        try:
            return int(num_str)
        except ValueError:
            logging.error(f'Unable to change {num_str} to int')        


def create_dictionary(substring, url) -> dict:
    ''' Extracts usefull data from the dictionary, creates new dictionary'''

    language = re.search(r'"jobOfferLanguage":{"isoCode":"(.*?)"', substring).group(1)
    job_title = re.search(r'"jobTitle":"(.*?)"', substring).group(1)
    country = re.search(r'"country":\{"id":\d+,"name":"(.*?)"', substring).group(1)
    region = re.search(r'"region":\{"id":\d+,"name":"(.*?)"', substring).group(1)
    location = re.search(r'"location":\{"id":\d+,"name":"(.*?)"', substring).group(1)

    position_level_match = re.search(r'"positionLevels":\[\{"id":\d+,"name":"(.*?)"', substring)
    work_schedule_match = re.search(r'"workSchedules":\[\{"id":\d+,"name":"(.*?)"', substring)
    contract_type_match = re.search(r'"typesOfContracts":\[\{"id":\d+,"name":"(.*?)"', substring)
    position_level = position_level_match.group(1) if position_level_match else None
    work_schedule = work_schedule_match.group(1) if work_schedule_match else None
    contract_type = contract_type_match.group(1) if contract_type_match else None

    work_modes_str = re.search(r'"workModes":\[(.*?)\]', substring)
    work_modes = re.findall(r'"code":"(.*?)"', work_modes_str.group(1)) if work_modes_str else None

    salary = re.search(r'"salary":\{"from":(.*?),"to":(.*?),"currency":\{"code":"(.*?)"', substring)
    if salary:
        salary_min = string_to_mumer(salary.group(1)) if salary.group(1) else None
        salary_max = string_to_mumer(salary.group(2)) if salary.group(2) else None
        currency = salary.group(3) if salary.group(3) else None
        salary_k_str = re.search(r'"salaryKind":.*?"name":"(.*?)"', substring)
        salary_kind = salary_k_str.group(1) if salary_k_str else None
    else:
        salary_min = None
        salary_max = None
        currency = None
        salary_kind = None
    
    time_match = re.search(r'"timeUnit":\{"id":\d+,"shortForm":\{"name":"(.*?)."', substring)
    time_unit = time_match.group(1) if time_match else None

    sec_att_str = re.search(r'"secondaryAttributes":.*?\[(.*?)]', substring)
    secondary_attrib = re.findall(r'"name":"(.*?)"', sec_att_str.group(1)) if sec_att_str else None

    tech_exp_str = re.search(r'"sectionType":"technologies-expected".*?\[(.*?)]', substring)
    tech_expected = re.findall(r'"name":"(.*?)"', tech_exp_str.group(1)) if tech_exp_str else None

    tech_opt_str = re.search(r'"dictionaryName":"technologies-optional".*?\[(.*?)]', substring)
    tech_optional = re.findall(r'"name":"(.*?)"', tech_opt_str.group(1)) if tech_opt_str else None

    initial_publication = re.search(r'"dateOfInitialPublicationUtc":"(.*?)"', substring).group(1)
    last_publication = re.search(r'"lastPublishedUtc":"(.*?)"', substring).group(1)
    expiration_date = re.search(r'"expirationDateUtc":"(.*?)"', substring).group(1)

    respon_match = re.search(r'"sectionType":"responsibilities".*?\[(.*?)\]', substring)
    if respon_match:
        respon_match = respon_match.group(1).replace('.','')
        responsibilities = respon_match.split('\",\"')
        responsibilities[0] = responsibilities[0].lstrip('"')
        responsibilities[-1] = responsibilities[-1].rstrip('"')
    else:
        responsibilities = None

    req_e_match = re.search(r':"requirements-expected".*?\[(.*?)\]', substring)
    if req_e_match:
        req_e_match = req_e_match.group(1).replace('.','')
        requierements_expected = req_e_match.split('\",\"')
        requierements_expected[0] = requierements_expected[0].lstrip('"')
        requierements_expected[-1] = requierements_expected[-1].rstrip('"')
    else:
        requierements_expected = None

    req_o_match = re.search(r':"requirements-optional".*?\[(.*?)\]', substring)
    if req_o_match:
        req_o_match = req_o_match.group(1).replace('.','')
        requierements_optional = req_o_match.split('\",\"')
        requierements_optional[0] = requierements_optional[0].lstrip('"')
        requierements_optional[-1] = requierements_optional[-1].rstrip('"')
    else:
        requierements_optional = None

    work_org_match = re.search(r'"sectionType":"offered".*?\[(.*?)\]', substring)
    if work_org_match:
        work_org_match = work_org_match.group(1).replace('.','')
        work_organization = work_org_match.split('\",\"')
        work_organization[0] = work_organization[0].lstrip('"')
        work_organization[-1] = work_organization[-1].rstrip('"')
    else:
        work_organization = None

    recruit_match = re.search(r':"recruitment-stages".*?\[(.*?)\]', substring)
    if recruit_match:
        recruit_match = recruit_match.group(1).replace('.','')
        recruitment_stages = recruit_match.split('\",\"')
        recruitment_stages[0] = recruitment_stages[0].lstrip('"')
        recruitment_stages[-1] = recruitment_stages[-1].rstrip('"')
    else:
        recruitment_stages = None

    par_match = re.search(r'"paragraphs":\[(.*?)\]', substring)
    if par_match:
        par_match = par_match.group(1).replace('.','').replace('\",\"\",\"','\",\"')
        paragraphs = par_match.split('\",\"')
        paragraphs[0] = paragraphs[0].lstrip('"')
        paragraphs[-1] = paragraphs[-1].rstrip('"')
    else:
        paragraphs = None

    job_benefits_str = re.search(r'"sectionType":"benefits","number":.*?\[(.*?)\]', substring)
    job_benefits = re.findall(r'"name":"(.*?)"', job_benefits_str.group(1)) if job_benefits_str else None

    training_space_str = re.search(r'"sectionType":"training-space".*?\[(.*?)\]', substring)
    oportunities = re.findall(r'"name":"(.*?)"', training_space_str.group(1)) if training_space_str else None

    offer_dict = dict()
    offer_dict['url'] = url
    offer_dict['language'] = language
    offer_dict['job_title'] = job_title
    offer_dict['country'] = country
    offer_dict['region'] = region
    offer_dict['location'] = location
    offer_dict['position_level'] = position_level
    offer_dict['work_schedule'] = work_schedule
    offer_dict['contract_type'] = contract_type
    offer_dict['work_modes'] = work_modes
    offer_dict['salary_min'] = salary_min
    offer_dict['salary_max'] = salary_max
    offer_dict['currency'] = currency
    offer_dict['salary_kind'] = salary_kind
    offer_dict['time_unit'] = time_unit
    offer_dict['secondary_attrib'] = secondary_attrib
    offer_dict['tech_expected'] = tech_expected
    offer_dict['tech_optional'] = tech_optional
    offer_dict['initial_publication'] = initial_publication
    offer_dict['last_publication'] = last_publication
    offer_dict['expiration_date'] = expiration_date
    offer_dict['responsibilities'] = responsibilities
    offer_dict['requierements_expected'] = requierements_expected
    offer_dict['requierements_optional'] = requierements_optional
    offer_dict['work_organization'] = work_organization
    offer_dict['recruitment_stages'] = recruitment_stages
    offer_dict['paragraphs'] = paragraphs
    offer_dict['job_benefits'] = job_benefits
    offer_dict['oportunities'] = oportunities

    #print(json.dumps(offer_dict, ensure_ascii=False, indent=2))
    return offer_dict


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
        logging.info(f'New listings: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')


def listing_pipeline_main(substring, url, succesfull_urls, dict_path) -> None:
    ''' Pipeline saves listing details to file'''
    substring = clean_listing_string(substring)   
    offer_dict = create_dictionary(substring, url) 
    save_dict_to_file(offer_dict, dict_path)
    save_str_to_file(url, succesfull_urls)


def main(scraped_urls, file_with_tech, succesfull_urls, failed_urls,
         succesfull_file, failed_file, sleep_min=4, sleep_max=7) -> None:
    ''' Main method of scrape_listings.py runs if script called directly'''
    succeses = 0
    failures = 0
    progress = 0
    last_progress = 0
    url_count = get_url_count(scraped_urls)
    progress_per_url = 1 / url_count * 100

    # Calculate estimated time
    aver_sleep = (sleep_min + sleep_max) / 2
    work_per_url = 0.099 # Estimate from running on single core, on a weak CPU
    seconds_left = (aver_sleep + work_per_url) * url_count
    estimated_datetime = dt.datetime.now() + dt.timedelta(seconds=seconds_left)
    days_left = seconds_left // 86400
    time_left = strftime("%H:%M:%S", gmtime(int(seconds_left)))
    print(f'Listing Scraping - Estimated time: {days_left:2} '
          f'days and {time_left:8}'
          f'     {estimated_datetime.strftime("%Y-%m-%d %H:%M:%S")}')

    # Extract all technologies in file to a set
    #_tech_set = extract_tech_set(file_with_tech)

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
                substring = scrape_listing(url)
            except Exception as e:
                save_str_to_file(url, failed_urls)
                failures += 1
                logging.error(f'Opening url failed: {url} - {repr(e)}')
                sleep(random.uniform(sleep_min, sleep_max))
                continue

            try:
                listing_pipeline_main(substring, url, succesfull_urls, succesfull_file)
                succeses += 1
            except Exception as e:
                save_str_to_file(url, failed_urls)
                save_str_to_file(f'{substring}\n\n', failed_file)
                failures += 1
                logging.error(f'Cleaning listing failed: {url} - {repr(e)}')
            finally:
                # Print progress if console is set to DEBUG or INFO
                if console_level < 30:
                    days_left = int(seconds_left // 86400)
                    time_left = strftime("%H:%M:%S", gmtime(int(seconds_left)))

                    if console_level == 10:
                        print(f'Successes: {succeses:5}     '
                              f'Failures: {failures:5}     '
                              f'Progress: {progress:6}%     '
                              f'Time left: {days_left:2} days {time_left:8}')

                    if console_level == 20 and \
                            int(progress) > last_progress:
                        last_progress = copy.deepcopy(int(progress))
                        print(f'Successes: {succeses:5}     '
                              f'Failures: {failures:5}     '
                              f'Progress: {progress:5}%     '
                              f'Time left: {days_left:2} days {time_left:8}')
                sleep(random.uniform(sleep_min, sleep_max))


if __name__ == '__main__':

    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    BASE_DIR = Path(__file__).parent.parent
    LOGGING_FILE = BASE_DIR / 'logging_files' / log_file_name
    LOGGING_JSON = BASE_DIR / 'logging_files' / 'logging_config.json'

    lf.configure_logging(LOGGING_JSON, LOGGING_FILE)

    TXT_DIR = BASE_DIR / 'txt_files'
    SCRAPPED_URLS = TXT_DIR / 'scrapped_urls.txt'
    TECH_SEARCHED_FOR = TXT_DIR / 'technologies.txt'
    SUCCESFULL_URLS = TXT_DIR / 'succesfull_urls.txt'
    FAILED_URLS = TXT_DIR / 'failed_urls.txt'
    SUCCESFULL_EXTRACTIONS = TXT_DIR / 'succesfull_extractions.txt'
    FAILED_EXTRACTIONS = TXT_DIR / 'failed_extractions.txt'

    # Scraping job listings from job site
    main(SCRAPPED_URLS, TECH_SEARCHED_FOR, SUCCESFULL_URLS, FAILED_URLS,
         SUCCESFULL_EXTRACTIONS, FAILED_EXTRACTIONS)

'''
# Job ofers abroad will usualy fail. It is not relevant as all offers
# from abroad are out of scope of the project
url = 'https://www.pracuj.pl/praca/technical-support-specialist-with-english-wroclaw-slezna-132,oferta,1003863101'
substring = scrape_listing(url)
substring = clean_listing_string(substring)
new_dict = create_dictionary(substring, url)
print(json.dumps(new_dict, ensure_ascii=False, indent=2))
#print(substring)
'''
