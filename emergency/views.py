
# import json
# import requests
# from datetime import datetime
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.http import JsonResponse
# from django.shortcuts import render, get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
# from core.models import Patient
# from emergency.sms_service import send_emergency_sms_async

# # --- ACCURATE HELPER FUNCTION ---

# def _get_readable_location(latitude, longitude):
#     """Fetches high-precision address and returns a clean, human-readable format."""
#     try:
#         headers = {"User-Agent": "SmartEmergencyQR/1.0 (your-email@example.com)"}
#         params = {
#             "format": "jsonv2",
#             "lat": latitude,
#             "lon": longitude,
#             "zoom": 18,
#             "addressdetails": 1,
#             "accept-language": "en"
#         }
        
#         response = requests.get(
#             "https://nominatim.openstreetmap.org/reverse",
#             params=params, headers=headers, timeout=5
#         )

#         if response.ok:
#             data = response.json()
#             addr = data.get("address", {})
#             # Construct a cleaner, more accurate address string
#             parts = [
#                 addr.get("house_number"), addr.get("road"), 
#                 addr.get("suburb"), addr.get("city") or addr.get("town"), 
#                 addr.get("state"), addr.get("postcode")
#             ]
#             readable = ", ".join([p for p in parts if p])
#             return readable if readable else data.get("display_name", f"{latitude}, {longitude}")
            
#     except Exception as e:
#         print(f"Geocoding error: {e}")
    
#     return f"Lat: {latitude}, Lon: {longitude}"

# # --- VIEWS ---

# @api_view(['POST'])
# def save_location(request):
#     return Response({"status": "saved", "lat": request.data.get('lat'), "lon": request.data.get('lon')})

# @api_view(['POST'])
# def scan_qr(request):
#     patient_id = request.data.get('patient_id', '').strip()
#     if patient_id.startswith("PP"): patient_id = patient_id[1:]

#     patient = Patient.objects.filter(patient_id=patient_id).first()
#     if not patient: return Response({'error': 'Invalid QR'}, status=404)

#     lat, lon = request.data.get('lat'), request.data.get('lon')
#     if not lat or not lon: return Response({'error': 'Invalid location'}, status=400)

#     location_name = _get_readable_location(lat, lon)
#     map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
#     message = f"EMERGENCY ALERT\nPatient: {patient.name}\nLoc: {location_name}\nLink: {map_link}"

#     # TERMINAL DEBUG
#     print(f"\n--- QR SCAN SMS CONTENT ---\n{message}\n---------------------------\n")

#     if patient.phone: send_sms(patient.phone, message)
#     if patient.emergency_contact: send_sms(patient.emergency_contact, message)
#     return Response({'status': 'sent'})

# # # @csrf_exempt
# # # def emergency_alert(request, patient_id):
# # #     patient = Patient.objects.filter(patient_id=patient_id).select_related("user").first()
# # #     if not patient: return JsonResponse({"error": "Not found"}, status=404)

# # #     data = json.loads(request.body.decode("utf-8") or "{}")
# # #     lat, lon = data.get("latitude"), data.get("longitude")
# # #     location = _get_readable_location(lat, lon) if lat and lon else "Location unavailable"
# # #     map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else ""
    
# # #     message_body = f"EMERGENCY ALERT\nPatient: {patient.name}\nLoc: {location}\nMap: {map_link}"

# # #     # TERMINAL DEBUG
# # #     print(f"\n--- EMERGENCY ALERT SMS CONTENT ---\n{message_body}\n-----------------------------------\n")

# # #     contacts = list(filter(None, [patient.phone, patient.emergency_contact]))
# # #     for contact in set(contacts):
# # #         send_emergency_sms_async(patient.name, contact, location, message_body)

# # #     return JsonResponse({"status": "sent", "location": location})


# @csrf_exempt
# def emergency_alert(request, patient_id):
#     patient = Patient.objects.filter(patient_id=patient_id).first()
#     if not patient: return JsonResponse({"error": "Not found"}, status=404)

#     data = json.loads(request.body.decode("utf-8"))
#     lat = data.get("latitude")
#     lon = data.get("longitude")

#     location_name = _get_readable_location(lat, lon)
    
#     map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    
#     message_body = f"EMERGENCY ALERT\nPatient: {patient.name}\nLoc: {location_name}\nMap: {map_link}"

    
#     print(f"\n--- FINAL SMS CONTENT ---\n{message_body}\n--------------------------\n")

