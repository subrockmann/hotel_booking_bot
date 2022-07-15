import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import phonenumbers

# take environment variables from .env.
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
SMTP_STRING = os.getenv("SMTP_STRING")
SMTP_PORT = os.getenv("SMTP_PORT")

subject = "A test mail sent by Python. It has an attachment."
content = """Hello,
This is a simple mail.
Thank You
"""


def send_email(receiver_email, subject, content):
    # Setup the MIME
    message = MIMEMultipart()
    message["From"] = SENDER_ADDRESS
    message["To"] = receiver_email
    message["Subject"] = subject
    # The body and the attachments for the mail
    message.attach(MIMEText(content, "plain"))
    text = message.as_string()

    # Create SMTP session for sending the mail
    session = smtplib.SMTP(SMTP_STRING, SMTP_PORT)
    session.starttls()  # enable security
    session.login(SENDER_ADDRESS, SENDER_EMAIL_PASSWORD)
    session.sendmail(SENDER_ADDRESS, receiver_email, text)
    session.quit()
    print("Mail Sent")
    return


def validate_phone_number(phone_number):
    phone_num_parsed = phonenumbers.parse(phone_number, None)
    valid_phone = phonenumbers.is_possible_number(phone_num_parsed)
    phone_num_formated = phonenumbers.format_number(
        phone_num_parsed, phonenumbers.PhoneNumberFormat.E164
    )
    return valid_phone, phone_num_formated


def request_room_availability(
    checkin_date, checkout_date, num_single_rooms, num_double_rooms
):
    """
    Mock-up of room hotel reservation system
    """
    num_single_rooms_available = num_single_rooms + 1
    num_double_rooms_available = num_double_rooms + 1
    single_room_rate = 80
    double_room_rate = 140
    availability_ID = "007"

    return {
        "availability_ID": availability_ID,
        "num_single_rooms_available": num_single_rooms_available,
        "num_double_rooms_available": num_double_rooms_available,
        "single_room_rate": single_room_rate,
        "double_room_rate": double_room_rate,
    }
