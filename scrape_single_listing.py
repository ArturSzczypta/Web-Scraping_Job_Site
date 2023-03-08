'''
Web scraping job listing details on popular polish job site, Pracuj.pl
'''
import re
import requests
import json

def scrape_single_listing(url):
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
  return my_dict

def main(url):
  '''
  This is the main function of the script.
          
  It scrapes job offer details

  Note: This function is only executed when the script is run directly,
  not when it is imported as a module.
  '''
  example_dict = scrape_listing(url)
  print(json.dumps(example_dict, indent=4))

if __name__ == '__main__':
    main('''https://www.pracuj.pl/praca/
      senior-manager-analytics-krakow-kapelanka-42a,oferta,1002448201''')
