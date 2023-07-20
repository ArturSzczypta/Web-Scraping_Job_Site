''' Send email with error messages and execution details'''
import os
import traceback
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid import Email, To, Content

# Load environment variables from .env file
if __name__ == '__main__':
    load_dotenv('../.env.txt')
else:
    load_dotenv('../.env.txt')

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
MY_EMAIL = os.getenv('MY_EMAIL')
EMAIL_TO = os.getenv('EMAIL_TO')

def send_email(subject, message, recipient=EMAIL_TO):
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

def error_email():
    ''' Send email with critical error messages and execution details'''

    # Get current working directory
    cwd = os.path.basename(os.getcwd())
    script_name = os.path.basename(__file__)

    error_message = traceback.format_exc()

    subject = f'Error {cwd} - {script_name}'
    message = f'''Error Notification \n
    Error ocurred during execution of {script_name} in {cwd}.\n
    Error message:\n{error_message}'''
    # Send email
    send_email(subject, message)

if __name__ == '__main__':
    #Performs basic logging set up
    #Get this script name
    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    # Send test email
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