''' Set of methods for connecting and using MongoDB Atlas database'''
import os
import datetime
import json

import logging
from logging import config

from dotenv import load_dotenv
from pymongo.mongo_client  import MongoClient
from pymongo.server_api import ServerApi

if __name__ != '__main__':
    from . import logging_functions as l
    from . import email_functions as e
else:
    import logging_functions as l
    import email_functions as e

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
        l.save_to_log_file(__name__, __file__, 'Unable to connect with database')

def save_dict_from_file_to_collection(collection, file_path):
    ''' Saves documents from file to collection
    Assumes file has one JSON in each line'''
    documents = []
    with open(file_path, 'r', encoding='utf-8') as file:
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

def save_str_from_file_to_collection(collection, file_path):
    ''' Saves urls from file to collection'''
    documents = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()[:-1]
        # Convert the contents of the file into a list of dictionaries
        documents = [{'url': line} for line in lines]

    result = collection.insert_many(documents)
    print(result.inserted_ids)

if __name__ == '__main__':
    #Performs basic logging set up
    #Create log file name based on script name
    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    l.get_log_file_name(log_file_name)

    #Configure logging file
    l.configure_logging()
    logger = logging.getLogger(__name__)

    #Saving succesfull_extractions to MongoDB Atlas
    SUCCESFULL_EXTRACTIONS = os.path.join(os.getcwd(), 'text_and_json/succesfull_extractions.txt')

    _client = return_db_client()
    check_connection(_client)

    db = _client['Web_Scraping_Job_Site']
    collection_succesfull = db['Job_Listings']

    save_dict_from_file_to_collection(collection_succesfull, SUCCESFULL_EXTRACTIONS)
