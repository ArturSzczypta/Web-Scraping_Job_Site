import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email account information
email = "suchinio0987@gmail.com" # Your email address
password = "suchinio7890" # Your email password

# Email information
to = "arturszczypta@gmail.com" # Reciever's address
subject = "Test Email" # Subjest
body = "This is a test email sent from Python" # Body

# Create a multipart message
msg = MIMEMultipart()
msg['From'] = email
msg['To'] = to
msg['Subject'] = subject

# Add body to email
msg.attach(MIMEText(body, 'plain'))

# Create SMTP session
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email, password)

# Send email
text = msg.as_string()
server.sendmail(email, to, text)
server.quit()

print('Email sent')