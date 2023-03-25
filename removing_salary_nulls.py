import json

# define the keys to delete
keys_to_delete = ['salary_from', 'salary_to', 'salary_currency', 'salary_long_form']

# open the input file and output file
with open('file_succesfull.txt', 'r',encoding='utf-8') as input_file, open('output_file.txt', 'w',encoding='utf-8') as output_file:
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