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
    FollowupAction,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)

from datetime import datetime as dt
from email_validator import validate_email, EmailNotValidError

# import imp
import importlib

from sqlalchemy import except_
import actions.utils as utils

# imp.reload(utils)
importlib.reload(utils)


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
# class ValidateRoomTypeForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_room_type_form"

#     def validate_num_single_rooms(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate number of single rooms"""
#         if isinstance(slot_value, int):
#             if slot_value < 0:
#                 dispatcher.utter_message(
#                     text="This is not a valid number for rooms."
#                 )  ### better explanation would be helpful
#                 return {"num_single_rooms": None}
#             else:
#                 return {"num_single_rooms": slot_value}
#         else:
#             dispatcher.utter_message(
#                 text="Please provide a full positive numer."
#             )  ### better explanation would be helpful
#             return {"num_single_rooms": None}

#     def validate_num_double_rooms(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate number of double rooms"""
#         if isinstance(slot_value, int):
#             if slot_value < 0:
#                 dispatcher.utter_message(
#                     text="This is not a valid number for rooms."
#                 )  ### better explanation would be helpful
#                 return {"num_double_rooms": None}
#             else:
#                 return {}  # {"num_double_rooms": slot_value}
#         else:
#             dispatcher.utter_message(
#                 text="Please provide a full positive numer."
#             )  ### better explanation would be helpful
#             return {"num_double_rooms": None}


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
            print("is no dict")
            # SlotSet("checkin_date", get_date(slot_value))
            # FollowupAction(name="stay_form") # not necessary due to detected intent
            return {"checkin_date": get_date(slot_value)}

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

    def validate_mobile_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        """ "
        check if a phone number was extracted
        """
        entities = tracker.latest_message["entities"]
        for e in entities:
            if e.get("entity") == "phone-number":
                phone = e.get("value")
                print(f"Phone was provided: {phone}")

                """Validate phone number."""
                try:
                    # Validate and format the phone number
                    valid_phone, phone_num_formated = utils.validate_phone_number(phone)
                    # dispatcher.utter_message(
                    #    text=f"Phone: {phone_num_formated} is {valid_phone}"
                    # )
                    if valid_phone:
                        dispatcher.utter_message(response="utter_mobile_number")
                        return {"mobile_number": phone_num_formated}
                    else:
                        dispatcher.utter_message(
                            text=f"Phone: {phone_num_formated} is not a valid number."
                        )
                        FollowupAction(
                            name="mobile_number_form"
                        )  #### Check if this works
                        return {"mobile_number": None}
                except:
                    print("validation failed")
                    dispatcher.utter_message(
                        text=f"Unfortunately we could not validate this phone number: {phone_num_formated}."
                    )
                    FollowupAction(name="mobile_number_form")
                    return {"mobile_number": None}

            else:
                print("no phone number")
                dispatcher.utter_message(
                    text=f"Your last message did not contain a valid phone number."
                )
                FollowupAction(name="mobile_number_form")
                return {"mobile_number": None}


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

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # num_guests = tracker.get_slot('num_guests')
        buttons = [
            {
                "payload": '/confirmation_by_email{"contact_channel":"email"}',
                "title": "Email",
            },
            {
                "payload": '/confirmation_by_sms{"contatct_channel":"sms"}',
                "title": "SMS",
            },
        ]

        dispatcher.utter_message(
            text="How would you like to receive the booking confirmation?",
            buttons=buttons,
        )

        ##### EMAIL TESTS
        subject = "A test mail sent by Python. It has an attachment."
        content = """Hello,
        This is a simple mail.
        Thank You
        """
        email = tracker.get_slot("email")

        utils.send_email(
            email,
            subject,
            content,
        )
        ######

        return []


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
        return [SlotSet("checkin_date", None), SlotSet("num_nights", None)]


class ActionResetCheckoutDate(Action):
    def name(self) -> Text:
        return "action_reset_checkout_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("checkout_date", None), SlotSet("num_nights", None)]


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


class ActionCheckRoom(Action):
    def name(self) -> Text:
        return "action_check_rooms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        num_guests = tracker.get_slot("num_guests")
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
            \n Checkin date: {checkin_date}
            \n Checkout date: {checkout_date}
            \n {room_proposal["num_single_rooms_available"]} single rooms for {room_proposal["single_room_rate"]} Euros per room per night.
            """
            dispatcher.utter_message(text=message)
        # message = f"Number of guests: {num_guests}"
        else:
            # message = f"Single room rate: {room_proposal.get('single_room_rate')}"
            message = (
                f"There is an availability issue {room_proposal['availability_issue']}"
            )
            dispatcher.utter_message(text=message)
        return [SlotSet("room_proposal", room_proposal)]


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
