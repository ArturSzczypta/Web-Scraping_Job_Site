# Web Scraping Job Site

This project scrapes job listings from polish job site "Pracuj.pl". Listings are saved as documents into MongoDB NoSQL database.

## Project goals

1. Inspect what technologies are mainly used in Poland with Python and SQL
2. Deeper dive into logging and error handling
3. Hand on experience with web scrapping
4. Hands on experience with No-SQL database

## Compatablitity

Python 3.11 on Windows 10
Chrome webbrowser version 114.0.5735.199.
Sendgrid for sending emails

## Installation

1. Clone or download this repository
2. Navigate to the repository in cmd or terminal
3. Run pip install -r requirements.txt
4. Create the enviroment file '.env' outside the project folder. File '.env' should contain login and password to your MongoDB and Sendgrid accounts

## Script Workflow

1. ~~Scrape all urls added since last scrapping~~
2. Compare current url's to thse scraped last time and remove repeats
3. Open each url and extract the interesting data
4. Save to MongoDB database

## First Time Use
1. ~~Go to 'txt_files/for_search.csv' and write the tags you are looking for (in my case data science, big data, Python, SQL, R, Tableau)~~
2. ~~Go to folder 'text_and_json/last_date.log' and modify the date.~~
3. Go to folder 'text_and_json/technologies.txt' and modify the tech acronyms and tech names the script will look for in scraped listings.
4. Manually scrape urls:
    4.1. Add all technologies you want to look for
    4.2. Press all 'Lokalizacje' buttons and press them, so all uls's are accessible
    4.3. Inspect the web site and copy the entire content in <div data-test="section-offers">
    4.4. Save the copied content to text file
    4.5. For each results page copy and save offers to the text file
    4.6. Specializations requiere seperate search. Search specializations you want, and repeat steps 4.2 to 4.5
    4.7. Save the text file to folder 'manual_scrapping' 
4. Run 'main.py' using Python3.

Originally the file scraped the url's automatically. Unfortunately, since July 2023 script misses most of the "Location" buttons. At that time the website was changing. In page inspect I noticed few errors raised. I tried multiple times to fix it
The way the technologies and specializations are searched also changed.
I added a option for using manually scrapped website data. Script will extract the url's for scraping.

Scraping job offers every 2 weeks was sufficient. I advise to scrape once a week, preferably during the weekend.

Depending on the ammout of offers, scraping may take few hours. This is caused by build in time delays. Without these delays, the website will block your access for few days.

## Consecutive uses
Run 'main.py' using Python3. The project saves last used job offer links to prevent repeats ~~and saves last usage date to continue from where it stopped.~~

## Known issues
1. Manually scrapping url's is very inconvinient.
2. Although the script only remembers urls's used last time. If a job is posted for long period of time the listing will be saved more than once.
3. Remote jobs are usually posted in each voivodeship, so some offers can be repeated up to 16 times.
4. Script does not save the bulk text of the offer, just the tech acronyms and tech names found in text
5. Script does not save the additional job benefits, flike private insurance, gym cards, etc.
6. 'requirements.txt' lists necessary liblaries, but not the actual versions used

## Author
Artur Szczypta

## Support
Feel free to provide me feedback, suggestions, create issues. 









