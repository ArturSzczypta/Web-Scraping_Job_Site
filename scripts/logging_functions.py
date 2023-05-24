'''
Methods ffor setting logging
'''
import logging
from logging import config
import json
import traceback
import re
import requests

#Get logging_file_name from main script
LOG_FILE_NAME = 'placeholder.log'
def get_log_file_name(new_log_file_name):
    '''
    Get logging_file_name from main script

    :new_log_file_name: main script name with ending '_log.log'
    '''
    #Makes file name global for all other functions
    global LOG_FILE_NAME
    LOG_FILE_NAME = new_log_file_name

# Configure logging to using JSON file
def configure_logging():
    '''
    Configure logging to using JSON file
    Assumes file is in folder "text_and_json"
    '''
    relative_path = '../text_and_json/logging_configuration.json'
    conf_path = os.path.join(os.path.dirname(__file__), \
                             relative_path)
    with open(conf_path, 'r', encoding='utf-8') as f:
        log_conf = json.load(f)

    for handler in log_conf.get('handlers', {}).values():
        if handler.get('class') == 'logging.FileHandler':
            handler['filename'] = LOG_FILE_NAME

    logging.config.dictConfig(log_conf)

# Save exception as single line in logger
def log_exception(hierarchy_str, written_string = ' '):
    '''
    Save exception as single line in logger

    :hierarchy_str: name of function
    :written_string: Additional info
    '''

    #Change traceback into single string
    exc_message = traceback.format_exc()
    # Remove ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    exc_message = re.sub(r'\^+', '', exc_message)
    # Remove ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    exc_message = re.sub(r'\~+', '', exc_message)

    exc_list = exc_message.split('\n')[:-1]
    exc_list = [x.strip(' ') for x in exc_list]
    exc_message = ' - '.join(exc_list)

    configure_logging()
    logger = logging.getLogger(f'main.{hierarchy_str}')
    logger.error(written_string + ' - ' + exc_message)
    logger.debug('')

# Save exception as single line in logger
def get_exception():
    '''Change traceback into single string'''
    exc_message = traceback.format_exc()
    # Remove ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    exc_message = re.sub(r'\^+', '', exc_message)
    # Remove ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    exc_message = re.sub(r'\~+', '', exc_message)

    # Split into list, replace new line with - 
    exc_list = exc_message.split('\n')[:-1]
    exc_list = [x.strip(' ') for x in exc_list]
    exc_message = ' - '.join(exc_list)
    # replace -  - with - 
    exc_message = re.sub(r'\-  \-', '-', exc_message)
    # Remove excess spaces
    exc_message = re.sub(r' {2,}', ' ', exc_message)
    return exc_message



#Check internet connection, terminate script if no internet and record error
def check_internet():
    '''
    Loggs error if cannot connect to Google
    '''
    try:
        requests.head("http://www.google.com/", timeout=2)
        #logger.debug('Internet connection active')
    except:
        log_exception(' - Cannot connect to internet')

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

if __name__ == '__main__':
    main()