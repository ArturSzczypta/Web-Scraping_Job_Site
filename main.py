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
    ''' Create regex pattern for given skill set
    I assume names of languages and technologies names shorter than 3 have to be search as \b%s\b (R, C)
    Longer names can be part of longer string (PostgreSQL, MySQL for sql)
    Each pattern dinds all instances of upper/lower case and capitalised'''
    
    
    skills_schort = []
    skills_long = []
    for skill in skill_set:
        if len(skill) <3:
            skills_schort.append(re.escape(skill))
        else:
            skills_long.append(re.escape(skill))
    
    pattern_1 = None
    pattern_2 = None
    if len(skills_schort) > 0:
        pattern_1 = '|'.join(skills_schort)
    if len(skills_long) > 0:
        pattern_2 = '|'.join(skills_long)
    
    if pattern_1 and pattern_2:
        pattern = re.compile(r'\b(%s)\b|(%s)' % (pattern_1, pattern_2), re.IGNORECASE)
    elif pattern_1:
        pattern = re.compile(pattern_1, re.IGNORECASE)
    elif pattern_2:
        pattern = re.compile(pattern_2, re.IGNORECASE)
    else:
        pattern = ''

    return pattern
print(skill_patterns(skill_set))


