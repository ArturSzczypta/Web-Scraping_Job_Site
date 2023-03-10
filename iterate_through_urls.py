'''
Web scraping popular polish job site, Pracuj.pl
'''

import datetime
import scrape_urls

date_today = datetime.date.today()
date_yesterday = date_today - datetime.timedelta(days=1)

webpage = 'https://it.pracuj.pl/'
new_http_links,unique_dates = scrape_urls.scrape_uls(webpage)
http_links = set(new_http_links)

# check if all listings are recent, if so start looking to other pages
if all(date == date_today or date == date_yesterday for date in unique_dates):
    page_number = 2
    while True:
        webpage = f'https://it.pracuj.pl/?pn={page_number}'
        new_http_links,unique_dates = scrape_urls.scrape_uls(webpage)
        http_links = http_links.union(new_http_links)

        if all(date == date_today or date == date_yesterday for date in unique_dates):
            page_number += 1
        else:
            print(f'Dates: {unique_dates}')
            break
else:
    print(f'Dates: {unique_dates}')

# Append file containing all job listing
with open('links_to_listings.txt', 'a+',encoding='UTF-8') as file:
    old_records = set(line.strip() for line in file)
    new_records = http_links - old_records
    print(f'New: {len(new_records)}')
    for link in new_records:
        file.write(link + '\n')
