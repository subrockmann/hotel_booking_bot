# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import email
from html import entities
import re, os, dotenv
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, ValidationAction, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.types import DomainDict


from rasa_sdk.events import (
    SlotSet,
    FollowupAction,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
    ActiveLoop
)

from datetime import datetime as dt
from email_validator import validate_email as ve
from email_validator import EmailNotValidError

# import impaction_ask_contact_channel
import importlib

from sqlalchemy import except_
import actions.utils as utils

# imp.reload(utils)
importlib.reload(utils)

# Helper functions

def get_date(time):
    # check if the date needs to be cleaned up
    try:
        time_object = dt.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")
        date = str(time_object.date())
        return date
    except:
        return time

# Default actions
class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #dispatcher.utter_message(template="my_custom_fallback_template")
        dispatcher.utter_message(text="Default Fallback Action Triggered!")
        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]


# Form validations

class ValidateStayForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_stay_form"

    def validate_checkin_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate checkin_date."""
        if isinstance(slot_value, dict):
            print("valdiate Stay form - checkin date - dict")
            # DucklingEntityExtractor returns a dict when it extracts a date range
            checkin_date = slot_value.get("to")
            print(f"Checkin date: {checkin_date}")
            # SlotSet("checkout_date", get_date(slot_value.get("to")))
            return [{"checkin_date": get_date(slot_value.get("from"))}]
            # return {"checkin_date": slot_value.capitalize()}
        else:
            # Duckling extractor returns a date
            # print("valdiate Stay form - checkin date -  no dict")
            return {"checkin_date": get_date(slot_value)}

    def validate_checkout_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate checkout_date."""
        if isinstance(slot_value, dict):
            # DucklingEntityExtractor returns a dict when it extracts a date range
            return {"checkout_date": get_date(slot_value.get("to"))}

            # return {"checkin_date": slot_value.capitalize()}
        else:
            # validation failed, set this slot to None
            return {"checkout_date": get_date(slot_value)}


