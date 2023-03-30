''' Scrape it.pracuj.pl job listings to database'''
import chardet
import json
import re
import datetime

import logging
from logging import config
import logging_functions as l
import scrape_urls
import scrape_listings
import db_functions_mongodb as mongodb

''' Performs basic logging set up'''
l.main()

''' #Scraping Urls from job site'''
# Specialisations start with 's=', technologies with 'tt=', spaces replaced by '+'
searched_set = {'s=data+science', 's=big+data', 'tt=Python', 'tt=SQL', 'tt=R'}

# _base_url will be used first, then _iterable_url untill the end
base_url = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn=1'
iterable_url = 'https://it.pracuj.pl/?{}&jobBoardVersion=2&pn='
last_date_file = 'last_date.log'
scraped_urls = 'scraped_urls.txt'
# Calling script
scrape_urls.main(last_date_file, searched_set, scraped_urls, base_url, iterable_url)

''' Scraping Listings using urls'''
# Required files
scraped_urls = 'scraped_urls_today.txt'
tech_in_listing = 'technologies.txt'
succesfull_extractions = 'succesfull_extractions.txt'
failed_extractions = 'failed_extractions.txt'
# Calling script
scrape_listings.main(scraped_urls, tech_in_listing, succesfull_extractions, failed_extractions)

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

# Record if there was a failure
db_failure = 0
try:
    mongodb.save_dict_from_file_to_collection(collection_succesfull, succesfull_extractions)
except:
    db_failure = 1
    l.log_exception('main','saving listing JSON to database')
try:
    mongodb.save_str_from_file_to_collection(collection_failed, failed_extractions)
except:
    db_failure = 1
    l.log_exception('main','saving url JSON to database')

''' Clearing files, only if saving to database was succesfull'''
if db_failure == 0:
    with open(succesfull_extractions, 'w', encoding='utf-8') as file:
        file.truncate(0)
    with open(failed_extractions, 'w', encoding='utf-8') as file:
        file.truncate(0)

