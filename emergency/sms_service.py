from django.conf import settings # Import this

def _send_emergency_sms(patient_name, emergency_contact, location, latitude, longitude):
    to_number = _normalize_phone_number(emergency_contact)

    if not to_number:
        logger.error("Emergency SMS failed: missing emergency contact for %s", patient_name)
        return

    # Use settings instead of os.getenv
    account_sid = settings.TWILIO_ACCOUNT_SID 
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_PHONE_NUMBER

    if not account_sid or not auth_token or not from_number:
        logger.error("Emergency SMS failed: Twilio environment variables are missing")
        return
    
   

import logging
import os
import threading

from twilio.rest import Client


logger = logging.getLogger(__name__)


def send_emergency_sms_async(patient_name, emergency_contact, location, latitude, longitude):
    thread = threading.Thread(
        target=_send_emergency_sms,
        args=(patient_name, emergency_contact, location, latitude, longitude),
        daemon=True,
    )
    thread.start()


def _send_emergency_sms(patient_name, emergency_contact, location, latitude, longitude):
    to_number = _normalize_phone_number(emergency_contact)

    if not to_number:
        logger.error("Emergency SMS failed: missing emergency contact for %s", patient_name)
        return

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not from_number:
        logger.error("Emergency SMS failed: Twilio environment variables are missing")
        return

    message = _build_message(patient_name, location, latitude, longitude)
    client = Client(account_sid, auth_token)

    for attempt in range(2):
        try:
            print(f"DEBUG: Checking Phone Number - '{from_number}'")
            client.messages.create(
                body=message,
                from_=from_number,
                to=to_number,
            )
            return
        except Exception as exc:
            if attempt == 1:
                logger.exception("Emergency SMS failed after retry: %s", exc)


def _build_message(patient_name, location, latitude, longitude):
    location_text = location or f"Coordinates: {latitude}, {longitude}"
    return f"Emergency access verified for {patient_name}. Location: {location_text}"


def _normalize_phone_number(phone_number):
    if not phone_number:
        return None

    phone_number = str(phone_number).strip()

    if phone_number.startswith("+"):
        return phone_number

    digits = "".join(character for character in phone_number if character.isdigit())

    if len(digits) == 10:
        return f"+91{digits}"

    return digits if digits.startswith("91") else None
