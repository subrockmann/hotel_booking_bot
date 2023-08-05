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
    try:
        session = smtplib.SMTP(SMTP_STRING, SMTP_PORT)
        session.connect()
        print("connected")
        session.starttls()  # enable security

        print("started tls")
        print("trying to login")
        session.login(SENDER_ADDRESS, SENDER_EMAIL_PASSWORD)
        print("Sending email")
        session.sendmail(SENDER_ADDRESS, receiver_email, text)
        session.quit()
        print("Mail Sent")
    except:
        print("Email process failed")
    return


def validate_phone_number(phone_number):
    try:
        phone_num_parsed = phonenumbers.parse(phone_number, None)
        valid_phone = phonenumbers.is_possible_number(phone_num_parsed)
        phone_num_formated = phonenumbers.format_number(
            phone_num_parsed, phonenumbers.PhoneNumberFormat.E164
        )
    except:
        phone_num_formated = phone_number
        valid_phone = False

    return valid_phone, phone_num_formated


def request_room_availability(
    checkin_date, checkout_date, num_single_rooms, num_double_rooms
    ):
    """
    Mock-up of hotel room reservation system
    """
    num_single_rooms_available = max(0, num_single_rooms + 1)   # change these values to simulate that the hotel has rooms available
    num_double_rooms_available = max(0,num_double_rooms + 1)
    single_room_rate = 80
    double_room_rate = 140
    availability_ID = "007"

    room_proposal = {
        "availability_ID": availability_ID,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "num_single_rooms_available": num_single_rooms,
        "num_double_rooms_available": num_double_rooms,
        "single_room_rate": single_room_rate,
        "double_room_rate": double_room_rate,
    }

    if num_single_rooms_available < num_single_rooms:
        room_proposal["num_single_rooms_available"] = num_single_rooms_available
        room_proposal["availability_issue"] = "We do not have any single rooms available for these dates."

        if num_double_rooms_available < num_double_rooms:
            room_proposal["num_double_rooms_available"] = num_double_rooms_available
            room_proposal["availability_issue"] = "Unfortunately, we do not have any rooms available for these dates."
    elif num_double_rooms_available < num_double_rooms:

        room_proposal["num_double_rooms_available"] = num_double_rooms_available
        room_proposal["availability_issue"] = "We do not have any double rooms available for these dates."

    else:
        room_proposal["availability_issue"] = None

    return room_proposal
