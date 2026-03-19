from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json

from .models import Patient, Doctor, Profile


# -------------------------
# REGISTER (Doctor / Patient)
# -------------------------
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        # Create user
        user = User.objects.create_user(username=username, password=password)

        # Create profile
        Profile.objects.create(user=user, role=role)

        # Create role-specific data
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
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            role = user.profile.role

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
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    return render(request, 'doctor_dashboard.html', {'doctor': doctor})


def patient_dashboard(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'patient_dashboard.html', {'patient': patient})


# -------------------------
# PATIENT REGISTRATION API (QR)
# -------------------------
@csrf_exempt
def register_patient(request):
    if request.method == "POST":
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