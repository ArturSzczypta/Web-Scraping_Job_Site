'''Combine all text files in a directory into a single file.'''
import json

elements_set = set()
succesfull_urls_set = set()
failed_urls_set = set()
mixed_urls_set = set()

def succesfull_to_set(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            json_str = line.strip()
            elements_set.add(json_str)
            json_obj = json.loads(json_str)
            succesfull_urls_set.add(json_obj['url'])

def urls_to_set(file_name, urls_set):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            urls_set.add(line.strip())

succesfull_to_set('succesfull_extractions_0.txt')
succesfull_to_set('succesfull_extractions_1.txt')
succesfull_to_set('succesfull_extractions_2.txt')
succesfull_to_set('succesfull_extractions_3.txt')

urls_to_set('failed_extractions_0.txt', failed_urls_set)
urls_to_set('failed_extractions_1.txt', failed_urls_set)
urls_to_set('failed_extractions_2.txt', failed_urls_set)

urls_to_set('mixed_extractions_0.txt', mixed_urls_set)
urls_to_set('mixed_extractions_1.txt', mixed_urls_set)

failed_missing_urls = mixed_urls_set.difference(succesfull_urls_set)
for url in failed_missing_urls:
    print(url)
    failed_urls_set.add(url)

with open('succesfull_extractions_combined.txt', 'w', encoding='utf-8') as file:
    for element in elements_set:
        element_json = json.loads(element)
        file.write(json.dumps(element_json, ensure_ascii=False) + '\n')

failed_urls_set.update(mixed_urls_set.difference(succesfull_urls_set))
with open('failed_urls_combined.txt', 'w', encoding='utf-8') as file:
    for url in failed_urls_set:
        file.write(url + '\n')