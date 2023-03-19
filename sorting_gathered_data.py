''' Extracting already downloaded data to text files'''
import json
import ast

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

def extract_tech_without_repetition():
    tech_set = set()
    sorted_tech = []
    # Open the file with the list of technologies/languages
    with open('tech_expected.txt', 'r', encoding='utf-8') as file:
        
        for line in file:
            line.strip()
            if line == 'None':
                continue
            tech_list = ast.literal_eval(line)
            if tech_list is not None:
                tech_set.update(tech_list)
        
    sorted_tech = sorted(tech_set)

    # Open a file to write the unique technologies/languages to
    with open('unique_tech.txt', 'a', encoding='utf-8') as output_file:

        for item in sorted_tech:
            output_file.write(item + '\n')

extract_tech_without_repetition()