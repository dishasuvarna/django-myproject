# alert
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

        if patient_id.startswith("PP"):
            patient_id = patient_id[1:]

    print("🔥 Received patient_id:", patient_id)

    # 🔹 FIND PATIENT
    patient = Patient.objects.filter(patient_id=patient_id).first()

    if not patient:
        return Response({'error': 'Invalid QR'}, status=404)

    # 🔹 GET GPS FROM FRONTEND
    lat = request.data.get('lat')
    lon = request.data.get('lon')

    if not lat or not lon:
        return Response({'error': 'Invalid location'}, status=400)

    # 🔹 DEFAULT LOCATION
    location_name = "Fetching location..."

    # 🔥 REVERSE GEOCODING
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

    # 🔹 TIME
    time_now = datetime.now().strftime("%I:%M %p")

    # 🔹 MAP LINK
    map_link = f"https://maps.google.com/?q={lat},{lon}"

    # 🔥 🔥 DETECT DOCTOR (SAFE METHOD)
    is_doctor = False

    if request.user.is_authenticated:
        if hasattr(request.user, 'doctor'):
            is_doctor = True

    # 🔥 DOCTOR DETAILS (SAFE FALLBACKS)
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

    # 🔥 MESSAGE LOGIC (FINAL CLEAN VERSION)

    if is_doctor:

        message = f"""
🚑 DOCTOR EMERGENCY RESPONSE 🚑  

Dr. {doctor_name} ({specialization})  
from {hospital_name} scanned the patient's QR code.

📍 Location: {location_name}  
🕒 Time: {time_now}

👉 View Exact Location:
{map_link}
"""

    else:
        # ✅ ORIGINAL MESSAGE (UNCHANGED)
        message = f"""
🚨 EMERGENCY ALERT 🚨  

{patient.name}'s QR code was scanned.

📍 Location: {location_name}  
🕒 Time: {time_now}

👉 View Exact Location:
{map_link}
"""

    # 🔥 SEND SMS (UNCHANGED)
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