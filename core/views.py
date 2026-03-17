from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .models import Patient, Doctor, Appointment, Prescription


# -------------------------
# HTML Pages
# -------------------------

def register_page(request):
    return render(request, "register_patient.html")


def appointment_page(request):
    return render(request, "book_appointment.html")


# -------------------------
# Register Patient API
# -------------------------

@require_POST
def register_patient(request):
    name = request.POST.get("name")
    age = request.POST.get("age")
    gender = request.POST.get("gender")
    phone = request.POST.get("phone")

    # Validation
    if not all([name, age, gender, phone]):
        return JsonResponse({"error": "All fields are required"}, status=400)

    try:
        age = int(age)
    except ValueError:
        return JsonResponse({"error": "Age must be a number"}, status=400)

    # Create Patient
    patient = Patient.objects.create(
        name=name,
        age=age,
        gender=gender,
        phone=phone
    )

    return JsonResponse({
        "message": "Patient registered successfully",
        "patient_id": patient.id
    }, status=201)


# -------------------------
# Book Appointment API
# -------------------------

@require_POST
def book_appointment(request):
    patient_id = request.POST.get("patient_id")
    doctor_id = request.POST.get("doctor_id")
    date = request.POST.get("date")
    time = request.POST.get("time")

    # Validation
    if not all([patient_id, doctor_id, date, time]):
        return JsonResponse({"error": "All fields are required"}, status=400)

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)

    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return JsonResponse({"error": "Doctor not found"}, status=404)

    # Create Appointment
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
    }, status=201)


# -------------------------
# Add Prescription API
# -------------------------

@require_POST
def add_prescription(request):
    appointment_id = request.POST.get("appointment_id")
    medicines = request.POST.get("medicines")
    notes = request.POST.get("notes")

    # Validation
    if not appointment_id or not medicines:
        return JsonResponse({"error": "Required fields missing"}, status=400)

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Appointment not found"}, status=404)

    # Create Prescription
    prescription = Prescription.objects.create(
        appointment=appointment,
        medicines=medicines,
        notes=notes
    )

    return JsonResponse({
        "message": "Prescription added successfully",
        "prescription_id": prescription.id
    }, status=201)


# -------------------------
# Optional: Get All Patients
# -------------------------

def get_patients(request):
    patients = list(Patient.objects.values())
    return JsonResponse(patients, safe=False)


# -------------------------
# Optional: Get All Doctors
# -------------------------

def get_doctors(request):
    doctors = list(Doctor.objects.values())
    return JsonResponse(doctors, safe=False)


# -------------------------
# Optional: Get Appointments
# -------------------------

def get_appointments(request):
    appointments = list(Appointment.objects.values())
    return JsonResponse(appointments, safe=False)