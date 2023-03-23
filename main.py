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



