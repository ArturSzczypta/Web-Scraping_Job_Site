''' Scrape it.pracuj.pl job listings to database'''
import os
import logging
from logging import config
from scripts import logging_functions as l
from scripts import scrape_urls as scrape_urls
from scripts import scrape_listings as scrape_listings
from scripts import mongodb_functions as mongodb
from scripts import email_functions as e

#Performs basic logging set up
#Get this script name
log_file_name = __file__.split('\\')
log_file_name = f'{log_file_name[-1][:-3]}_log.log'

l.get_log_file_name(log_file_name)

#Configure logging file
l.configure_logging()
logger = logging.getLogger(__name__)

#Scraping Urls from job site
# Specialisations start with 's=', technologies with 'tt=', spaces replaced by '+'
searched_set = {'s=data+science', 's=big+data', 'tt=Python', 'tt=SQL', 'tt=R', 'tt=Tableau'}

# _BASE_URL will be used first, then _ITERABLE_URL untill the end
BASE_URL = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn=1'
ITERABLE_URL = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn='
LAST_DATE_LOG = 'last_date.log'
SCRAPPED_URLS = os.path.join(os.getcwd(), 'text_and_json/scrapped_urls.txt')
# Calling script
scrape_urls.main(LAST_DATE_LOG, searched_set, SCRAPPED_URLS, BASE_URL, ITERABLE_URL)

#Scraping Listings using urls
# Required files
TECH_SEARCHED_FOR = 'technologies.txt'
SUCCESFULL_EXTRACTIONS = os.path.join(os.getcwd(), 'text_and_json/succesfull_extractions.txt')
FAILED_EXTRACTIONS = os.path.join(os.getcwd(), 'text_and_json/failed_extractions.txt')
# Calling script
scrape_listings.main(SCRAPPED_URLS, TECH_SEARCHED_FOR, SUCCESFULL_EXTRACTIONS, FAILED_EXTRACTIONS)

#Saving extraction results to MongoDB Atlas
# Connect to DB
client = mongodb.return_db_client()

# Check connection to DB
try:
    mongodb.command_ping(client)
except:
    logger.critical('MongoDB - Unable to connect with database')
    e.send_error_email('MongoDB - Unable to connect with database')

db = client['Web_Scraping_Job_Site']
collection_succesfull = db['Job_Listings']
collection_failed = db['Failed_Urls']

# Record if there was a failure, clear files
try:
    mongodb.save_dict_from_file_to_collection(collection_succesfull, SUCCESFULL_EXTRACTIONS)
    #mongodb.save_str_from_file_to_collection(collection_failed, FAILED_EXTRACTIONS)
    
    # Preparing email
    with open(SUCCESFULL_EXTRACTIONS, 'r') as file:
        succesfull = sum(1 for _ in file)
    with open(FAILED_EXTRACTIONS, 'r') as file:
        failed = sum(1 for _ in file)
    parent_path = os.path.dirname(__file__)
    parent_directory = os.path.basename(parent_path)
    subject = f'Summary of executing {parent_directory}'
    message = f'''Scraping Succesfull \n
    Succesfull Extractions: {succesfull}\n
    Failed Extractions:     {failed}\n
    Database updated.'''
    # Send email
    e.send_email(subject, message)
    '''
    #Clearing listing file
    with open(SUCCESFULL_EXTRACTIONS, 'w', encoding='utf-8') as file:
        file.truncate(0)
    '''
except:
    logger.critical('MongoDB - Cannot save documents to database')
    e.send_error_email('MongoDB - Cannot save documents to database')
