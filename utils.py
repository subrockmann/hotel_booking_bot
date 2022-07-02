import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
SMTP_STRING = os.getenv("SMTP_STRING")
SMTP_PORT = os.getenv("SMTP_PORT")

subject = 'A test mail sent by Python. It has an attachment.' 
content = '''Hello,
This is a simple mail.
Thank You
'''

def send_email(receiver_email, subject, content):
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = SENDER_ADDRESS
    message['To'] = receiver_email
    message['Subject'] = subject
    #The body and the attachments for the mail
    message.attach(MIMEText(content, 'plain'))
    text = message.as_string()

    #Create SMTP session for sending the mail
    session = smtplib.SMTP(SMTP_STRING, SMTP_PORT) 
    session.starttls() #enable security
    session.login(SENDER_ADDRESS, SENDER_EMAIL_PASSWORD) 
    session.sendmail(SENDER_ADDRESS, receiver_email, text)
    session.quit()
    print('Mail Sent')
    return