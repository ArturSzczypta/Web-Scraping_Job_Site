'''
Methods ffor setting logging
'''
import os
from datetime import datetime
import logging
from logging import config
import json
import re

#Get logging_file_name from main script
log_file = 'placeholder.log'
LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','logging_files')
JSON_FILE = os.path.join(LOG_DIR, 'logging_configuration.json')

LOG_CONF_JSON = None
logger = logging.getLogger(__name__)

def get_log_file_name(new_log_file_name):
    '''
    Get logging_file_name from main script

    :new_log_file_name: main script name with ending '_log.log'
    '''
    #Makes file name global for all other functions
    global log_file
    global LOG_DIR
    log_file = os.path.join(LOG_DIR, new_log_file_name)

def configure_logging():
    '''Configure logging by using JSON file'''

    # Get the path of logging_configuration.json
    global LOG_CONF_JSON

    # Load logging configuration from JSON file                           
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            LOG_CONF_JSON = json.load(f)
        # Change log file name
        for handler in LOG_CONF_JSON.get('handlers', {}).values():
            if handler.get('class') == 'logging.FileHandler':
                handler['filename'] = log_file
                print(handler['filename'])
        # Clear any existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers = []
    except Exception as e:
        print(e)
        logger.error(f"Error loading logging configuration: {e}")
        return

    # Configure logging
    logging.config.dictConfig(LOG_CONF_JSON)

def get_logging_json():
    '''Get logging configuration from JSON file'''
    return LOG_CONF_JSON

def format_exception(exc_info):
    '''Format to single line without special characters'''
    # Remove multiple ^ and ~
    exc_info = re.sub(r'(\^+|\~+)', '', exc_info)
    # Remove multiple spaces
    exc_info = re.sub(r'\s+', ' ', exc_info)
    #replace new lines with |
    exc_info = re.sub(r'\n', ' | ', exc_info)
    return exc_info

def save_to_log_file(name, file, error_message, message):
    '''
    Save message to log file
    :name: __name__
    :file: __file__
    :message: message to be saved
    '''
    # Get log file name
    file_name = log_file
    
    time = datetime.now()
    file = os.path.basename(file)
    
    # Create string for log file
    log_message = f'{time} - {name} - {file} - {message}'
    if error_message:
        log_message += f' - {error_message}'
    
    # Save message to log file
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write(f'{log_message}\n')

def main():
    ''' Performs basic logging set up, if script is runned directly'''

    #Create log file name based on script name
    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    get_log_file_name(log_file_name)

    #Configure logging file 
    configure_logging()
    logger = logging.getLogger(__name__)

if __name__ == '__main__':
    main()