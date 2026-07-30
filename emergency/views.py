import json

from .sms_service import send_emergency_sms_async
import traceback
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
        location_readable = location_readable if lat and lon else "Not shared"

    if note:
        message_parts.append(f"\nResponder's Note:\n{note}")
    else:
        message_parts.append("\nResponder's Note:\nNot provided.")

    message_body = "\n".join(message_parts)

    # print(f"\n--- FINAL DYNAMIC SMS CONTENT ---\n{message_body}\n--------------------------\n")
    print(f"\n{message_body}\n")

    location_readable = location_readable if lat and lon else "Not shared"
    send_emergency_sms_async(
        patient_name=patient.name,
        emergency_contact=patient.phone,
        location=location_readable,
        message_body=message_body,
        )

    send_emergency_sms_async(
        patient_name=patient.name,
        emergency_contact=patient.emergency_contact,
        location=location_readable,
        message_body=message_body,
        )

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


def verify_emergency_code_page(request):
    return render(request, 'verify.html')


def verify_emergency_code(request):
    if request.method == "POST":
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            entered_code = data.get("code")
            
            # Check if code was provided
            if not entered_code:
                return JsonResponse({"status": "error", "message": "Code is required"}, status=400)
            
            # Security Check: Does this specific code exist?
            # Note: Ensure 'patient_code' is the exact field name in your Patient model
            patient = Patient.objects.get(patient_code=entered_code)
            
            # If found, return success and the patient_id
            return JsonResponse({
                "status": "success", 
                "patient_id": patient.patient_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except Patient.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid emergency code"}, status=404)
        except Exception:
            # Print the actual error to your terminal for debugging
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
