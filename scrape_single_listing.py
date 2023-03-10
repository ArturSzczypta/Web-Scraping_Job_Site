'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import re
import requests
import json
from time import sleep
from numpy import random

import logging_functions as l

def scrape_single_listing(url):
  try:
    ''' Scrapes job listing details from the url, return a dictionary'''

    # Make a request to the URL and get the HTML response
    response = requests.get(url)
    response.encoding = 'utf-8' # To recognise polish letters
    html = response.text

    # Extract the substring {...} between "window['kansas-offerview'] = "and "<"
    start_string = "window['kansas-offerview'] = "
    end_string = "<"
    start_index = response.text.find(start_string) + len(start_string)
    end_index = response.text.find(end_string, start_index)
    substring = response.text[start_index:end_index]

    # Replace invalid valiable name with null
    fixed_json_str = re.sub(r'\bundefined\b', 'null', substring)

    # Convert the string to a dictionary using the json module
    my_dict = json.loads(fixed_json_str)
    new_dict = {'url': url}
    my_dict = {**new_dict, **my_dict}

    json_str = json.dumps(my_dict)
    json_str = json_str.replace('\n', '').replace(' ', '')
    return json.dumps(my_dict, ensure_ascii=False)
  except:
    print(url)

def scrape_json_data():
  ''' Scrapes json data about job listings, save to text file'''
  unique_links = set()
  finished_links = set()
  finished_count = 0

  # Open the file for reading
  with open('links_to_listings.txt', 'r', encoding='UTF-8') as file:
      # Read the lines into a set, removing any leading or trailing whitespace
      unique_links = set(line.strip() for line in file)

  # Open the file for reading
  with open('finished_listings.txt', 'r', encoding='UTF-8') as file:
      # Read the lines into a set, removing any leading or trailing whitespace
      finished_links = set(line.strip() for line in file)

  #Remaining links to do
  remaining_listings = unique_links - finished_links
  total = len(remaining_listings)
  one_percent = int(total / 100)

  for link in remaining_listings:
    sleep(random.uniform(2, 5))
    
    # Append file containing all job listing
    with open('listings_json_data.txt', 'a',encoding='UTF-8') as file:
          file.write(scrape_single_listing(link) + '\n')
    with open('finished_listings.txt', 'a',encoding='UTF-8') as file:
          file.write(link + '\n')
    
    #Print if a round percent is finished
    finished_count += 1
    if finished_count % one_percent == 0:
      print(finished_count / one_percent)

def main():
    ''' Performs basic logging set up, if script is runned directly'''

    #Get this script name
    log_file_name = __file__.split('\\')
    log_file_name = f'{log_file_name[-1][:-3]}_log.log'

    get_log_file_name(log_file_name)

    #Configure logging file 
    configure_logging()
    logger = logging.getLogger('main')

    #Check internet connection, terminate script if no internet
    check_internet()

    scrape_json_data()

if __name__ == '__main__':
    main()