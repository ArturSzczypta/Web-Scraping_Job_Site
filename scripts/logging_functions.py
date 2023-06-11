'''
Methods ffor setting logging
'''
import os
import logging
from logging import config
import json
import traceback
import re
import requests

#Get logging_file_name from main script
LOG_FILE_NAME = 'placeholder.log'
LOG_CONF_JSON = 'logging_configuration.json'
logger = None

def get_log_file_name(new_log_file_name):
    '''
    Get logging_file_name from main script

    :new_log_file_name: main script name with ending '_log.log'
    '''
    #Makes file name global for all other functions
    global LOG_FILE_NAME
    LOG_FILE_NAME = new_log_file_name


def configure_logging():
    '''
    Configure logging by using JSON file
    Assumes file is in folder "text_and_json"
    '''
    # Get the path of executing script
    script_path = os.path.dirname(__file__)

    # Get the path of logging_configuration.json
    json_path = None
  
    if __name__ == '__main__':
        script_path = os.path.dirname(__file__)
        parent_path = os.path.dirname(script_path)
        json_path = os.path.join(parent_path, 'text_and_json', \
                                 'logging_configuration.json')
    else:
        parent_path = os.path.dirname(script_path)
        json_path = os.path.join(parent_path, 'text_and_json', \
                                 'logging_configuration.json')

    # Load logging configuration from JSON file                           
    with open(json_path, 'r', encoding='utf-8') as f:
        global LOG_CONF_JSON
        LOG_CONF_JSON = json.load(f)
    # Change log file name
    for handler in LOG_CONF_JSON.get('handlers', {}).values():
        if handler.get('class') == 'logging.FileHandler':
            handler['filename'] = LOG_FILE_NAME

    logging.config.dictConfig(LOG_CONF_JSON)

def get_logging_json():
    '''Get logging configuration from JSON file'''
    return LOG_CONF_JSON

# Save exception as single line in logger
def log_exception(hierarchy_str, written_string = ' '):
    '''
    Save exception as single line in logger

    :hierarchy_str: name of function
    :written_string: Additional info
    '''

    #Change traceback into single string
    error_message = traceback.format_exc()
    # Remove ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    error_message = re.sub(r'\^+', '', error_message)
    # Remove ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    error_message = re.sub(r'\~+', '', error_message)

    exc_list = error_message.split('\n')[:-1]
    exc_list = [x.strip(' ') for x in exc_list]
    error_message = ' - '.join(exc_list)

    configure_logging()
    logger = logging.getLogger(f'main.{hierarchy_str}')
    logger.error(written_string + ' - ' + error_message)
    logger.debug('')

# Save exception as single line in logger
def get_exception():
    '''Change traceback into single line string'''
    error_message = traceback.format_exc()
    # Remove ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    error_message = re.sub(r'\^+', '', error_message)
    # Remove ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    error_message = re.sub(r'\~+', '', error_message)

    # Split into list, replace new line with - 
    exc_list = error_message.split('\n')[:-1]
    exc_list = [x.strip(' ') for x in exc_list]
    error_message = ' - '.join(exc_list)
    # replace -  - with - 
    error_message = re.sub(r'\-  \-', '-', error_message)
    # Remove excess spaces
    error_message = re.sub(r' {2,}', ' ', error_message)
    return error_message



#Check internet connection, terminate script if no internet and record error
def check_internet():
    '''
    Loggs error if cannot connect to Google
    '''
    try:
        requests.head("http://www.google.com/", timeout=5)
        logger.debug('Internet connection active')
    except:
        logger.critical('Cannot connect to internet')

if __name__ != '__main__':
    #Performs basic logging set up
    #Get logging_file_name from main script
    configure_logging()
    logger = logging.getLogger(__name__)

def main():
    ''' Performs basic logging set up, if script is runned directly'''

    #Get this script name
    log_file_name = __file__.split('\\')
    log_file_name = f'{log_file_name[-1][:-3]}_log.log'

    get_log_file_name(log_file_name)

    #Configure logging file 
    configure_logging()
    logger = logging.getLogger(__name__)

    #Check internet connection, terminate script if no internet
    check_internet()

if __name__ == '__main__':
    main()