########################
class ValidateRoomTypeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_room_type_form"

    def validate_num_single_rooms(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate number of single rooms"""
        if isinstance(slot_value, int):
            if slot_value < 0:
                dispatcher.utter_message(
                    text="This is not a valid number for rooms."
                )  ### better explanation would be helpful
                return {"num_single_rooms": None}
            else:
                #dispatcher.utter_message(text = "Thanks for providing the number of single rooms.") # replaced by utter_num_room_types
                return {"num_single_rooms": slot_value}
        else:
            dispatcher.utter_message(
                text="Please provide a full positive number."
            )  ### better explanation would be helpful
            return {"num_single_rooms": None}

    def validate_num_double_rooms(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate number of double rooms"""
        if isinstance(slot_value, int):
            if slot_value < 0:
                dispatcher.utter_message(
                    text="This is not a valid number for rooms."
                )  ### better explanation would be helpful
                return {"num_double_rooms": None}
            else:
                return {"num_double_rooms": slot_value}
        else:
            dispatcher.utter_message(
                text="Please provide a full positive nubmer."
            )  ### better explanation would be helpful
            return {"num_double_rooms": None}


class ValidateEmailForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_email_form"

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ "
        check if an email entity was extracted
        """
        print("validate_email_form triggered")
        email = None
        try:
            email = tracker.get_slot('email')
            #entities = tracker.latest_message["entities"]
            # #dispatcher.utter_message(text=str(entities))  # only for debugging purposes

            # # get the value from the 'email' entity if it has been provided
            # for e in entities:
            #     if e.get("entity") == "email":
            #         email = e.get("value")
            #         # print(f"Email was provided: {email}")
            #     else:
            #         # print("NO Email was provided")
            #         dispatcher.utter_message(response="utter_no_email")
            print(f"Your email is {email}")
        except:
            email = None
            dispatcher.utter_message(response="utter_no_email")

        if email is not None:
            # validate the email
            print(f"validating your email: {email}")

            try:
                # Check that the email address is valid. Turn on check_deliverability
                # for first-time validations like on account creation pages (but not
                # login pages).


                emailinfo = ve(email, check_deliverability=False)
                #validate_email(email)
                  # After this point, use only the normalized form of the email address,
                # especially before going to a database query.
                email = emailinfo.normalized
                print(f"normalized email {email}")
                #return [SlotSet("email", email)] # not allowed for form actions
                return {"email": email}
            except EmailNotValidError as e:
                # The exception message is human-readable explanation of why it's
                # not a valid (or deliverable) email address.
                print("Email error")
                print(str(e))
                dispatcher.utter_message(response="utter_no_email")
                dispatcher.utter_message(text=str(e))
                #print(e)
                email = None
                return {"email": email}
        else:
            dispatcher.utter_message(response="utter_no_email")
            return {"email": email}


class ValidatePredefinedSlots(ValidationAction):
    def validate_checkin_date_dummy(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate checkin_date_dummy."""
        # DucklingEntityExtractor returns a dict when it extracts a date range
        if isinstance(slot_value, dict):
            print(f"Is dict: {slot_value}")
            # tracker.set_slot("checkout_date", get_date(slot_value.get("to")))  ### FIX: 'Tracker' object has no attribute 'set_slot'
            # SlotSet("checkout_date", get_date(slot_value.get("to")))  ### FIX: This crashes
            # key = frozenset(slot_value.items())
            checkin_date = slot_value.get("from")
            try:
                checkout_date = slot_value.get("to")
            except:
                checkout_date = None
            print(f"Checkin date: {checkin_date}")
            SlotSet("checkin_date", checkin_date)
            print(f"Checkout date: {checkout_date}")
            SlotSet("checkout_date", checkout_date)
            FollowupAction("action_set_checkout_date")
            print("Set slots")
            # FollowupAction(name="stay_form") # not necessary due to detected intent
            # SlotSet("checkout_date", get_date(slot_value.get("to")))
            # return {SlotSet("checkin_date", get_date(slot_value.get("from")))}
            # return {SlotSet("checkin_date", checkin_date)}
            return {"checkin_date": get_date(checkin_date)}

        else:
            # DucklingEntityExtractor returns a string for a single date/time
            print("Checkin date is no dict")
            # SlotSet("checkin_date", get_date(slot_value))
            # FollowupAction(name="stay_form") # not necessary due to detected intent
            return {"checkin_date": get_date(slot_value)}

    # def validate_email(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:

    #     """ "
    #     check if an email entity was extracted
    #     """
    #     print("action_validate_predefined slot email triggered")


    #     email = None
    #     try:
    #         email = tracker.get_slot('email')


    #         """Validate email."""
    #         try:
    #             # Validate & take the normalized form of the email
    #             # address for all logic beyond this point (especially
    #             # before going to a database query where equality
    #             # does not take into account normalization).
    #             ve(email)
    #             # dispatcher.utter_message(response="utter_email") # redundant because it is included in email_form_validation
    #             return {"email": email}

    #         except EmailNotValidError as e:
    #             # email is not valid, exception message is human-readable
    #             print(str(e))
    #             dispatcher.utter_message(response="utter_no_email")
    #             dispatcher.utter_message(text=str(e))
    #             dispatcher.utter_message(text="Validate predefined slots")
    #             return [{"email": None}, FollowupAction("email_form")]
    #     except:
    #         print("no email")
    #         return {"email": None}

    # def validate_mobile_number(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:

    #     """ "
    #     check if a phone number was extracted
    #     """
    #     entities = tracker.latest_message["entities"]
    #     for e in entities:
    #         if e.get("entity") == "phone-number":
    #             phone = e.get("value")
    #             print(f"Phone was provided: {phone}")

    #             """Validate phone number."""
    #             try:
    #                 # Validate and format the phone number
    #                 valid_phone, phone_num_formated = utils.validate_phone_number(phone)
    #                 # dispatcher.utter_message(
    #                 #    text=f"Phone: {phone_num_formated} is {valid_phone}"
    #                 # )
    #                 if valid_phone:
    #                     dispatcher.utter_message(response="utter_mobile_number")
    #                     [{"mobile_number": phone_num_formated}, FollowupAction("utter_mobile_number")]
    #                     #return {"mobile_number": phone_num_formated}
    #                 else:
    #                     dispatcher.utter_message(
    #                         text=f"Phone: {phone_num_formated} is not a valid number."
    #                     )
    #                     FollowupAction(
    #                         name="mobile_number_form"
    #                     )  #### Check if this works
    #                     return {"mobile_number": None}
    #             except:
    #                 print("validation failed")
    #                 dispatcher.utter_message(
    #                     text=f"Unfortunately we could not validate this phone number: {phone}."
    #                 )
    #                 FollowupAction(name="mobile_number_form")
    #                 return {"mobile_number": None}

    #         else:
    #             print("no phone number")
    #             dispatcher.utter_message(
    #                 text=f"Your last message did not contain a valid phone number."
    #             )
    #             FollowupAction(name="mobile_number_form")
    #             return {"mobile_number": None}



class ActionValidateEmail(Action):
    def name(self) -> Text:
        return "action_validate_email"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        """
        check if an email entity was extracted
        """
        email = None
        print(f"action_validate_email is triggered")
        try:
            email = tracker.get_slot('email')
            print(f"Your email is {email}")
            #entities = tracker.latest_message["entities"]
            # #dispatcher.utter_message(text=str(entities))  # only for debugging purposes

            # # get the value from the 'email' entity if it has been provided
            # for e in entities:
            #     if e.get("entity") == "email":
            #         email = e.get("value")
            #         # print(f"Email was provided: {email}")
            #     else:
            #         # print("NO Email was provided")
            #         dispatcher.utter_message(response="utter_no_email")
            return [SlotSet("email", email)]
        except:
            email = None
            dispatcher.utter_message(response="utter_no_email")
            return [SlotSet("email", email), FollowupAction("email_form")]
        if email is not None:
            # validate the email
            try:
                emailinfo = ve(email, check_deliverability=False)
                  # After this point, use only the normalized form of the email address,
                # especially before going to a database query.
                email = emailinfo.normalized
                print(f"normalized email {email}")
                #ve(email)
                return [SlotSet("email", email), FollowupAction("email_form")]
            except EmailNotValidError as e:
                dispatcher.utter_message(response="utter_no_email")
                dispatcher.utter_message(text=str(e))
                # print(e)
                email = None
                return [SlotSet("email", email), FollowupAction("email_form")]
        else:
            dispatcher.utter_message(response="utter_no_email")
            return [SlotSet("email", email)]

class ActionValidateMobileNumber(Action):
    def name(self) -> Text:
        return "action_validate_mobile_number"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        """
        Validate phone number.
        """
        mobile_number = None
        print(f"action_validate_mobile_number is triggered")
        
        try:
            # Validate and format the phone number


            mobile_number = tracker.get_slot('mobile_number')
            print(f"Your mobile_number is {mobile_number}")
            valid_phone, phone_num_formated = utils.validate_phone_number(phone)
            # dispatcher.utter_message(
            #    text=f"Phone: {phone_num_formated} is {valid_phone}"
            # )
            if valid_phone:
                dispatcher.utter_message(response="utter_mobile_number")
                return [SlotSet("mobile_number", mobile_number), FollowupAction("utter_mobile_number")]
                #return {"mobile_number": phone_num_formated}
            else:
                print("validation failed")
                dispatcher.utter_message(
                    text=f"Phone: {phone_num_formated} is not a valid number."
                )
                return [SlotSet("mobile_number", None), FollowupAction(name="mobile_number_form")]
        except:
                #return [{"mobile_number": None}, FollowupAction(name="mobile_number_form")]


            dispatcher.utter_message(
                text=f"Unfortunately we could not validate your phone number" #: {mobile_number}."
            )
            
            return [SlotSet("mobile_number", None), FollowupAction(name="mobile_number_form")]



class ActionEmailOrSMS(Action):
    def name(self) -> Text:
        return "action_ask_contact_channel"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # num_guests = tracker.get_slot('num_guests')
        # buttons = [
        #     {
        #         "payload": '/confirmation_by_email{"contact_channel":"email"}',
        #         "title": "Email",
        #     },
        #     {
        #         "payload": '/confirmation_by_sms{"contatct_channel":"sms"}',
        #         "title": "SMS",
        #     },
        # ]

        buttons = [{"title": "SMS", "payload": "/inform_contact_channel{\"contact_channel\": \"SMS\"}"},
                   {"title": "Email", "payload": "/inform_contact_channel{\"contact_channel\": \"Email\"}"}]

        # Provide a message with buttons to ask the user about their preference
        # message = "How would you like to receive information?"
        # dispatcher.utter_message(text=message, buttons=buttons)



        dispatcher.utter_message(
            text="How would you like to receive the booking confirmation?",
            buttons=buttons,
        )

        # Set the slot 'preference' to None to clear any previous value
        return [SlotSet("contact_channel", None), FollowupAction("action_set_contact_channel")]
    
        # preference = tracker.latest_message.get('entities')[0]['value']

        # if preference == "SMS":
        #     print("action_set_contact_channel - SMS")
        #     dispatcher.utter_message(response="utter_ask_mobile_number")
        #     return [SlotSet("contact_channel", preference), FollowupAction("mobile_number_form")]
        # elif preference == "Email":
        #     print("action_set_contact_channel - email")
        #     dispatcher.utter_message(response="utter_ask_email")
        #     # Set the 'preference' slot to the user's choice
        #     return [SlotSet("contact_channel", preference), FollowupAction("email_form")]
        # else:
        #     print("action_set_contact_channel - ELSE")

# '        ##### EMAIL TESTS
#         subject = "A test mail sent by Python. It has an attachment."
#         content = """Hello,
#         This is a simple mail.
#         Thank You
#         """
#         email = tracker.get_slot("email")

#         utils.send_email(
#             email,
#             subject,
#             content,'
#       )
        ######

        return []
    
class ActionSetContactChannel(Action):
    def name(self) -> Text:
        return "action_set_contact_channel"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Get the user's preference from the intent
        preference = tracker.get_slot('contact_channel')
        #preference = tracker.latest_message.get('entities')[0]['value']

        if preference == "SMS":
            print("action_set_contact_channel - SMS")
            dispatcher.utter_message(response="utter_ask_mobile_number")
            return [SlotSet("contact_channel", preference), FollowupAction("mobile_number_form")]
        elif preference == "Email":
            print("action_set_contact_channel - email")
            dispatcher.utter_message(response="utter_ask_email")
            # Set the 'preference' slot to the user's choice
            return [SlotSet("contact_channel", preference), FollowupAction("email_form")]
        else:
            print(f"action_set_contact_channel - ELSE {preference}")


class ActionCalculateNumNights(Action):
    def name(self) -> Text:
        return "action_calculate_num_nights"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        date_format = "%Y-%m-%d"
        checkin_date = dt.strptime(tracker.get_slot("checkin_date"), date_format)
        checkout_date = dt.strptime(tracker.get_slot("checkout_date"), date_format)
        num_nights = (checkout_date - checkin_date).days

        buttons = [
            {"payload": "/change_checkout_date", "title": "Change checkout date"},
            {"payload": "/change_checkin_date", "title": "Change checkin date"},
        ]
        # {"payload": "/change_num_guests", "title": "Change number of guests"}] ### FIX probably not used in this context

        if int(num_nights) == 0:
            dispatcher.utter_message(
                text=f"Your checkout date {checkout_date} and checkin date {checkin_date} are identical. \
            Which date do you want to change?",
                buttons=buttons,
            )
            return []

        elif int(num_nights) < 0:
            dispatcher.utter_message(
                text=f"Your checkout date {checkout_date} is before the checkin date {checkin_date}. \
            Which date do you want to change?",
                buttons=buttons,
            )

            return []
        else:
            return [SlotSet("num_nights", num_nights)]

###################
class ActionAddBreakfast(Action):
    def name(self) -> Text:
        return "action_add_breakfast"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Triggering an intent from a custom action

        # if tracker.slots.get("slot_name"):
        #     slot_value = tracker.get_slot("slot_name")
        #     dispatcher.utter_message(f"The value of slot 'slot_name' is: {slot_value}")

        if tracker.get_slot("room_proposal"):
            return [SlotSet("include_breakfast", "yes")]
        else:
            # in the rare case that a customer wants breakfast but has not specified the dates, we start the stay form
            trigger_intent = "ask_availability"
            return [UserUtteranceReverted(),SlotSet("include_breakfast", "yes"), {"intent": trigger_intent}]






######################
class ActionSetCheckoutDate(Action):
    def name(self) -> Text:
        return "action_set_checkout_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dummy_date = tracker.get_slot(
            "checkin_date_dummy"
        )  # dt.strptime(tracker.get_slot('checkout_date'), date_format)
        try:
            checkout_date = dummy_date.get(
                "to"
            )  # this action should only be called from checkin_date_dummy validation if duckling returns a dict
            return [
                SlotSet("checkout_date", get_date(checkout_date)),
                SlotSet("checkin_date_dummy", None),
            ]
        except:
            checkout_date = None
        return [SlotSet("checkout_date", checkout_date)]


