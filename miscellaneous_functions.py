''' Extracting already downloaded data to text files'''
import json
import ast
import re

def extracting_to_files():
    keys = ['req_expected', 'req_optional', 'resp_bullets', 'tech_expected', 'tech_optional']

    # Open the input and output files
    with open('succesfull extractions.txt', 'r', encoding='utf-8') as input_file:
        with open('req_expected.txt', 'w', encoding='utf-8') as req_expected_file, \
             open('req_optional.txt', 'w', encoding='utf-8') as req_optional_file, \
             open('resp_bullets.txt', 'w', encoding='utf-8') as resp_bullets_file, \
             open('tech_expected.txt', 'w', encoding='utf-8') as tech_expected_file, \
             open('tech_optional.txt', 'w', encoding='utf-8') as tech_optional_file:

            # Loop through each lline with JSON
            for line in input_file:
                # Load the JSON object
                obj = json.loads(line)

                # Write the values for the desired keys to their respective output files
                req_expected_file.write(str(obj.get('req_expected', '')) + '\n')
                req_optional_file.write(str(obj.get('req_optional', '')) + '\n')
                resp_bullets_file.write(str(obj.get('resp_bullets', '')) + '\n')
                tech_expected_file.write(str(obj.get('tech_expected', '')) + '\n')
                tech_optional_file.write(str(obj.get('tech_optional', '')) + '\n')

def extract_tech_without_repetition(file_with_lists,file_with_tech):
    tech_set = set()
    sorted_tech = []
    # Open the file with the list of technologies/languages
    with open(file_with_lists, 'r', encoding='utf-8') as file:
        
        for line in file:
            line.strip()
            if line == 'None':
                continue
            tech_list = ast.literal_eval(line)
            if tech_list is not None:
                tech_set.update(tech_list)
        
    sorted_tech = sorted(tech_set)

    # Open a file to write the unique technologies/languages to
    with open(file_with_tech, 'a', encoding='utf-8') as output_file:

        for item in sorted_tech:
            output_file.write(item + '\n')

def update_tech(file_with_tech, new_tech_set=None):
    ''' Add new technologies/languages and then sort'''
    # Extract technologies/languages to a set
    tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file:
        for line in file:
            tech_set.add(line.strip())
    
    # Add new technologies/languages if provided
    if new_tech_set is not None:
        tech_set.update(new_tech_set)

    # Sort and write unique technologies/languages to file
    sorted_tech = sorted(tech_set)
    with open(file_with_tech, 'w', encoding='utf-8') as file:
        for item in sorted_tech:
            file.write(item + '\n')

def removing_salary_nulls(file_with_jsons, new_file_with_jsons):
    ''' Remove salary keys if there is no salary'''
    # define the keys to delete
    keys_to_delete = ['salary_from', 'salary_to', 'salary_currency', 'salary_long_form']

    # open the input file and output file
    with open(file_with_jsons, 'r',encoding='utf-8') as input_file,\
    open(new_file_with_jsons, 'w',encoding='utf-8') as output_file:
        # iterate over each line in the input file
        for line in input_file:
            # parse the JSON object from the line
            json_obj = json.loads(line)
            
            # check if the condition is met (e.g. a different key has value False)
            if json_obj.get('is_salary') == False:
                # delete the keys to delete from the JSON object
                for key in keys_to_delete:
                    if key in json_obj:
                        del json_obj[key]
            
            # write the modified JSON object to the output file
            output_file.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def nest_current_listings(file_with_jsons, new_file_with_jsons):
    ''' Nest salary and technology keys'''
    # open the input file and output file
    with open(file_with_jsons, 'r',encoding='utf-8') as input_file,\
    open(new_file_with_jsons, 'w',encoding='utf-8') as output_file:
        # iterate over each line in the input file
        for line in input_file:
            # parse the JSON object from the line
            json_obj = json.loads(line)
            
            # Store salary data in nested dictionary, remove is_salary boolean
            if json_obj.get('is_salary') == True:
                json_obj['salary'] = {
                'salary_from': json_obj.pop('salary_from'),
                'salary_to': json_obj.pop('salary_to'),
                'salary_currency': json_obj.pop('salary_currency'),
                'salary_long_form': json_obj.pop('salary_long_form')
                }
                del json_obj['is_salary']
            if json_obj.get('is_salary') == False:
                del json_obj['is_salary']

            if json_obj.get('tech_expected') == True:
                # Store tech data in nested dictionary
                json_obj['technologies'] = {
                'expected': json_obj.pop('tech_expected'),
                'optional': json_obj.pop('tech_optional')
                }

            # write the modified JSON object to the output file
            output_file.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def replace_descriptions(file_name_1, file_name_2):
    lines = None
    with open(file_name_1, 'r', encoding='utf-8') as file_1:
        lines = file_1.readlines()

    with open(file_name_2, 'w',encoding='utf-8') as file_2:
        for line in lines:
            line = line.replace('salary_from','min')
            line = line.replace('salary_to','max')
            line = line.replace('salary_currency','currency')
            line = line.replace('salary_long_form','pay_period')
            file_2.write(line)

