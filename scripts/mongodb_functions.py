''' Set of methods for connecting and using MongoDB Atlas database'''
import os
import datetime
import json

import logging
from logging import config
import logging_functions as l
import email_functions as e

from dotenv import load_dotenv
from pymongo.mongo_client  import MongoClient
from pymongo.server_api import ServerApi

logger = None
if __name__ != '__main__':
    #Performs basic logging set up
    #Get logging_file_name from main script
    logging.config.dictConfig(l.get_logging_json())
    logger = logging.getLogger(__name__)

def return_db_client():
    '''Connects to database, returns client'''
    # Load environment variables from .env file
    if __name__ == '__main__':
        load_dotenv('../.env.txt')
    else:
        load_dotenv('.env.txt')
    # Get MongoDB URI from environment variables
    MONGODB_URI = os.getenv('MONGODB_URI')

    # Connect to MongoDB
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    return client

def check_connection(client):
    ''' Check connection to database'''
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except:
        logger.critical('check_connection - Unable to connect with database')
        e.error_email('Check_connection - Unable to connect with database')

def save_dict_from_file_to_collection(collection, file_name):
    ''' Saves documents from file to collection
    Assumes file has one JSON in each line'''
    documents = []
    if __name__ == '__main__':
        data_file_path = os.path.join(os.path.dirname(__file__), \
                                  f'../text_and_json/{file_name}')
    else:
        data_file_path = os.path.join(os.path.dirname(__file__), \
                                  f'text_and_json/{file_name}')
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()[:-1]
        # Convert the contents of the file into a list of dictionaries
        documents = [json.loads(line) for line in lines]

    #Convert date strings to ISO Dates
    date_format = '%Y-%m-%d'
    for doc in documents:
        date_str = doc['publication_date']
        publication_date = datetime.datetime.strptime(date_str, date_format)
        doc['publication_date'] = publication_date.isoformat()

        date_str = doc['publication_month']
        publication_date = datetime.datetime.strptime(date_str, date_format)
        doc['publication_month'] = publication_date.isoformat()

        date_str = doc['expiration_date']
        expiration_date = datetime.datetime.strptime(date_str, date_format)
        doc['expiration_date'] = expiration_date.isoformat()

    result = collection.insert_many(documents)
    print(result.inserted_ids)

def save_str_from_file_to_collection(collection, file_name):
    ''' Saves urls from file to collection
    Assumes file is in "text_and_json" folder and
    has one url in each line'''
    documents = []
    if __name__ == '__main__':
        data_file_path = os.path.join(os.path.dirname(__file__), \
                                  f'../text_and_json/{file_name}')
    else:
        data_file_path = os.path.join(os.path.dirname(__file__), \
                                  f'text_and_json/{file_name}')
    with open(data_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()[:-1]
        # Convert the contents of the file into a list of dictionaries
        documents = [{'url': line} for line in lines]

    result = collection.insert_many(documents)
    print(result.inserted_ids)

if __name__ == '__main__':
    #Performs basic logging set up
    #Get this script name
    log_file_name = __file__.split('\\')
    log_file_name = f'{log_file_name[-1][:-3]}_log.log'

    l.get_log_file_name(log_file_name)

    #Configure logging file
    l.configure_logging()
    logger = logging.getLogger(__name__)

    #Saving succesfull_extractions to MongoDB Atlas
    SUCCESFULL_EXTRACTIONS = 'succesfull_extractions.txt'
    FAILED_EXTRACTIONS = 'failed_extractions.txt'

    _client = return_db_client()
    check_connection(_client)

    db = _client['Web_Scraping_Job_Site']
    collection_succesfull = db['Job_Listings']
    collection_failed = db['Failed_Urls']

    save_dict_from_file_to_collection(collection_succesfull, SUCCESFULL_EXTRACTIONS)
    save_str_from_file_to_collection(collection_failed, FAILED_EXTRACTIONS)
