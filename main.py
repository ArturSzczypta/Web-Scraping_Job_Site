'''
Analyze listings with my skills
'''
import chardet
import json
import re
import datetime

import logging
from logging import config
import logging_functions as l

#Get this script name
log_file_name = __file__.split('\\')
log_file_name = f'{log_file_name[-1][:-3]}_log.log'

l.get_log_file_name(log_file_name)

#Configure logging file 
l.configure_logging()
logger = logging.getLogger('main')


skill_set = {'Python', 'SQL', 'R'}

def skill_patterns(skill_set):
    ''' Create regex patterns for given skill set
    I assume names of languages and technologies names shorter than 3 have to be search as \b%s\b (R, C)
    Longer names can be part of longer string (PostgreSQL, MySQL for sql)
    Each pattern dinds all instances of upper/lower case and capitalised'''
    
    # Names shorter than 3
    pattern_1 = r'\b%s\b'
    # Names longer or equal 3
    pattern_2 = r'%s'
    
    pattern_list = []
    for skill in skill_set:
        if len(skill) <3:
            pattern_list.append(pattern_1 % skill)
        else:
            pattern_list.append(pattern_2 % skill)
    return pattern_list


