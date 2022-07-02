# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import email
from html import entities
import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, ValidationAction, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)

from datetime import datetime as dt
from email_validator import validate_email, EmailNotValidError
import imp
import utils

imp.reload(utils)

def get_date(time):
    # check if the date needs to be cleaned up
    try:
        time_object = dt.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")
        date = str(time_object.date())
        return date
    except:
        return time


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
            return [
                {"checkin_date": get_date(slot_value.get("from"))},
                {"checkout_date": get_date(slot_value.get("to"))},
            ]
            # return {"checkin_date": slot_value.capitalize()}
        else:
            # validation failed, set this slot to None
            print("valdiate Stay form - checkin date -  no dict")
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
            [
                {"checkin_date": get_date(slot_value.get("from"))},
                {"checkout_date": get_date(slot_value.get("to"))},
            ]

            # return {"checkin_date": slot_value.capitalize()}
        else:
            # validation failed, set this slot to None
            return {"checkout_date": get_date(slot_value)}


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
        entities = tracker.latest_message["entities"]
        for e in entities:
            if e.get("entity") == "email":
                email = e.get("value")
                print(f"Email was provided: {email}")

                """Validate email."""
                try:
                    # Validate & take the normalized form of the email
                    # address for all logic beyond this point (especially
                    # before going to a database query where equality
                    # does not take into account normalization).

                    # email = validate_email(entities.get("email")).email
                    # email = validate_email(slot_value).email
                    # print(email)
                    dispatcher.utter_message(response="utter_email")
                    return {"email": email}

                except EmailNotValidError as e:
                    # email is not valid, exception message is human-readable
                    print(str(e))
                    dispatcher.utter_message(response="utter_no_email")
                    dispatcher.utter_message(text=str(e))
                    dispatcher.utter_message(text="Validate predefined slots")
                    return {"email": None}

            else:
                print("no email")
                return {"email": None}

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
            #tracker.set_slot("checkout_date", get_date(slot_value.get("to")))  ### FIX: 'Tracker' object has no attribute 'set_slot'
            #SlotSet("checkout_date", get_date(slot_value.get("to")))  ### FIX: This crashes 
            
            return {"checkin_date": get_date(slot_value.get("from"))}
            #return {"checkout_date": get_date(slot_value.get("to"))}
            #return {"checkin_date": get_date(slot_value.get("from")), 
            #       "checkout_date": get_date(slot_value.get("to"))}
            #return [SlotSet("checkin_date", get_date(slot_value.get("from"))),
            #        SlotSet("checkout_date", get_date(slot_value.get("to")))]

        else:
            # DucklingEntityExtractor returns a string for a single date/time
            print("is no dict")
            return {"checkin_date": get_date(slot_value)}
            #return SlotSet("checkin_date", get_date(slot_value))

    def validate_email(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:

            """"
            check if an email entity was extracted
            """
            entities = tracker.latest_message['entities']
            for e in entities:
                if e.get("entity")== "email":
                    email = e.get("value")
                    print (f"Email was provided: {email}")
                
                    """Validate email."""
                    try: 
                        # Validate & take the normalized form of the email
                        # address for all logic beyond this point (especially
                        # before going to a database query where equality
                        # does not take into account normalization).

                        #email = validate_email(entities.get("email")).email
                        #email = validate_email(slot_value).email
                        #print(email)
                        dispatcher.utter_message(response="utter_email")
                        return {"email": email}

                    except EmailNotValidError as e:
                        # email is not valid, exception message is human-readable
                        print(str(e))
                        dispatcher.utter_message(response="utter_no_email")
                        dispatcher.utter_message(text=str(e))
                        dispatcher.utter_message(text= "Validate predefined slots")
                        return {"email": None}
                    
                else:
                    print("no email")
                    return {"email": None}

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
        try:
            entities = tracker.latest_message["entities"]
            dispatcher.utter_message(text=str(entities))  # only for debugging purposes

            # get the value from the 'email' entity if it has been provided
            for e in entities:
                if e.get("entity") == "email":
                    email = e.get("value")
                    # print(f"Email was provided: {email}")
                else:
                    # print("NO Email was provided")
                    dispatcher.utter_message(response="utter_no_email")
        except:
            email = None

        if email is not None:
            # validate the email
            try:
                validate_email(email)
                # print(email)
            except EmailNotValidError as e:
                dispatcher.utter_message(response="utter_no_email")
                dispatcher.utter_message(text=str(e))
                # print(e)
                email = None
        else:
            dispatcher.utter_message(response="utter_no_email")
        return [SlotSet("email", email)]

class ActionEmailOrSMS(Action):
    def name(self) -> Text:
        return "action_email_or_sms"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #num_guests = tracker.get_slot('num_guests')
        buttons = [{"payload": '/confirmation_by_email{"contact_channel":"email"}', "title": "Email"},
            {"payload": '/confirmation_by_sms{"contatct_channel":"sms"}', "title": "SMS"}]
        
        dispatcher.utter_message(text="How would you like to receive the booking confirmation?", buttons=buttons)

        ##### EMAIL TESTS
        subject = 'A test mail sent by Python. It has an attachment.' 
        content = '''Hello,
        This is a simple mail.
        Thank You
        '''
        email = tracker.get_slot('email')

        utils.send_email(email, subject, content, )
        ######


        return []


class ActionCalculateNumNights(Action):
    def name(self) -> Text:
        return "action_calculate_num_nights"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date_format = "%Y-%m-%d"
        checkin_date = dt.strptime(tracker.get_slot('checkin_date'), date_format)
        checkout_date = dt.strptime(tracker.get_slot('checkout_date'), date_format)
        num_nights = (checkout_date - checkin_date).days

        buttons = [{"payload": "/change_checkout_date", "title": "Change checkout date"}, 
            {"payload": "/change_checkin_date", "title": "Change checkin date"},
            {"payload": "/change_num_guests", "title": "Change number of guests"}] ### FIX probably not used in this context
        
        if int(num_nights) == 0:
            dispatcher.utter_message(text=f"Your checkout date {checkout_date} and checkin date {checkin_date} are identical. \
            Which date do you want to change?", buttons=buttons)
            return []

        elif int(num_nights) < 0:
            dispatcher.utter_message(text=f"Your checkout date {checkout_date} is before the checkin date {checkin_date}. \
            Which date do you want to change?", buttons=buttons)
            return []
        else:
            return [SlotSet("num_nights", num_nights)]

class ActionResetCheckinDate(Action):
    def name(self) -> Text:
        return "action_reset_checkin_date"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("checkin_date", None),
                SlotSet("num_nights", None)]

class ActionResetCheckoutDate(Action):
    def name(self) -> Text:
        return "action_reset_checkout_date"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("checkout_date", None),
        SlotSet("num_nights", None)]

class ActionResetNumGuests(Action):
    def name(self) -> Text:
        return "action_reset_num_guests"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("num_guests", None)]



class ActionCheckRoom(Action):
    def name(self) -> Text:
        return "action_check_rooms"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        num_guests = tracker.get_slot('num_guests')
        #q = "select * from restaurants where cuisine='{0}' limit 1".format(cuisine)
        #result = db.query(q)
        message = f"Number of guests: {num_guests}"
        dispatcher.utter_message(text=message)
        #return [SlotSet("matches", result if result is not None else [])]
        return []