class ActionResetCheckinDate(Action):
    def name(self) -> Text:
        return "action_reset_checkin_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("checkin_date", None), SlotSet("num_nights", None), FollowupAction("stay_form")]


class ActionResetCheckoutDate(Action):
    def name(self) -> Text:
        return "action_reset_checkout_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("checkout_date", None), SlotSet("num_nights", None), FollowupAction("stay_form")]


class ActionResetNumGuests(Action):
    def name(self) -> Text:
        return "action_reset_num_guests"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("num_guests", None)]

class ActionResetNumSingleRooms(Action):
    def name(self) -> Text:
        return "action_reset_num_single_rooms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("num_single_rooms", None), ActiveLoop('room_type_form'), FollowupAction("room_type_form")]
    

class ActionResetNumDoubleRooms(Action):
    def name(self) -> Text:
        return "action_reset_num_double_rooms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("num_double_rooms", None), FollowupAction("room_type_form")]


class ActionCheckRoom(Action):
    def name(self) -> Text:
        return "action_check_rooms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # num_guests = tracker.get_slot("num_guests")
        checkin_date = tracker.get_slot("checkin_date")
        checkout_date = tracker.get_slot("checkout_date")
        num_single_rooms = tracker.get_slot("num_single_rooms")
        num_double_rooms = tracker.get_slot("num_double_rooms")

        # check availabilty on API
        room_proposal = utils.request_room_availability(
            checkin_date, checkout_date, num_single_rooms, num_double_rooms
        )

        # TODO:  include business logic for validating availabiliy vs. request
        if room_proposal["availability_issue"] == None:
            message = f"""We can offer you the following rooms: 
            Checkin date: {checkin_date}
            Checkout date: {checkout_date}
            {room_proposal["num_single_rooms_available"]} single rooms for {room_proposal["single_room_rate"]} Euros per room per night.
            {room_proposal["num_double_rooms_available"]} double rooms for {room_proposal["double_room_rate"]} Euros per room per night."""
            dispatcher.utter_message(text=message)
            #dispatcher.utter_message(response = "utter_ask_proceed_booking")
            return[SlotSet("room_proposal", True)] # , SlotSet("proceed_with_booking", True), FollowupAction("action_listen")]
        # message = f"Number of guests: {num_guests}"
        else:
            # message = f"Single room rate: {room_proposal.get('single_room_rate')}"
            message = (
                f"There is an availability issue: {room_proposal['availability_issue']}"
            )
            dispatcher.utter_message(text=message)
            #dispatcher.utter_message(response = "utter_change_stay_info")
            return [SlotSet("room_proposal", False), FollowupAction("utter_change_stay_info")]


