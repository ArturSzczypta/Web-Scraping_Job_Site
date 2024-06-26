''' Scrape job listings in it.pracuj.pl and save to database'''
import os
import csv

import logging
from logging import config
from scripts import logging_functions as l
from scripts import scrape_urls as scrape_urls
from scripts import scrape_listings as scrape_listings
from scripts import mongodb_functions as mongodb
from scripts import email_functions as e

#Create log file name based on script name
log_file_name = os.path.basename(__file__).split('.')
log_file_name = f'{log_file_name[0]}_log.log'

l.get_log_file_name(log_file_name)

#Configure logging file
l.configure_logging()
logger = logging.getLogger(__name__)

# Required files
TXT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'txt_files')
FOR_SEARCH = os.path.join(TXT_DIR,'for_search.csv')
LAST_DATE_LOG = os.path.join(TXT_DIR,'last_date.log')
SCRAPPED_URLS = os.path.join(TXT_DIR,'scrapped_urls.txt')
TECH_SEARCHED_FOR = os.path.join(TXT_DIR,'technologies.txt')
SUCCESFULL_EXTRACTIONS = os.path.join(TXT_DIR, 'succesfull_extractions.txt')
FAILED_EXTRACTIONS = os.path.join(TXT_DIR, 'failed_extractions.txt')
INVALID_JSON = os.path.join(TXT_DIR, 'invalid_json.txt')

# Manually scrapped website search resutls
MANUAL_URLS = os.path.join(TXT_DIR,'manual_url_scraping')
# Check if there are any files in the directory
files = os.scandir(MANUAL_URLS)
manual_files_exist = any(file.is_file() for file in files)


# For Search, _BASE_URL will be used first, then _ITERABLE_URL untill the end
BASE_URL = 'https://it.pracuj.pl/praca?{}'
ITERABLE_URL = 'https://it.pracuj.pl/praca?pn={}&{}'

# Get search parameters from csv file
searched_set = set()
with open(FOR_SEARCH, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=',')
    for row in reader:
        if 'Search' in row:
            searched_set.update({row['Search']:row['Search']})

# Scraping Urls from job site
#scrape_urls.main(LAST_DATE_LOG, searched_set, SCRAPPED_URLS, BASE_URL, ITERABLE_URL, MANUAL_URLS, manual_files_exist)

# Scraping job listings from job site
scrape_listings.main(SCRAPPED_URLS, TECH_SEARCHED_FOR, SUCCESFULL_EXTRACTIONS, FAILED_EXTRACTIONS)
'''
#Saving extraction results to MongoDB Atlas
# Connect to DB
client = mongodb.return_db_client()

# Check connection to DB
try:
    mongodb.command_ping(client)
except:
    logger.critical('MongoDB - Unable to connect with database')
    l.save_to_log_file(__name__, __file__, 'MongoDB - Unable to connect with database')
    e.send_error_email('MongoDB - Unable to connect with database')

db = client['Web_Scraping_Job_Site']
collection_succesfull = db['Job_Listings']
collection_failed = db['Failed_Urls']

# Record if there was a failure, clear files
try:
    mongodb.save_dict_from_file_to_collection(collection_succesfull, SUCCESFULL_EXTRACTIONS, INVALID_JSON)
    
    # Preparing email
    with open(SUCCESFULL_EXTRACTIONS, 'r') as file:
        succesfull = sum(1 for _ in file)
    with open(FAILED_EXTRACTIONS, 'r') as file:
        failed = sum(1 for _ in file)
    parent_path = os.path.dirname(__file__)
    parent_directory = os.path.basename(parent_path)
    subject = f'Summary of executing {parent_directory}'
    message = fScraping Succesfull \n
    Succesfull Extractions: {succesfull}\n
    Failed Extractions:     {failed}\n
    Database updated.
    # Send email
    e.send_email(subject, message)
    
    #Clearing listing file
    with open(SUCCESFULL_EXTRACTIONS, 'w', encoding='utf-8') as file:
        file.truncate(0)
    
except:
    logger.critical('MongoDB - Cannot save documents to database')
    l.save_to_log_file(__name__, __file__, 'MongoDB - Cannot save documents to database')
    e.send_error_email('MongoDB - Cannot save documents to database')
'''