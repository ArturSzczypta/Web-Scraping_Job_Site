''' Scrape job listings in it.pracuj.pl and save to database'''

from pathlib import Path

import csv
import logging
from scripts import logging_functions as lf
from scripts import scrape_urls as scrape_urls
from scripts import scrape_listings as scrape_listings
from scripts import mongodb_functions as mongodb
from scripts import email_functions as ef


current_file_name = Path(__file__).stem
log_file_name = f'{current_file_name}_log.log'

BASE_DIR = Path(__file__).parent
LOGGING_FILE = BASE_DIR / 'logging_files' / log_file_name
LOGGING_JSON = BASE_DIR / 'logging_files' / 'logging_config.json'

lf.configure_logging(LOGGING_JSON, LOGGING_FILE)

TXT_DIR = BASE_DIR / 'txt_files'
FOR_SEARCH = TXT_DIR / 'for_search.csv'
LAST_DATE_LOG = TXT_DIR / 'last_date.log'
SCRAPPED_URLS = TXT_DIR / 'scrapped_urls.txt'
TECH_SEARCHED_FOR = TXT_DIR / 'technologies.txt'
SUCCESFULL_EXTRACTIONS = TXT_DIR / 'succesfull_extractions.txt'
FAILED_EXTRACTIONS = TXT_DIR / 'failed_extractions.txt'
INVALID_JSON = TXT_DIR / 'invalid_json.txt'
MANUAL_URLS = TXT_DIR / 'manual_url_scraping'

# Check if there are any files in the directory
manual_files = Path(MANUAL_URLS).iterdir()
manual_files_exist = any(file.is_file() for file in manual_files)


# For Search, _BASE_URL will be used first, then _ITERABLE_URL untill the end
BASE_URL = 'https://it.pracuj.pl/praca?{}'
ITERABLE_URL = 'https://it.pracuj.pl/praca?pn={}&{}'

# Get search parameters from csv file
searched_set = set()
with open(FOR_SEARCH, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=',')
    for row in reader:
        if 'Search' in row:
            searched_set.update({row['Search']: row['Search']})


scrape_urls.main(LAST_DATE_LOG, searched_set, SCRAPPED_URLS, BASE_URL,
                 ITERABLE_URL, MANUAL_URLS, manual_files_exist)

# Scraping job listings from job site
scrape_listings.main(SCRAPPED_URLS, TECH_SEARCHED_FOR,
                     SUCCESFULL_EXTRACTIONS, FAILED_EXTRACTIONS)


client = mongodb.return_db_client()
try:
    mongodb.command_ping(client)
except Exception as e:
    logging.critical(f'MongoDB - Unable to connect with database - {repr(e)}')
    ef.send_error_email('MongoDB - Unable to connect with database')

db = client['Web_Scraping_Job_Site']
collection_succesfull = db['Job_Listings']
collection_failed = db['Failed_Urls']

# Record if there was a failure, clear files
try:
    mongodb.save_dict_from_file_to_collection(collection_succesfull,
                                              SUCCESFULL_EXTRACTIONS,
                                              INVALID_JSON)

    # Preparing email
    with open(SUCCESFULL_EXTRACTIONS, 'r') as file:
        succesfull = sum(1 for _ in file)
    with open(FAILED_EXTRACTIONS, 'r') as file:
        failed = sum(1 for _ in file)
    project_folder = BASE_DIR.name
    subject = f'Summary of executing {project_folder}'
    message = f'''Scraping Succesfull \n
    Succesfull Extractions: {succesfull}\n
    Failed Extractions:     {failed}\n
    Database updated.'''

    ef.send_email(subject, message)

    with open(SUCCESFULL_EXTRACTIONS, 'w', encoding='utf-8') as file:
        file.truncate(0)

except Exception as e:
    logging.critical(f'MongoDB - Cannot save documents to database'
                     f' - {repr(e)}')
    ef.send_error_email('MongoDB - Cannot save documents to database')