class ActionNavigation(Action):
    def name(self) -> Text:
        return "action_display_navigation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload": "/ask_availability", "title": "Book a room"},
            {"payload": "/ask_room_price", "title": "Check room prices"},
        ]

        return []
    
###

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



#send_email(receiver_email, subject, content)
class ActionSendEmailConfirmation(Action):
    def name(self) -> Text:
        return "action_send_email_confirmation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        


        # take environment variables from .env.
        SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
        SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
        SMTP_STRING = os.getenv("SMTP_STRING")
        SMTP_PORT = os.getenv("SMTP_PORT")

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Mockup for quick testing:
        receiver_email = "newinmunich@aol.com"
        subject = "Booking Confirmation"
        content = "Lakeside Hotel is confirming your booking."
        #def send_email(receiver_email, subject, content):
            # Setup the MIME
        message = MIMEMultipart()
        message["From"] = SENDER_ADDRESS
        message["To"] = receiver_email
        message["Subject"] = subject
        # The body and the attachments for the mail
        message.attach(MIMEText(content, "plain"))
        text = message.as_string()

        # Create SMTP session for sending the mail
    #try:
        # session = smtplib.SMTP(SMTP_STRING, SMTP_PORT)
        # session.connect(SMTP_STRING, SMTP_PORT)
        # print("trying to login")
        # session.login(SENDER_ADDRESS, SENDER_EMAIL_PASSWORD)
        # print("connected")
        # #session.ehlo()
        # session.starttls(context=context)  # enable security

        # print("started tls")
 
        # print("Sending email")
        # session.sendmail(SENDER_ADDRESS, receiver_email, text)
        # session.quit()
        # print("Mail Sent")
    #except:
            #print("Email process failed")
            #return

        #send_email(receiver_email, subject, content)
        return [FollowupAction("utter_confirmation_by_email")]



###########################




class ActionPROMO(Action):
    def name(self) -> Text:
        return "action_PROMO"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        

        date_format = "%Y-%m-%d"
        checkin_date = "2023-12-02"#dt.strptime("2023-12-02", "%Y-%m-%d")
        #checkin_date = dt.strptime("2023-12-02", date_format)
        checkout_date = "2023-12-12"#dt.strptime("2023-12-12", date_format)

        SlotSet("checkin_date", checkin_date)# get_date(checkin_date))
        SlotSet("checkout_date", checkout_date)#get_date(checkout_date))
        SlotSet("num_single_rooms", "1")
        SlotSet("num_double_rooms", "2")

        return [SlotSet("checkin_date", checkin_date),
                SlotSet("checkout_date", checkout_date),
                SlotSet("num_single_rooms", 1),
                SlotSet("num_double_rooms", 2),
                FollowupAction("action_check_rooms")]
