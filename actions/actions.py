# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, ValidationAction, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

from datetime import datetime as dt

def get_date(time):
    try:
        time_object = dt.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")
        date = str(time_object.date())
        return date
    except:
        return "get_date_exception"


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
            # DucklingEntityExtractor returns a dict when it extracts a date range
            return [{"checkin_date": get_date(slot_value["from"])}, 
                {"checkout_date": get_date(slot_value["to"])}]
            #return {"checkin_date": slot_value.capitalize()}
        else:
            # validation failed, set this slot to None
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
            [{"checkin_date": get_date(slot_value["from"])}, 
                {"checkout_date": get_date(slot_value["to"])}]

            #return {"checkin_date": slot_value.capitalize()}
        else:
            # validation failed, set this slot to None
            return {"checkout_date": get_date(slot_value)}

class ValidatePredefinedSlots(ValidationAction):
    def validate_checkin_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate checkin_date."""
        if isinstance(slot_value, dict):
            # DucklingEntityExtractor returns a dict when it extracts a date range
            return [{"checkin_date": get_date(slot_value["from"])}, 
                {"checkout_date": get_date(slot_value["to"])}]
            #return {"checkin_date": slot_value.capitalize()}
        else:
            # validation failed, set this slot to None
            return {"checkin_date": get_date(slot_value)}


# class EmailValidation(ValidationAction):
# #
#     def name(self) -> Text:
#         return "validate_email"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # validate the email address
#         entities = tracker.latest_message['entities']
#         dispatcher.utter_message(text=entities)

#         return []


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
        return