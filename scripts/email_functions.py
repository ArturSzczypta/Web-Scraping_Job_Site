''' Send email with error messages and execution details'''
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid import Email, To, Content

load_dotenv(os.path.join(os.path.dirname(__file__), \
                             '..','.env.txt'))

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
MY_EMAIL = os.getenv('MY_EMAIL')
EMAIL_TO = os.getenv('EMAIL_TO')

def send_email(subject, message, recipient=EMAIL_TO):
    ''' Send email'''
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    senders_email = Email(MY_EMAIL)
    receivers_email = To(recipient)
    content = Content(message)
    mail = Mail(senders_email, receivers_email, subject, content)

    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)

def error_email(error_message):
    ''' Send email with critical error messages and execution details'''

    cwd = os.path.basename(os.getcwd())
    script_name = os.path.basename(__file__)

    subject = f'Error {cwd} - {script_name}'
    message = f'''Error Notification \n
    Error ocurred during execution of {script_name} in {cwd}.\n
    Error message:\n{error_message}'''
    send_email(subject, message)

if __name__ == '__main__':
    #Performs basic logging set up
    #Get this script name
    log_file_name = os.path.basename(__file__).split('.')
    log_file_name = f'{log_file_name[0]}_log.log'

    # Send test email
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    sender_email = Email('arturszczypta@gmail.com')
    receiver_email = To('arturszczypta@gmail.com')

    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(sender_email,receiver_email, subject, content)

    mail_json = mail.get()

    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)