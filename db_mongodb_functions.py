''' Set of methods for connecting and using MongoDB Atlas database'''
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json

def return_db_client():
    '''Connects to database, returns client'''
    # Load environment variables from .env file
    load_dotenv()

    # Get MongoDB URI from environment variables
    MONGODB_URI = os.getenv('MONGODB_URI')

    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    return client

def return_db_collection(client, database_name, collection_name):
    ''' Returs collection'''
    return client[database_name][collection_name]

def save_from_file_to_collection(collection, file_name)
    ''' Saves documents from file to collection
    Assumes file has one JSON in each line'''
    with open(file_name, 'r', encoding='utf-8') as file:
        contents = file.read()
        # Convert the contents of the file into a list of dictionaries
        documents = [json.loads(line) for line in contents.split('\n')]

    result = collection.insert_many(documents)
    print(result.inserted_ids)
