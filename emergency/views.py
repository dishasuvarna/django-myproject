#alert
import requests


from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.shortcuts import render, get_object_or_404

from core.models import Patient

# 🔹 Dummy SMS (later replace with Twilio)
def send_sms(number, message):
    print(f"📩 SMS sent to {number}:\n{message}")

def make_call(number):
    print("Calling:", number)


# 🔥 SAVE LOCATION (SEPARATE FUNCTION)
@api_view(['POST'])
def save_location(request):
    lat = request.data.get('lat')
    lon = request.data.get('lon')

    print("📍 Saved Location:", lat, lon)

    return Response({
        "status": "saved",
        "lat": lat,
        "lon": lon
    })



# 🔥 MAIN QR SCAN FUNCTION
@api_view(['POST'])
def scan_qr(request):

    # 🔹 GET PATIENT ID
    patient_id = request.data.get('patient_id')

    if patient_id:
        patient_id = patient_id.strip()

        # remove wrong PP case
        if patient_id.startswith("PP"):
            patient_id = patient_id[1:]

    print("🔥 Received patient_id:", patient_id)

    # 🔹 FIND PATIENT
    patient = Patient.objects.filter(patient_id=patient_id).first()

    if not patient:
        # print("❌ Patient NOT FOUND:", patient_id)
        return Response({'error': 'Invalid QR'}, status=404)

    # 🔹 GET GPS FROM FRONTEND
    lat = request.data.get('lat')
    lon = request.data.get('lon')

    # 🔹 DEFAULT LOCATION
    location_name = "Fetching location..."

    # 🔥 REVERSE GEOCODING (REAL LOCATION)
    if lat and lon:
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            # res = requests.get(url, timeout=3)
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 18,
                "addressdetails": 1
           }
            res = requests.get(url, params=params, timeout=5, headers={
            "User-Agent": "emergency-system"
        })
            data = res.json()

            address = data.get('address', {})
            # 🔥 BETTER EXTRACTION
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

    # 🔹 TIME
    time_now = datetime.now().strftime("%I:%M %p")

    # 🔹 MAP LINK
    map_link = f"https://maps.google.com/?q={lat},{lon}"

    # 🔹 MESSAGE FORMAT (AS YOU WANTED)
    message = f"""
🚨 EMERGENCY ALERT 🚨  

{patient.name}'s QR code was scanned.

📍 Location: {location_name}  
🕒 Time: {time_now}

👉 View Exact Location:
https://maps.google.com/?q={lat},{lon}
"""

    # # 🔹 SEND SMS TO BOTH CONTACTS
    # status_list = []

    # if patient.phone:
    #     send_sms(patient.phone, message)
    #     status_list.append("phone")

    # if hasattr(patient, 'emergency_contact') and patient.emergency_contact:
    #     send_sms(patient.emergency_contact, message)
    #     status_list.append("emergency")

    # # 🔹 PRINT (for testing)
    # print(message)

    # # 🔒 LOCK AFTER SEND
    # patient.alert_sent = True
    # patient.save()

    # # 🔹 RESPONSE TO FRONTEND
    # return Response({
    #     'status': 'sent',
    #     'sent_to': status_list
    # })



    # 🔥 SEND SMS
    if hasattr(patient, 'phone') and patient.phone:
        send_sms(patient.phone, message)

    if hasattr(patient, 'emergency_contact') and patient.emergency_contact:
        send_sms(patient.emergency_contact, message)

    print(message)

    return Response({'status': 'sent'})


# 🔹 SCAN PAGE (NO CHANGE)
def scan_qr_page(request):
    patient_id = request.GET.get('patient_id')

    patient = get_object_or_404(Patient, patient_id=patient_id)

    return render(request, 'scan.html', {
        'patient': patient
    })