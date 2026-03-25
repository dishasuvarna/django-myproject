from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import re

from .models import Patient, Doctor, Profile, Prescription


# PASSWORD VALIDATION
# def is_strong_password(password):
#     return len(password) >= 6 and re.search(r"[a-z]", password) and re.search(r"[0-9]", password)


def is_strong_password(password):
    # Must be at least 8 characters
    if len(password) < 8:
        return False
    # No spaces allowed
    if " " in password:
        return False
    # Must contain at least one lowercase letter
    if not re.search(r"[a-z]", password):
        return False
    # Must contain at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return False
    # Must contain at least one digit
    if not re.search(r"[0-9]", password):
        return False
    # Must contain at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    
    return True


# -------------------------
# PATIENT REGISTER
# -------------------------
def register(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        phone = request.POST.get('phone')

        if not phone.isdigit() or len(phone) != 10:
            return render(request, 'register.html', {'error': 'Invalid phone'})

        if not is_strong_password(password):
            return render(request, 'register.html', {'error': 'Weak password'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'User exists'})

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, role='patient')

        return redirect('login')

    return render(request, 'register.html')


# -------------------------
# LOGIN
# -------------------------
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user is None:
            return render(request, 'login.html', {'error': 'Invalid login'})

        login(request, user)
        profile = Profile.objects.get(user=user)

        if profile.role == 'doctor':
            return redirect('doctor_dashboard')
        return redirect('patient_form')

    return render(request, 'login.html')


# -------------------------
# PATIENT FORM → QR ONLY
# -------------------------
# @login_required
# def patient_form(request):

#     patient = Patient.objects.filter(user=request.user).first()

#     if patient:
#         return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

#     if request.method == "POST":
#        phone = request.POST.get('phone')

#     if not phone or not phone.isdigit() or len(phone) != 10:
#             return render(request, 'patient_form.html', {'error': 'Invalid phone'})

#     patient = Patient.objects.create(
#             user=request.user,
#         patient_id=f"P{request.user.id}",
#             name=request.user.username,
#             age=request.POST.get('age') or 0,
#             gender=request.POST.get('gender') or "N/A",
#             phone=phone,
#             blood_group=request.POST.get('blood_group') or "",
#             allergies=request.POST.get('allergies') or "",
#             emergency_contact=request.POST.get('emergency_contact') or ""
#         )

#     return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

#     return render(request, 'patient_form.html')


# @login_required
# def scan_qr(request):
#     return render(request, 'scan.html')


@login_required
def patient_form(request):

    patient = Patient.objects.filter(user=request.user).first()

    # If patient already exists → show QR
    if patient:
        return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

    # Handle form submission
    if request.method == "POST":
        phone = request.POST.get('phone')

        # Validate phone
        if not phone or not phone.isdigit() or len(phone) != 10:
            return render(request, 'patient_form.html', {'error': 'Invalid phone'})

        # Create patient
        patient = Patient.objects.create(
            user=request.user,
            patient_id=f"P{request.user.id}",
            name=request.user.username,
            age=request.POST.get('age') or 0,
            gender=request.POST.get('gender') or "N/A",
            phone=phone,
            blood_group=request.POST.get('blood_group') or "",
            allergies=request.POST.get('allergies') or "",
            emergency_contact=request.POST.get('emergency_contact') or ""
        )

        return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

    # GET request → show form
    return render(request, 'patient_form.html')


@login_required
def scan_qr(request):
    return render(request, 'scan.html')



from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------------
# DOCTOR LOGIN (STRICT)
# -------------------------
def doctor_login(request):
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        print("LOGIN TRY:", username, password)  # DEBUG

        user = authenticate(request, username=username, password=password)

        if user is None:
            print("AUTH FAILED")
            return render(request, 'doctor_login.html', {'error': 'Invalid login'})

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return render(request, 'doctor_login.html', {'error': 'No profile found'})

        if profile.role != 'doctor':
            return render(request, 'doctor_login.html', {'error': 'Not a doctor'})

        login(request, user)

        print("LOGIN SUCCESS")

        return redirect('doctor_dashboard')

    return render(request, 'doctor_login.html')


# -------------------------
# DOCTOR DASHBOARD
# -------------------------
@login_required
def doctor_dashboard(request):

    profile = Profile.objects.get(user=request.user)

    # 🔒 STRICT CHECK
    if profile.role != 'doctor':
        return redirect('login')

    patient = None

    if request.method == "POST":
        search = request.POST.get('search')

        patient = Patient.objects.filter(
            patient_id=search
        ).first() or Patient.objects.filter(
         phone=search
        ).first()

    return render(request, 'doctor_dashboard.html', {
        'patient': patient
    })


# -------------------------
# ADD PRESCRIPTION
# -------------------------
@login_required
def add_prescription(request, patient_id):

    profile = Profile.objects.get(user=request.user)
    if profile.role != 'doctor':
        return redirect('login')

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
         return HttpResponse("Doctor profile not created")

    patient = Patient.objects.get(patient_id=patient_id)

    if request.method == "POST":
        Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            medicines=request.POST.get('medicines'),
            notes=request.POST.get('notes')
        )
        return redirect('doctor_dashboard')

    return render(request, 'add_prescription.html', {'patient': patient})

#View prescriptions for a patient


# @login_required
# def view_prescriptions(request, patient_id):

#     profile = Profile.objects.get(user=request.user)
#     if profile.role != 'doctor':
#         return redirect('login')

#     patient = Patient.objects.get(patient_id=patient_id)
#     prescriptions = Prescription.objects.filter(patient=patient)

#     return render(request, 'view_prescriptions.html', {
#         'patient': patient,
#         'prescriptions': prescriptions
#     })



@login_required
def my_prescriptions(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_form')

    prescriptions = Prescription.objects.filter(patient=patient)

    return render(request, 'patient_prescriptions.html', {
        'patient': patient,
        'prescriptions': prescriptions
    })




# view-prescriptions for doctor

@login_required
def view_prescriptions(request, patient_id):

    profile = Profile.objects.get(user=request.user)

    if profile.role != 'doctor':
        return redirect('login')

    patient = Patient.objects.get(patient_id=patient_id)
    prescriptions = Prescription.objects.filter(patient=patient)

    return render(request, 'view_prescriptions.html', {
        'patient': patient,
        'prescriptions': prescriptions
    })
# -------------------------
# QR FETCH (API)
# -------------------------
def get_patient(request, patient_id):

    patient = Patient.objects.get(patient_id=patient_id)

    return JsonResponse({
        "name": patient.name,
        "blood_group": patient.blood_group,
        "phone": patient.phone,
        "allergies": patient.allergies,
        "emergency_contact": patient.emergency_contact
    })