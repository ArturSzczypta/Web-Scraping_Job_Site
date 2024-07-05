''' Modify documents in the database'''
import re
from datetime import datetime
import mongodb_functions as mongo
import scrape_listings as s_l


def remove_single_tech(collection, tech_name):
    ''' Remove a single technology from the database'''
    result = collection.update_many({'$or': [
        {'technologies.expected': tech_name},
        {'technologies.optional': tech_name},
        {'technologies.found': tech_name}]},
        {'$pull': {'technologies.expected': tech_name,
                   'technologies.optional': tech_name,
                   'technologies.found': tech_name}})
    print(result.modified_count, "documents updated.")


def get_all_locations(collection):
    ''' Returns all locations in the database'''
    locations = collection.distinct('location')
    print(locations)


def modify_location(collection):
    '''Modify the location field by removing the county
    or shire name inside the parentheses'''
    # Define the regular expression pattern
    pattern = r'^(.*?)\s+\('

    # Update the documents in the collection
    result = collection.update_many({'location': {'$regex': pattern}},
                                    {'$set': {'location': {'$regexReplace': {
                                        'input': '$location',
                                        'find': pattern,
                                        'replacement': '$1'
                                    }}}})
    print(result.modified_count, 'documents updated')


def modify_regions(collection, approved_values):
    for document in collection.find():
        current_region = document.get('region')

        if current_region not in approved_values:
            cleaned_region = s_l.clean_region(current_region)
            collection.update_one({'_id': document['_id']},
                                  {'$set': {'region': cleaned_region}})
            print(f'''Document {document['_id']}
                   updated with region {cleaned_region}.''')


def remove_invalid_field(collection, field):
    '''Remove invelid fields'''
    # During querries, some variables were replaced with querry itself.
    result = collection.update_many({field: {'$type': 'object'}},
                                    {'$unset': {field: ''}})

    query = {field: {"$type": "object"}}
    result = collection.find(query)
    print('objects removed')
    # Print the documents
    for document in result:
        print(document[field])


def clean_regions(collection):
    '''Replace the region field with proper voivodeship name'''
    for doc in collection.find({'region': {'$ne': ''}}):
        # call the clean_region function
        new_region = s_l.clean_region(doc['region'])
        collection.update_one({'_id': doc['_id']},
                              {'$set': {'region': new_region}})
        print('regions replaced')


def correct_one_region(collection):
    '''Correct the last region name'''
    filter = {"region": "Kuyavia-Pomerania"}
    update = {"$set": {"region": "kujawsko-pomorskie"}}

    result = collection.update_many(filter, update)
    print(result.modified_count, "documents updated.")


