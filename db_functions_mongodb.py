''' Set of methods for connecting and using MongoDB Atlas database'''
import os
from dotenv import load_dotenv
from pymongo.mongo_client  import MongoClient
from pymongo.server_api import ServerApi
import json

def return_db_client():
    '''Connects to database, returns client'''
    # Load environment variables from .env file
    load_dotenv('.env.txt')
    # Get MongoDB URI from environment variables
    MONGODB_URI = os.getenv('MONGODB_URI')

    # Connect to MongoDB
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    return client

def command_ping(client):
    ''' Returns command used in checking connection'''
    return client.admin.command('ping')

def check_connection(client):
    ''' Check connection to database'''
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

def save_dict_from_file_to_collection(collection, file_name):
    ''' Saves documents from file to collection
    Assumes file has one JSON in each line'''
    documents = []
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()[:-1]
        # Convert the contents of the file into a list of dictionaries
        documents = [json.loads(line) for line in lines]

    result = collection.insert_many(documents)
    print(result.inserted_ids)

def save_str_from_file_to_collection(collection, file_name):
    ''' Saves urls from file to collection
    Assumes file has one url in each line'''
    documents = []
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()[:-1]
        # Convert the contents of the file into a list of dictionaries
        documents = [{'url': line} for line in lines]

    result = collection.insert_many(documents)
    print(result.inserted_ids)

if __name__ == '__main__':

    ''' Saving succesfull_extractions to MongoDB Atlas'''
    succesfull_extractions = 'succesfull_extractions.txt'
    failed_extractions = 'failed_extractions.txt'

    client = return_db_client()
    check_connection(client)

    db = client['Web_Scraping_Job_Site']
    collection_succesfull = db['Job_Listings']
    collection_failed = db['Failed_Urls']

    save_dict_from_file_to_collection(collection_succesfull, succesfull_extractions)
    save_str_from_file_to_collection(collection_failed, failed_extractions)