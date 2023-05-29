''' Send email with critical error messages and execution details'''
import os
import traceback
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid import Email, To, Content

# Load environment variables from .env file
load_dotenv('.env.txt')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
MY_EMAIL = os.getenv('MY_EMAIL')
EMAIL_TO = os.getenv('EMAIL_TO')

sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
from_email = Email('arturszczypta@gmail.com')  # Change to your verified sender
to_email = To('arturszczypta@gmail.com')  # Change to your recipient
subject = "Sending with SendGrid is Fun"
content = Content("text/plain", "and easy to do anywhere, even with Python")
mail = Mail(from_email, to_email, subject, content)

# Get a JSON-ready representation of the Mail object
mail_json = mail.get()

# Send an HTTP POST request to /mail/send
response = sg.client.mail.send.post(request_body=mail_json)
print(response.status_code)
print(response.headers)

def send_email(subject, message, recipient):
    ''' Send email'''
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(MY_EMAIL)  # Change to your verified sender
    to_email = To(recipient)  # Change to your recipient
    content = Content(message)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)

def error_email(subject):
    ''' Send email with critical error messages and execution details'''

    # Get the path of main folder
    # if main.py is executed, bellow is true
    parent_path = os.path.dirname(__file__) 

    # Test if above is true. If not, go one folder up
    test_path = os.path.join(parent_path, 'text_and_json')
    if not os.path.exists(test_path):
        parent_path = os.path.join(parent_path, '..')
    
    parent_directory = os.path.basename(parent_path)

    error_message = traceback.format_exc()

    subject = f'Error {parent_directory} - {subject}'
    message = f'''Error Notification \n
    Error ocurred during execution of {parent_directory}.\n
    Error message:\n{error_message}'''
    # Send email
    send_email(subject, message, EMAIL_TO)
