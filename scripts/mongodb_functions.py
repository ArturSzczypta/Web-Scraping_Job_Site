''' Set of methods for connecting and using MongoDB Atlas database'''
import os
from pathlib import Path
import datetime
import json

import logging
import logging_functions as lf

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


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
    except Exception as e:
        logging.critical(f'check_connection - Unable to connect with database'
                         f' - {repr(e)}')


def save_str_to_file(str, file_path):
    ''' Saves string to file'''
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(str + '\n')


def save_dict_from_file_to_collection(collection, extractions, invalid_json):
    ''' Saves documents from file to collection
    Assumes file has one JSON in each line'''
    documents = []
    with open(extractions, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]

        # Print the first line for inspection
        # Convert the contents of the file into a list of dictionaries,
        # save invalid json
        documents = list()
        for line in lines:
            try:
                new_json = json.loads(line)
                documents.append(new_json)
            except json.JSONDecodeError as e:
                save_str_to_file(line, invalid_json)
                logging.error(f'Invalid JSON: {line} - {repr(e)}')

    # Convert date strings to ISO Dates
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
    print(f'Uploaded to database {result.inserted_ids}')


def save_str_from_file_to_collection(collection, file_path: str):
    ''' Saves string from file to collection'''
    documents = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()[:-1]
        # Convert the contents of the file into a list of dictionaries
        documents = [{'Item': line} for line in lines]

    result = collection.insert_many(documents)
    print(result.inserted_ids)


if __name__ == '__main__':
    current_file_name = Path(__file__).stem
    log_file_name = f'{current_file_name}_log.log'

    BASE_DIR = Path(__file__).parent.parent
    LOGGING_FILE = BASE_DIR / 'logging_files' / log_file_name
    LOGGING_JSON = BASE_DIR / 'logging_files' / 'logging_config.json'

    lf.configure_logging(LOGGING_JSON, LOGGING_FILE)
    logging.error('Testing saving logs to file.')

    # Saving succesfull_extractions to MongoDB Atlas
    # Required files
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    TXT_DIR = os.path.join(PARENT_DIR, 'txt_files')
    SUCCESFULL_EXTRACTIONS = os.path.join(TXT_DIR,
                                          'succesfull_extractions.txt')
    INVALID_JSON = os.path.join(TXT_DIR, 'invalid_json.txt')

    _client = return_db_client()
    check_connection(_client)

    db = _client['Web_Scraping_Job_Site']
    collection = db['Job_Listings']

    save_dict_from_file_to_collection(collection, SUCCESFULL_EXTRACTIONS,
                                      INVALID_JSON)
