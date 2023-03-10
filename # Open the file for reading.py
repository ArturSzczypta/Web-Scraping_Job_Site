''' Script for cleanining when something goes wrong'''
import re
import json
unique_links = set()
finished_listings = set()

# Extract all listings to be scraped
with open('links_to_listings.txt', 'r', encoding='UTF-8') as file:
    # Read the lines into a set, removing any leading or trailing whitespace
    unique_links = set(line.strip() for line in file)
'''
# extract listings already made
with open('listings_json_data.txt', 'r', encoding='UTF-8') as file:
    
    # Strings used in regex
    start_string = "{\"url\": \""
    end_string = "\", \"toastReducer"

    for line in file:
        # Read the lines into a set, removing any leading or trailing whitespace
        line = line.strip()

        # Extract the finished urls
        start_index = line.find(start_string) + len(start_string)
        end_index = line.find(end_string, start_index)
        substring = line[start_index:end_index]
        finished_listings.add(substring)
'''

with open('listings_json_data.txt', 'r', encoding='UTF-8') as file:
    
    lines = [line.strip() for line in file]
    print("Number of lines:", len(lines))
    
    # Strings used in regex
    start_string = "{\"url\": \""
    end_string = "\", \"toastReducer"

    for line in file:
        # Strip any leading or trailing whitespace and newlines from the line
        line = line.strip()

        # Extract the finished urls
        start_index = line.find(start_string) + len(start_string)
        end_index = line.find(end_string, start_index)
        substring = line[start_index:end_index]
        finished_listings.add(substring)





# Open the file for writing
with open('finished_listings.txt', 'w', encoding='UTF-8') as file:
    # Write the unique links back to the file, one per line
    for link in finished_listings:
        file.write(link + '\n')
with open('finished_listings.txt', 'r', encoding='UTF-8') as file:
    lines = [line.strip() for line in file]
    print("Number of lines:", len(lines))