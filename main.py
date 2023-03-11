'''
Analyze listings with my skills
'''
import json
import re
import datetime

'''
Result for big batch collected on 10 March 2023:
Regex found 
Pattern Python: 1830 unique matches
Pattern SQL: 3754 unique matches
Pattern \bR\b: 710 unique matches
'''
skills_list = ['Python', 'SQL', 'R']
my_dict = {}
with open('listings_matching_skills.txt', 'r',encoding='UTF-8') as file:
    first_line = file.readline()
    my_dict = json.loads(first_line)
    #print(json.dumps(my_dict, ensure_ascii=False, indent=4))

#Basic listing data
#url
url = my_dict['url']
job_title = my_dict['offerReducer']['offer']['jobTitle']
country = my_dict['offerReducer']['offer']['workplaces'][0]['country']['name']
region = my_dict['offerReducer']['offer']['workplaces'][0]['region']['name']
location = my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location']['name']
salary = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']

# Assuming both dates always comply to ISO 8601 format
publication_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['dateOfInitialPublication']).date()
expiration_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['expirationDate']).date()

# technologies
tech_expected = {tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][0]['model']['customItems']}
tech_optional = {tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][1]['model']['customItems']}

# responsibilities
resp_expected = {resp for resp in my_dict['offerReducer']['offer']['sections'][1]['model']['bullets']}

# requirements
req_expected = {resp for resp in my_dict['offerReducer']['offer']['sections'][2]['subSections'][0]['model']['bullets']}
req_optional = {resp for resp in my_dict['offerReducer']['offer']['sections'][2]['subSections'][1]['model']['bullets']}

# development-practices
dev_practices = {practices['code'] for practices in my_dict['offerReducer']['offer']['sections'][4]['model']['items']}


'''
for i in dev_practices:
    print(i)
'''

'''

#def extract_usefull_listings(skills_list):
Extract listings that have my skills
    # Patterns for skills_slist = ['Python', 'SQL', 'R']
    # Designed to find SQL
    pattern_1 = r'%s'
    # Designed to find R language
    pattern_2 = r'\b%s\b'

    patterns_list = [pattern_1 % skills_list[0], pattern_1 % skills_list[1],
    pattern_2 % skills_list[2]]

    with open('listings_json_data.txt', 'r',encoding='UTF-8') as input_file, \
    open('listings_matching_skills.txt', 'a',encoding='UTF-8') as output_file:
        #Find all JSON that contain my skills
        matches = set()
        for pattern in patterns_list:
            # Set comprehensioin to filter out listings with my skills
            new_matches = {line for line in input_file if re.search(pattern, line)}
            
            # Merge the sets of matches
            matches |= new_matches

            # Reset the input file pointer to the beginning
            input_file.seek(0)

            # Print the number of unique matches for this pattern
            print(f"Pattern {pattern}: {len(new_matches)} unique matches")
        # Write the matching lines to the output file
        for match in matches:
            output_file.write(match)
'''