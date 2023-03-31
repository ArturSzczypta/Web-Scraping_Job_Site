''' Scrape it.pracuj.pl job listings to database'''
import logging
from logging import config
import logging_functions as l
import scrape_urls
import scrape_listings
import db_functions_mongodb as mongodb

#Performs basic logging set up
#Get this script name
log_file_name = __file__.split('\\')
log_file_name = f'{log_file_name[-1][:-3]}_log.log'

l.get_log_file_name(log_file_name)

#Configure logging file
l.configure_logging()
logger = logging.getLogger('main')

#Scraping Urls from job site
# Specialisations start with 's=', technologies with 'tt=', spaces replaced by '+'
searched_set = {'s=data+science', 's=big+data', 'tt=Python', 'tt=SQL', 'tt=R'}

# _BASE_URL will be used first, then _ITERABLE_URL untill the end
BASE_URL = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn=1'
ITERABLE_URL = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn='
LAST_DATE_LOG = 'last_date.log'
SCRAPPED_URLS = 'scrapped_urls.txt'
# Calling script
scrape_urls.main(LAST_DATE_LOG, searched_set, SCRAPPED_URLS, BASE_URL, ITERABLE_URL)

#Scraping Listings using urls
# Required files
TECH_SEARCHED_FOR = 'technologies.txt'
SUCCESFULL_EXTRACTIONS = 'succesfull_extractions.txt'
FAILED_EXTRACTIONS = 'failed_extractions.txt'
# Calling script
scrape_listings.main(SCRAPPED_URLS, TECH_SEARCHED_FOR, SUCCESFULL_EXTRACTIONS, FAILED_EXTRACTIONS)

#Saving extraction results to MongoDB Atlas

client = mongodb.return_db_client()

# Check connection to DB
try:
    mongodb.command_ping(client)
except:
    l.log_exception('main', 'Unable to connect with database')

db = client['Web_Scraping_Job_Site']
collection_succesfull = mongodb.db['Job_Listings']
collection_failed = mongodb.db['Failed_Urls']

# Record if there was a failure, clear files
try:
    mongodb.save_dict_from_file_to_collection(collection_succesfull, SUCCESFULL_EXTRACTIONS)
    mongodb.save_str_from_file_to_collection(collection_failed, FAILED_EXTRACTIONS)
    #Clearing files
    with open(SUCCESFULL_EXTRACTIONS, 'w', encoding='utf-8') as file:
        file.truncate(0)
    with open(FAILED_EXTRACTIONS, 'w', encoding='utf-8') as file:
        file.truncate(0)
except:
    l.log_exception('main','saving listing JSON to database')