#     return JsonResponse({"status": "sent"})





# @csrf_exempt
# def reverse_location(request):
#     data = json.loads(request.body.decode("utf-8") or "{}")
#     lat, lon = data.get("latitude") or data.get("lat"), data.get("longitude") or data.get("lon")
#     return JsonResponse({"location": _get_readable_location(lat, lon)})

# def scan_qr_page(request):
#     patient = get_object_or_404(Patient, patient_id=request.GET.get('patient_id'))
#     return render(request, 'scan.html', {'patient': patient})

# def send_sms(number, message):
#     print(f"SMS sent to {number}:\n{message}")



import json
import requests
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from core.models import Patient

# --- 1. HELPER FUNCTION ---
def _get_readable_location(latitude, longitude):
    """Fetches high-precision address using OpenStreetMap Nominatim."""
    try:
        headers = {"User-Agent": "SmartEmergencyQR/1.0"}
        params = {
            "format": "jsonv2",
            "lat": latitude,
            "lon": longitude,
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "en"
            # "accept-language": "en-US,en;q=0.9"
        }
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params=params, headers=headers, timeout=5
        )
        if response.ok:
            data = response.json()
            addr = data.get("address", {})
            # parts = [addr.get("road"), addr.get("suburb"), addr.get("city") or addr.get("town"), addr.get("state"), addr.get("postcode")]
            # readable = ", ".join([p for p in parts if p])
            city = addr.get("city") or addr.get("town") or addr.get("village")
            state = addr.get("state")
            pincode = addr.get("postcode")
            location_parts = [part for part in [city, state, pincode] if part]
            readable = ", ".join(location_parts)
            # return readable if readable else data.get("display_name", f"{latitude}, {longitude}")
            if readable:
                return f"{readable} (GPS: {latitude}, {longitude})"
    except Exception as e:
        print(f"Geocoding error: {e}")
    # return f"Lat: {latitude}, Lon: {longitude}"
    return f"GPS Coordinates: {latitude}, {longitude}"

# --- 2. VIEWS ---

@csrf_exempt
def emergency_alert(request, patient_id):
    print(f"\n[DEBUG] RECEIVED REQUEST for Patient ID: {patient_id}")
    print(f"[DEBUG] Request Body: {request.body.decode('utf-8')}")
    patient = Patient.objects.filter(patient_id=patient_id).first()
    if not patient:
        print("[DEBUG] Patient NOT FOUND in database!")
        return JsonResponse({"error": "Patient not found"}, status=404)

    data = json.loads(request.body.decode("utf-8"))
    lat = data.get("latitude")
    lon = data.get("longitude")
    note = data.get("message", "").strip()
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Dynamic Message Assembly
    message_parts = [
        "Smart Emergency QR Alert",
        f"Patient: {patient.name}",
        "Your Emergency QR was scanned.",
        f"Time: {timestamp}"
    ]

    if lat and lon:
        location_readable = _get_readable_location(lat, lon)
        map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        message_parts.append(f"\nEmergency Detected At:\n{location_readable}")
        message_parts.append(f"Google Maps:\n{map_link}")
    else:
        message_parts.append("\nEmergency Detected At:\nLocation not shared by the responder.")

    if note:
        message_parts.append(f"\nResponder's Note:\n{note}")
    else:
        message_parts.append("\nResponder's Note:\nNot provided.")

    message_body = "\n".join(message_parts)

    # print(f"\n--- FINAL DYNAMIC SMS CONTENT ---\n{message_body}\n--------------------------\n")
    print(f"\n{message_body}\n")

    return JsonResponse({"status": "sent", "message": "Alert processed"})

@api_view(['POST'])
def save_location(request):
    return Response({"status": "saved"})

@api_view(['POST'])
def scan_qr(request):
    return Response({'status': 'sent'})

@csrf_exempt
def reverse_location(request):
    data = json.loads(request.body.decode("utf-8") or "{}")
    lat, lon = data.get("latitude") or data.get("lat"), data.get("longitude") or data.get("lon")
    return JsonResponse({"location": _get_readable_location(lat, lon)})

def scan_qr_page(request):
    patient = get_object_or_404(Patient, patient_id=request.GET.get('patient_id'))
    return render(request, 'scan.html', {'patient': patient})

def send_sms(number, message):
    print(f"SMS sent to {number}:\n{message}")