from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json

from .models import Patient, Doctor, Profile, Prescription


# -------------------------
# REGISTER (Doctor / Patient)
# -------------------------
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'User already exists'})

        user = User.objects.create_user(username=username, password=password)

        # Create profile safely
        profile = Profile.objects.create(user=user, role=role)

        if role == "doctor":
            Doctor.objects.create(
                user=user,
                doctor_id=f"D{user.id}",
                name=username,
                specialization="General",
                phone="0000000000"
            )

        elif role == "patient":
            Patient.objects.create(
                user=user,
                patient_id=f"P{user.id}",
                name=username,
                age=20,
                gender="Not set",
                phone="0000000000",
                address="Not set",
                blood_group="NA",
                allergies="None",
                emergency_contact="0000000000"
            )

        return redirect('login')

    return render(request, 'register.html')


# -------------------------
# LOGIN
# -------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Safe profile access
            profile = Profile.objects.filter(user=user).first()

            if not profile:
                return redirect('login')

            role = profile.role

            if role == "admin":
                return redirect('admin_dashboard')
            elif role == "doctor":
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------------
# DASHBOARDS
# -------------------------
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
def doctor_dashboard(request):
    doctor = Doctor.objects.filter(user=request.user).first()
    if not doctor:
        return redirect('login')

    return render(request, 'doctor_dashboard.html', {'doctor': doctor})


@login_required
def patient_dashboard(request):
    patient = Patient.objects.filter(user=request.user).first()
    if not patient:
        return redirect('login')

    return render(request, 'patient_dashboard.html', {'patient': patient})


# -------------------------
# PATIENT REGISTRATION API (QR)
# -------------------------
@csrf_exempt
def register_patient(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            patient = Patient.objects.create(
                patient_id=data.get('patient_id'),
                name=data.get('name'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                address=data.get('address'),
                blood_group=data.get('blood_group'),
                allergies=data.get('allergies'),
                emergency_contact=data.get('emergency_contact')
            )

            return JsonResponse({
                "message": "Patient Registered Successfully",
                "qr_code": patient.qr_code.url
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Only POST method allowed"})


# -------------------------
# QR SCAN → GET PATIENT
# -------------------------
def get_patient(request, patient_id):
    patient = Patient.objects.filter(patient_id=patient_id).first()

    if not patient:
        return JsonResponse({"error": "Patient not found"})

    return JsonResponse({
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone,
        "blood_group": patient.blood_group,
        "allergies": patient.allergies,
        "address": patient.address
    })


# -------------------------
# SCAN PAGE
# -------------------------
@login_required
def scan_page(request):
    return render(request, 'scan.html')


# -------------------------
# ADD PRESCRIPTION
# -------------------------
@login_required
def add_prescription(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        medicines = request.POST.get('medicines')
        notes = request.POST.get('notes')

        patient = Patient.objects.filter(patient_id=patient_id).first()
        doctor = Doctor.objects.filter(user=request.user).first()

        if not patient or not doctor:
            return render(request, 'add_prescription.html', {'error': 'Invalid data'})

        Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            medicines=medicines,
            notes=notes
        )

        return redirect('doctor_dashboard')

    return render(request, 'add_prescription.html')


# -------------------------
# VIEW PRESCRIPTIONS
# -------------------------
@login_required
def view_prescriptions(request):
    patient = Patient.objects.filter(user=request.user).first()

    if not patient:
        return redirect('login')

    prescriptions = Prescription.objects.filter(patient=patient)

    return render(request, 'view_prescriptions.html', {'prescriptions': prescriptions})