'''Combine all text files in a directory into a single file.'''
import json

elements_set = set()
succesfull_urls_set = set()
failed_urls_set = set()
mixed_urls_set = set()

def succesfull_to_set(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            elements_set.add(json_obj)
            succesfull_urls_set.add(json_obj['url'])

def urls_to_set(file_name, urls_set):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            urls_set.add(line.strip())