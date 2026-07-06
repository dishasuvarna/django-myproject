import logging
import os
import threading

from twilio.rest import Client

logger = logging.getLogger(__name__)


def send_emergency_sms_async(patient_name, emergency_contact,
  location, message_body):
      thread = threading.Thread(
          target=_send_emergency_sms,
          args=(patient_name, emergency_contact, location,
          message_body),
          daemon=True,
      )
      thread.start()


def _send_emergency_sms(patient_name, emergency_contact,
  location, message_body):
      to_number = _normalize_phone_number(emergency_contact)

      if not to_number:
          logger.error("Emergency SMS failed: missing contact for %s", patient_name)
          return

      account_sid = os.getenv("TWILIO_ACCOUNT_SID")
      auth_token = os.getenv("TWILIO_AUTH_TOKEN")
      from_number = os.getenv("TWILIO_PHONE_NUMBER")

      if not account_sid or not auth_token or not from_number:
          logger.error("Emergency SMS failed: Twilio environment variables are missing")
          return

      client = Client(account_sid, auth_token)

      try:
          client.messages.create(
              body=message_body,
              from_=from_number,
              to=to_number,
          )
      except Exception as exc:
          logger.exception("Emergency SMS failed: %s", exc)


def _normalize_phone_number(phone_number):
      if not phone_number:
          return None

      phone_number = str(phone_number).strip()

      if phone_number.startswith("+"):
          return phone_number

      digits = "".join(character for character in phone_number
      if character.isdigit())

      if len(digits) == 10:
          return f"+91{digits}"

      if len(digits) == 12 and digits.startswith("91"):
          return f"+{digits}"

      return None