def extract_all_tech(file_with_jsons):
    ''' Extracts all tech from each JSON, adds it in technologies dictionary'''
    # Nothing yet

def skill_patterns(skill_set):
    ''' Create regex pattern for given skill set
    I assume names of languages and technologies names shorter than 3
    have to be search as \b%s\b (R, C)
    Longer names can be part of longer string (PostgreSQL, MySQL for sql)
    Each pattern dinds all instances of upper/lower case and capitalised'''

    skills_schort = []
    skills_long = []
    for skill in skill_set:
        if len(skill) <3:
            skills_schort.append(re.escape(skill))
        else:
            skills_long.append(re.escape(skill))

    pattern_1 = None
    pattern_2 = None
    if len(skills_schort) > 0:
        pattern_1 = '|'.join(skills_schort)
    if len(skills_long) > 0:
        pattern_2 = '|'.join(skills_long)

    if pattern_1 and pattern_2:
        pattern = re.compile(r'\b(%s)\b|(%s)' % (pattern_1, pattern_2),
            re.IGNORECASE)
    elif pattern_1:
        pattern = re.compile(pattern_1, re.IGNORECASE)
    elif pattern_2:
        pattern = re.compile(pattern_2, re.IGNORECASE)
    else:
        pattern = ''

    return pattern

def check_for_skill_set(substring, skill_set):
    ''' Check for elements of skill set in the substring
    Cancel pipeline if none of skills is mentioned'''
    return re.search(skill_patterns(skill_set),substring, flags=re.IGNORECASE)

def update_file(old_urls_file, urls_file):
    ''' Adds new records, removes old ones'''
    old_records = set()
    with open(old_urls_file, 'r',encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)

    with open(urls_file, 'r+',encoding='utf-8') as file:
        todays_links = set(line.strip() for line in file)
        new_records = todays_links - old_records
        print(f'New: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')


def filter_unused_tech(file_with_tech, file_with_listings, file_only_used_tech):
    ''' Keep only technologies/languages found in the scraped listings'''
    # Extract technologies/languages to a set
    tech_set = set()
    filtered_tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file_1:
        for line in file_1:
            tech_set.add(line.strip())
    
    with open(file_with_listings, 'r', encoding='utf-8') as file_2:
        count = 0
        for line in file_2:
            for tech in tech_set:
                tech_escaped = re.escape(tech)
                pattern = re.compile(r'\b(%s)\b' % tech_escaped, re.IGNORECASE)
                if pattern.search(line):
                    filtered_tech_set.add(tech)
            count += 1
            if count % 10 == 0:
                print(count)

    # Sort and write unique found technologies/languages to file
    sorted_tech = sorted(filtered_tech_set)
    with open(file_only_used_tech, 'w', encoding='utf-8') as file:
        for item in sorted_tech:
            file.write(item + '\n')

