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
import db_functions_mongodb as db

''' Performs basic logging set up'''
    l.main()

''' Scraping Urls'''
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

'''

''' 
#Saving succesfull_extractions to MongoDB Atlas
'''
client = db.return_db_client()
collection_succesfull = db.return_db_collection(client, 'Web_Scraping_Job_Site', 'Job_Listings')
collection_failed = db.return_db_collection(client, 'Web_Scraping_Job_Site', 'Failed_Urls')

db.save_dict_from_file_to_collection(collection_succesfull, succesfull_extractions)
db.save_str_from_file_to_collection(collection_failed, failed_extractions)



''' Clearing files'''
with open(succesfull_extractions, 'w', encoding='utf-8') as file:
    file.truncate(0)
with open(failed_extractions, 'w', encoding='utf-8') as file:
    file.truncate(0)
'''
