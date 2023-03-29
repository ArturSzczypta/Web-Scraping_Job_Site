''' Extracting already downloaded data to text files'''
import json
import ast
import re
from collections import Counter

def extracting_to_files(file_name):
    keys = ['req_expected', 'req_optional', 'resp_bullets', 'tech_expected', 'tech_optional']

    # Open the input and output files
    with open(file_name, 'r', encoding='utf-8') as input_file:
        with open('req_expected.txt', 'w', encoding='utf-8') as req_expected_file, \
             open('req_optional.txt', 'w', encoding='utf-8') as req_optional_file:

            # Loop through each lline with JSON
            for line in input_file:
                # Load the JSON object
                obj = json.loads(line)

                # Write the values for the desired keys to their respective output files
                req_expected_file.write(str(obj.get('req_expected', '')) + '\n')
                req_optional_file.write(str(obj.get('req_optional', '')) + '\n')


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


def nest_current_listings(file_with_jsons, new_file_with_jsons):
    ''' Nest salary and technology keys'''
    # open the input file and output file
    with open(file_with_jsons, 'r',encoding='utf-8') as input_file,\
    open(new_file_with_jsons, 'w',encoding='utf-8') as output_file:
        # iterate over each line in the input file
        for line in input_file:
            # parse the JSON object from the line
            json_obj = json.loads(line)
            '''
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
            '''
            
            # Store tech data in nested dictionary
            json_obj['requirements'] = {
            'expected': json_obj.pop('req_expected'),
            'optional': json_obj.pop('req_optional')
            }

            # write the modified JSON object to the output file
            output_file.write(json.dumps(json_obj, ensure_ascii=False) + '\n')
#nest_current_listings('new_listings_scraped.txt','new_listings_scraped_1.txt')


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

def extract_all_tech(file_with_tech, file_with_listings, new_file_with_listings):
    ''' Extract all technologies/languages/annrevations saved in a file
    Add them to given dictionary as a list'''
    # Save requirements to set
    tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file_1:
        for line in file_1:
            tech_set.add(line.strip())
    
    # Open each line as string. After extraction convert to dictionary.
    all_tech_found = []
    with open(file_with_listings, 'r', encoding='utf-8') as file_2,\
    open(new_file_with_listings, 'a', encoding='utf-8') as file_3:
        count = 0
        for line in file_2:
            line = line.strip()
            line = line.replace('u003E', '')
            line = line.replace('--', '')
            line = line.replace(', \"\"', '')
            tech_found = []
            for tech in tech_set:
                tech_escaped = re.escape(tech)
                pattern = re.compile(r'\b(%s)\b' % tech_escaped, re.IGNORECASE)
                if pattern.search(line):
                    tech_found.append(tech)
                    all_tech_found.append(tech)

            tech_found.sort()
            new_dict = json.loads(line)
            new_dict['technologies']['found'] = tech_found

            file_3.write(json.dumps(new_dict, ensure_ascii=False) + '\n')
    '''
    # Count and print
    counter = Counter(all_tech_found)
    sorted_values = counter.most_common()
    print(sorted_values)
    '''
extract_all_tech('technologies_final.txt','new_listings_scraped.txt','new_listings_scraped_2.txt')

def simplify_dev_practices(file_with_listings, new_file_with_listings):
    ''' Replace each dictionary in list with just main value'''
    
    with open(file_with_listings, 'r', encoding='utf-8') as file_2,\
    open(new_file_with_listings, 'a', encoding='utf-8') as file_3:
        count = 0
        for line in file_2:
            line = line.strip()
            new_dict = json.loads(line)
            if new_dict['dev_practices'] != None:
                my_list = new_dict['dev_practices']
                new_list = [element['primaryTargetSiteName'] for element in my_list]
                new_dict['dev_practices'] = new_list

                print(new_dict['url'], new_dict['dev_practices'])

            file_3.write(json.dumps(new_dict, ensure_ascii=False) + '\n')




'''
skills = []
with open('technologies_final_1.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.replace('\t',',').strip()
        skills.append(tuple(line.split(','))[0])

with open('technologies_final.txt', 'w', encoding='utf-8') as file:
    for skill in skills:
        file.write(skill + '\n')
'''
#skill_list = [skill[0] for skill in Skills_freq_list]
#print(skill_list[:500])

'''
with open('technologies_trimmed_2.txt', 'a', encoding='utf-8') as file:
    for skill in Skills_freq_list:
        file.write(f'{skill[0]}\t{skill[1]}\n')
'''
'''
count = 0
for skill in Skills_freq_list:
    #print(skill[0])
    count += int(skill[1])
print(count)

count_decimated = int(count / 10)
print(count_decimated)
skills_90_percent = 9 * count_decimated
skills_80_percent = 8 * count_decimated
skills_70_percent = 7 * count_decimated
skills_60_percent = 6 * count_decimated
skills_50_percent = 5 * count_decimated
print(skills_90_percent,skills_80_percent,skills_70_percent,skills_60_percent,skills_50_percent)

skill_count = 0
count = 0
last_count = 0
for skill in Skills_freq_list:
    skill_count += 1
    count += int(skill[1])
    if count >= skills_90_percent and last_count < skills_90_percent:
        print(f'90% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_80_percent and last_count < skills_80_percent:
        print(f'80% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_70_percent and last_count < skills_70_percent:
        print(f'70% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_60_percent and last_count < skills_60_percent:
        print(f'60% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_50_percent and last_count < skills_50_percent:
        print(f'50% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')

    last_count += int(skill[1])
'''