def find_duplicates(collection):
    '''Get the duplicate documents'''
    pipeline = [{"$group": {"_id": "$url", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$project": {"_id": 0, "url": "$_id", "count": 1}}]

    # get the duplicates
    duplicates = list(collection.aggregate(pipeline))
    print(len(duplicates))
    return duplicates


def add_pub_month_field(collection):
    '''Add publication month field'''

    # assuming your collection is named "my_collection"
    docs = collection.find({})

    for doc in docs:
        pub_str = str(doc["publication_date"])
        pub_dt = datetime.fromisoformat(pub_str)
        # Use first day of the month as default
        month_year = datetime(pub_dt.year, pub_dt.month, 1).isoformat()
        collection.update_one({'_id': doc['_id']},
                              {'$set': {'publication_month': month_year}})
    print('publication month added')


def check_types_in_field(collection, field):
    '''Check data types in given field'''
    pipeline = [{'$group': {'_id': {'$type': f'${field}'},
                            'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}]

    result = collection.aggregate(pipeline)

    for doc in result:
        data_type = doc['_id']
        count = doc['count']
        print(f'Data Type: {data_type}, Count: {count}')


def add_field(collection, field, value):
    '''Add a field to the collection'''
    query = {field: {'$exists': False}}

    # Update documents by adding the 'location' field
    result = collection.update_many(query, {'$set': {field: value}})
    print(f'''{result.modified_count} documents updated
          with {field} set to {value}.''')


def update_non_string_locations(collection):
    # Find documents where 'location' is not a string and not None
    query = {
        'location': {
            '$not': {'$type': 'string'},
            '$ne': None
        }
    }

    # Update documents by setting 'location' to None
    update_query = {'$set': {'location': None}}
    result = collection.update_many(query, update_query)

    print(f"{result.modified_count} documents 'location' set to None.")


def count_region_values(collection):
    pipeline = [
        {
            '$group': {
                '_id': {'$type': '$region'},
                'count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 0,
                'type': {
                    '$cond': {
                        'if': {'$eq': ['$_id', 'missing']},
                        'then': 'missing',
                        'else': {
                            '$cond': {
                                'if': {'$eq': ['$_id', 'null']},
                                'then': 'None',
                                'else': {'$toString': '$_id'}
                            }
                        }
                    }
                },
                'count': 1
            }
        }
    ]
    result = collection.aggregate(pipeline)

    for doc in result:
        print(f"Data Type: {doc['type']}, Count: {doc['count']}")


def count_unique_region_strings(collection):
    pipeline = [
        {
            '$match': {'region': {'$type': 'string'}}
        },
        {
            '$group': {
                '_id': '$region',
                'count': {'$sum': 1}
            }
        }
    ]
    result = collection.aggregate(pipeline)

    for doc in result:
        print(f"String: {doc['_id']}, Count: {doc['count']}")


def clean_listing_string(substring: str) -> str:
    ''' Cleans substring from problematic symbols, patterns, sequences'''

    substring = substring.strip()

    sequences = r'\\n|\\t|\\r|\\b|\\f|\\"'
    substring = re.sub(sequences, ' ', substring)

    not_polish = r'[^\w,:\.\'"\-(){}\[\]\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+'
    substring = re.sub(not_polish, ' ', substring)

    incorrect_null = r'\bundefined\b'
    substring = re.sub(incorrect_null, 'null', substring)

    missing_nulls = r':\s*(,|"\s*"|\]|\[\s*\]|\}|\{\s*\})'
    substring = re.sub(missing_nulls, ':null', substring)

    missing_commas_1 = r'null\s*([^,\]\}])'
    substring = re.sub(missing_commas_1, r'null,\g<1>', substring)
    missing_commas_2 = r'(\w+)\s+,\s*"'
    substring = re.sub(missing_commas_2, r'\1","', substring)

    extra_char_1 = r'(?<=",)\s*",(?=")'
    substring = re.sub(extra_char_1, '', substring)

    # Remove special whitespace characters
    substring = re.sub(r'\s', ' ', substring)

    substring = substring.replace('u002F', ' ')
    substring = substring.replace('u003E', ' ')
    substring = substring.replace('--', ' ')
    substring = substring.replace(', \"\"', ' ')

    # Remove excess spaces
    substring = re.sub(r' {2,}', ' ', substring)
    substring = re.sub(r'\s*"\s*', '"', substring)

    # Add missing curly Brackets
    opening_braces = len(re.findall(r'{', substring))
    closing_braces = len(re.findall(r'}', substring))
    if opening_braces > closing_braces:
        substring += '}'*(opening_braces-closing_braces)

    return substring


def modify_listing_string(file_in, file_out):
    '''Modify the listing string in the database'''
    with open(file_in, 'r', encoding='utf8') as file_1:
        lines = file_1.readlines()
        data_cleaned = list()
        for line in lines:
            line = clean_listing_string(line)
            data_cleaned.append(line)
            print(line)

    with open(file_out, 'a', encoding='utf8') as file_2:
        for line in data_cleaned:
            file_2.write(line + '\n')


if __name__ == '__main__':
    '''Performs basic database operations'''
    _client = mongo.return_db_client()
    mongo.check_connection(_client)

    db = _client['Web_Scraping_Job_Site']
    collection = db['Job_Listings']

    # Add functions you want to run
