<h1>Web Scraping Job site</h1>

This project scrapes job listings from polish site "Pracuj.pl" using tags, extracts data and saves into MongoDB NoSQL database. If error occurs in try/except clause, a email will be sent

<h1>Installation</h1>

- Clone or download this repository
- Navigate to the repository in cmd or terminal
- Run pip install -r requirements.txt
- Create in the main folder a enviroment file '.env' with login and password to your MongoDB and  Sendgrid accounts


<h1>First Time Use</h1>
- Go to 'main.py' and write the tags you are looking for (in my case data science, big data, Python, SQL, R, Tableau)
- Go to folder 'text_and_json' and modify the  date in 'last_date.log'. 
- Go to folder 'text_and_json' and modify the  date in 'technologies.txt'. File contains words  that  will be searched for in scraped listings.
- Run 'main.py' using Python3.
Depending on  the ammout of offers, it may take few hours  to finish. This is caused by build in time delays. Without these delays, the website will be spammed buy request and you will be block for few days.

<h1>Consecutive uses</h1>
Run 'main.py' using Python3. The project saves last used  job offer links and  last usage date.

<h2>Notes</h2>

<h2>Compatablitity</h2>

It was created and used with Python 3.11 on Windows 10. Current webbrowser version 114.0.5735.199.
If you used in different operating system or Python version, please let me know.

<h2>Authors</h2>
Artur Szczypta

<h2>Support</h2>
Feel free to provide me feedback, suggestions, create issues. 









1. Search job listings bz specified technologies and IT specialisations
2. Save urls to all listings posted since last scraping date
3. Delete any urls that were used last time
4. Scrape each job listing, record failed extractions
5. Clean and arrange data
6. Save to MongoDB database
7. Save date, clear temporary storage files