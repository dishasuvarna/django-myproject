from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Patient, Doctor, Appointment, Prescription
from django.shortcuts import render

# -------------------------
# Register Patient
# -------------------------
@csrf_exempt
def register_patient(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})

    name = request.POST.get("name")
    age = request.POST.get("age")
    gender = request.POST.get("gender")
    phone = request.POST.get("phone")

    if not name or not age or not gender or not phone:
        return JsonResponse({"error": "All fields are required"})

    patient = Patient.objects.create(
        name=name,
        age=age,
        gender=gender,
        phone=phone
    )

    return JsonResponse({
        "message": "Patient registered successfully",
        "patient_id": patient.id
    })


# -------------------------
# Book Appointment
# -------------------------
@csrf_exempt
def book_appointment(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})

    patient_id = request.POST.get("patient_id")
    doctor_id = request.POST.get("doctor_id")
    date = request.POST.get("date")
    time = request.POST.get("time")

    if not patient_id or not doctor_id or not date or not time:
        return JsonResponse({"error": "All fields are required"})

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"})

    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return JsonResponse({"error": "Doctor not found"})

    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        date=date,
        time=time,
        status="pending"
    )

    return JsonResponse({
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id
    })


# -------------------------
# Add Prescription
# -------------------------
@csrf_exempt
def add_prescription(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})

    appointment_id = request.POST.get("appointment_id")
    medicines = request.POST.get("medicines")
    notes = request.POST.get("notes")

    if not appointment_id or not medicines:
        return JsonResponse({"error": "Required fields missing"})

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Appointment not found"})

    prescription = Prescription.objects.create(
        appointment=appointment,
        medicines=medicines,
        notes=notes
    )

    return JsonResponse({
        "message": "Prescription added successfully",
        "prescription_id": prescription.id
    })
def register_page(request):
    return render(request, "register_patient.html")

def appointment_page(request):
    return render(request, "book_appointment.html")