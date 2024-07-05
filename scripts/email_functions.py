''' Send email with error messages and execution details'''
import os
from pathlib import Path
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid import Email, To, Content

import logging
import logging_functions as lf

ENV_DIR = Path(__file__).parent.parent.parent / '.env.txt'
load_dotenv(str(ENV_DIR))

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
    try:
        response = sg.client.mail.send.post(request_body=mail_json)
        print(response.status_code)
        print(response.headers)
    except Exception as e:
        logging.error(f'Unable to send email: {repr(e)}')


def error_email(error_message):
    ''' Send email with critical error messages and execution details'''

    cwd = str(Path.cwd().name)
    script_name = str(Path(__file__).name)

    subject = f'Error {cwd} - {script_name}'
    message = f'''Error Notification \n
    Error ocurred during execution of {script_name} in {cwd}.\n
    Error message:\n{error_message}'''
    send_email(subject, message)


if __name__ == '__main__':
    current_file_name = Path(__file__).stem
    log_file_name = f'{current_file_name}_log.log'

    BASE_DIR = Path(__file__).parent.parent
    LOGGING_FILE = BASE_DIR / 'logging_files' / log_file_name
    LOGGING_JSON = BASE_DIR / 'logging_files' / 'logging_config.json'

    lf.configure_logging(LOGGING_JSON, LOGGING_FILE)
    logging.error('Testing saving logs to file.')

    # Send test email
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    sender_email = Email('arturszczypta@gmail.com')
    receiver_email = To('arturszczypta@gmail.com')

    subject = "Test Email"
    content = Content("Sended using SendGrid", "and Python")
    mail = Mail(sender_email, receiver_email, subject, content)

    mail_json = mail.get()

    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
