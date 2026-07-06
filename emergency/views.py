# alert
import json
import requests

from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from core.models import Patient
from emergency.sms_service import send_emergency_sms_async


  # Dummy SMS
def send_sms(number, message):
      print(f"SMS sent to {number}:\n{message}")


def make_call(number):
      print("Calling:", number)


  # SAVE LOCATION
@api_view(['POST'])
def save_location(request):
      lat = request.data.get('lat')
      lon = request.data.get('lon')

      print("Saved Location:", lat, lon)

      return Response({
          "status": "saved",
          "lat": lat,
          "lon": lon
      })


  # MAIN QR SCAN FUNCTION
@api_view(['POST'])
def scan_qr(request):
      patient_id = request.data.get('patient_id')

      if patient_id:
          patient_id = patient_id.strip()

          if patient_id.startswith("PP"):
              patient_id = patient_id[1:]

      print("Received patient_id:", patient_id)

      patient = Patient.objects.filter(patient_id=patient_id).first()

      if not patient:
          return Response({'error': 'Invalid QR'}, status=404)

      lat = request.data.get('lat')
      lon = request.data.get('lon')

      if not lat or not lon:
          return Response({'error': 'Invalid location'}, status=400)

      location_name = "Fetching location..."

      try:
          params = {
              "lat": lat,
              "lon": lon,
              "format": "json",
              "zoom": 18,
              "addressdetails": 1
          }

          res = requests.get(
              "https://nominatim.openstreetmap.org/reverse",
              params=params,
              timeout=5,
              headers={"User-Agent": "emergency-system"}
          )

          data = res.json()
          address = data.get('address', {})

          city = (
              address.get('city') or
              address.get('town') or
              address.get('village') or
              address.get('municipality')
          )

          state = address.get('state')

          if city and state:
              location_name = f"{city}, {state}"
          elif state:
              location_name = state
          else:
              location_name = "Exact location available in map"

      except Exception as e:
          print("Geocoding error:", e)
          location_name = "Exact location in map"

      time_now = datetime.now().strftime("%I:%M %p")
      map_link = f"https://maps.google.com/?q={lat},{lon}"

      is_doctor = False

      if request.user.is_authenticated:
          if hasattr(request.user, 'doctor'):
              is_doctor = True

      doctor_name = ""
      specialization = "General"
      hospital_name = "Hospital"

      if is_doctor:
          user = request.user
          doctor_name = user.get_full_name() or user.username
          doctor = getattr(user, 'doctor', None)

          if doctor:
              specialization = getattr(doctor, 'specialization', "General")
              hospital_name = getattr(doctor, 'hospital_name', "Hospital")

      if is_doctor:
          message = f"""
  DOCTOR EMERGENCY RESPONSE

  Dr. {doctor_name} ({specialization})
  from {hospital_name} scanned the patient's QR code.

  Location: {location_name}
  Time: {time_now}

  View Exact Location:
  {map_link}
  """
      else:
          message = f"""
  EMERGENCY ALERT

  {patient.name}'s QR code was scanned.

  Location: {location_name}
  Time: {time_now}

  View Exact Location:
  {map_link}
  """

      if hasattr(patient, 'phone') and patient.phone:
          send_sms(patient.phone, message)

      if hasattr(patient, 'emergency_contact') and patient.emergency_contact:
          send_sms(patient.emergency_contact, message)

      print(message)

      return Response({'status': 'sent'})


@csrf_exempt
def emergency_alert(request, patient_id):
        if request.method != "POST":
            return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

        patient = Patient.objects.filter(patient_id=patient_id).select_related("user").first()

        if not patient:
            return JsonResponse({"error": "Patient not found"},
            status=404)

        try:
            data = json.loads(request.body.decode("utf-8") or
            "{}")
        except json.JSONDecodeError:
            data = {}

        rescuer_message = data.get("message") or "No rescuer message provided"
        location = data.get("location") or "Location not available"
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude and longitude and (
            location == "Location not available" or
            location == "Location permission denied" or
            location.startswith("Coordinates:")
        ):
            location = _get_readable_location(latitude,
            longitude)

        map_link = ""
        if latitude and longitude:
            map_link = f"https://maps.google.com/?q={latitude},{longitude}"

        message_body = (
            f"EMERGENCY ALERT\n"
            f"Patient: {patient.name}\n"
            f"Patient ID: {patient.patient_id}\n"
            f"Blood Group: {patient.blood_group}\n"
            f"Allergies: {patient.allergies or 'None'}\n"
            f"Rescuer Message: {rescuer_message}\n"
            f"Location: {location}\n"
        )

        if map_link:
            message_body += f"Map: {map_link}\n"

        contacts = []

        if patient.phone:
            contacts.append(patient.phone)

        profile = getattr(patient.user, "profile", None)
        if profile and profile.phone:
            contacts.append(profile.phone)

        if patient.emergency_contact:
            contacts.append(patient.emergency_contact)

        unique_contacts = []
        for contact in contacts:
            if contact and contact not in unique_contacts:
                unique_contacts.append(contact)

        for contact in unique_contacts:
            send_emergency_sms_async(
                patient.name,
                contact,
                location,
                message_body
            )

        return JsonResponse({
            "status": "sent",
            "contacts_count": len(unique_contacts),
            "location": location
        })
def _get_readable_location(latitude, longitude):
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "format": "json",
                    "lat": latitude,
                    "lon": longitude,
                    "zoom": 18,
                    "addressdetails": 1
                },
                headers={"User-Agent":
                "DjangoEmergencyAlert/1.0"},
                timeout=5
            )

            if not response.ok:
                return f"Coordinates: {latitude}, {longitude}"

            data = response.json()
            return data.get("display_name") or f"Coordinates:{latitude}, {longitude}"
        except Exception:
            return f"Coordinates: {latitude}, {longitude}"


@csrf_exempt
def reverse_location(request):
      if request.method != "POST":
          return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

      try:
          data = json.loads(request.body.decode("utf-8") or "{}")
      except json.JSONDecodeError:
          data = {}

      latitude = data.get("latitude") or data.get("lat")
      longitude = data.get("longitude") or data.get("lon")

      if not latitude or not longitude:
          return JsonResponse({"error": "Latitude and longitude are required"}, status=400)

      location = _get_readable_location(latitude, longitude)

      return JsonResponse({
          "location": location
      })


  # SCAN PAGE
def scan_qr_page(request):
      patient_id = request.GET.get('patient_id')

      patient = get_object_or_404(Patient, patient_id=patient_id)

      return render(request, 'scan.html', {
          'patient': patient
      })
