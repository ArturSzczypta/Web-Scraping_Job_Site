'''
Web scraping popular polish job site, Pracuj.pl
'''
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pprint

from bs4 import BeautifulSoup
from time import sleep
import re
from numpy import random

import datetime
import requests

import scrape_urls

#list of all
http_links = set()

date_today = datetime.date.today()
date_yesterday = date_today - datetime.timedelta(days=1)

webpage = 'https://it.pracuj.pl/'
new_http_links,unique_dates = scrape_urls.scrape_uls(webpage)

for date in unique_dates:
    if date == date_today and date == date_yesterday:
        # filter through
    else:
        print('Too old')
        break

