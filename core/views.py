# otp_new

import profile

from twilio.rest import Client

account_sid = "TWILIO_ACCOUNT_SID"
auth_token = "TWILIO_AUTH_TOKEN"
twilio_number = "TWILIO_PHONE_NUMBER"


client = Client(account_sid, auth_token)


def send_otp(phone, otp):
    try:
        client.messages.create(
            body=f"Your OTP is {otp}",
            from_=twilio_number,
            to="+91" + phone
        )
        print("OTP sent successfully")
    except Exception as e:
        print("Error sending OTP:", e)


# # fast2sms
# import requests








from urllib import request

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import re

from .models import Patient, Doctor, Profile, Prescription





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

        action = request.POST.get('action')

        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        entered_otp = request.POST.get('otp')

        # ✅ common validations
        if not username or not password or not phone:
            return render(request, 'register.html', {'error': 'Fill all fields first'})

        if not phone.isdigit() or len(phone) != 10:
            return render(request, 'register.html', {'error': 'Invalid phone'})

        if not is_strong_password(password):
            return render(request, 'register.html', {'error': 'Weak password'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'User exists'})

        # 🔹 STEP 1: SEND OTP
        if action == "send_otp":

            otp = generate_otp()

            request.session['reg_data'] = {
                'username': username,
                'password': password,
                'phone': phone,
                'otp': otp
            }

            send_otp(phone, otp)
            print("REGISTER OTP:", otp)

            return render(request, 'register.html', {
                'otp_sent': True,
                'username': username,
                'phone': phone
            })

        # 🔹 STEP 2: VERIFY OTP + CREATE USER
        elif action == "verify_otp":

            data = request.session.get('reg_data')

            if not data:
                return render(request, 'register.html', {'error': 'Send OTP first'})

            if not entered_otp:
                return render(request, 'register.html', {
                    'error': 'Enter OTP',
                    'otp_sent': True
                })

            if str(entered_otp) == str(data['otp']):

                user = User.objects.create_user(
                    username=data['username'],
                    password=data['password']
                )

                profile = Profile.objects.create(user=user, role='patient')
                profile.phone = data['phone']
                profile.save()

                # #code_new
                # import random

                # patient = form.save(commit=False)
                # patient.patient_code = f"{patient.patient_id}-{random.randint(100000, 999999)}"
                # patient.save()
                # del request.session['reg_data']

                return redirect('login')

            return render(request, 'register.html', {
                'error': 'Invalid OTP',
                'otp_sent': True
            })

    return render(request, 'register.html')





import random

def generate_otp():
    return str(random.randint(100000, 999999))

#otp_new
def verify_register_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        data = request.session.get('reg_data')

        if not data:
            return redirect('register')

        if str(entered_otp) == str(data['otp']):

            user = User.objects.create_user(
                username=data['username'],
                password=data['password']
            )

            profile = Profile.objects.create(user=user, role='patient')
            profile.phone = data['phone']
            profile.save()

            del request.session['reg_data']

            return redirect('login')

        return render(request, 'verify_register_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_register_otp.html')

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

#     # If patient already exists → show QR
#     if patient:
#         return render(request, 'qr_page.html', {
#             'qr': patient.qr_code.url,
#             'patient': patient
# })

#     if request.method == "POST":
#         form_data = request.POST
#         # form_data = request.POST.dict()
#         phone = request.user.profile.phone
#         emergency_contact = request.POST.get('emergency_contact')


#         # ✅ ADD HERE
#         if not emergency_contact:
#             return render(request, 'patient_form.html', {
#                 'error': 'Enter emergency contact',
#                 'phone': phone,
#                 'form': form_data
#     })
#         entered_otp = request.POST.get('otp')



#         # # validations (same as yours)
#         # if not all(form_data.values()):
#         #     return render(request, 'patient_form.html', {
#         #         'error': 'Fill all fields first',
#         #         'phone': phone,
#         #         'form': form_data
#         #     })


#         # validations (exclude OTP)

        
#         required_fields = ['age', 'gender', 'blood_group', 'allergies', 'emergency_contact']

#         if not all(request.POST.get(field) for field in required_fields):
#             return render(request, 'patient_form.html', {
#                 'error': 'Fill all fields first',
#                 'phone': phone,
#                 'form': form_data
#     })

#         if not phone or not phone.isdigit() or len(phone) != 10:
#             return render(request, 'patient_form.html', {
#                 'error': 'Invalid phone',
#                 'phone': phone,
#                 'form': form_data
#             })

#         if phone == emergency_contact:
#             return render(request, 'patient_form.html', {
#                 'error': 'Phone and emergency contact cannot be same',
#                 'phone': phone,
#                 'form': form_data
#             })

#         session_otp = request.session.get('emergency_otp')

#        # emergency_new
#         print("SESSION OTP:", session_otp)

#         # 🔹 STEP 1: SEND OTP
#         if not session_otp:
#             otp = generate_otp()

#             # request.session['patient_data'] = dict(form_data)
#             request.session['patient_data'] = request.POST.dict()
#             request.session['emergency_otp'] = otp
# #

#             # print("EMERGENCY OTP:", otp)
# #             print("INSIDE FAST2SMS BLOCK")


# #             #fast2sms
# #            

# #             payload = {
# #             "route": "q",
# #             "message": f"Your OTP is {otp}",
# #             "language": "english",
# #             "flash": 0,
# #             "numbers": emergency_contact.strip()
# # }

# #             headers = {
# #     # "authorization": "YOUR_API_KEY_HERE",
# #             "authorization": "api_key_goes_here",
# #             "Content-Type": "application/json"
# # }

# #             response = requests.post(url, json=payload, headers=headers)

# #             print("FAST2SMS RESPONSE:", response.text)






#             # emergency_otp
#             message = client.messages.create(
#     body=f"Your OTP is {otp}",
#     from_='twilio_number',  # Twilio number
#     to=f'+91{emergency_contact}'# MUST include +91



# #     # to=emergency_contact if emergency_contact.startswith('+91') else f'+91{emergency_contact}'
# #     # clean_number = emergency_contact.strip()

# # # to = clean_number if clean_number.startswith('+91') else f'+91{clean_number}'

# # #emergency_otp
# # # clean_number = emergency_contact.strip()
# # # to_number = clean_number if clean_number.startswith('+91') else f'+91{clean_number}'

# # # message = client.messages.create(
# # #     body=f"Your OTP is {otp}",
# # #     from_='+1XXXXXXXXXX',
# # #     to=to_number
# # # )
#              )
            
#             print("OTP SENT TO:", emergency_contact)
#             print("SID:", message.sid)
#             print("STATUS:", message.status)

#             return render(request, 'patient_form.html', {
#                 'phone': phone,
#                 'form': form_data,
#                 'otp_sent': True
#             })


            

#         # 🔹 STEP 2: VERIFY OTP
#         else:
#             if not entered_otp:
#                 return render(request, 'patient_form.html', {
#                     'error': 'Enter OTP',
#                     'phone': phone,
#                     'form': form_data,
#                     'otp_sent': True
#                 })

#             if str(entered_otp) == str(session_otp):

#                 data = request.session.get('patient_data')

#                 # ✅ ADD THIS LINE HERE
#                 print("AGE RAW:", data.get('age'), type(data.get('age')))

#                 patient = Patient.objects.create(
#                     user=request.user,
#                     patient_id=f"P{request.user.id}",
#                     name=request.user.username,
#                     # age=data.get('age')or 0,

#                     # age = int(data.get('age') or 0),

#                     # FIX: handle list or string
#                     age = int(data.get('age')[0] if isinstance(data.get('age'), list) else data.get('age') or 0),
#                     gender=data.get('gender') or "N/A",
#                     phone=phone,
#                     blood_group=data.get('blood_group') or "",
#                     allergies=data.get('allergies') or "",
#                     emergency_contact=data.get('emergency_contact') or ""
#                 )

#                 #otp_new
#                 import random
#                 patient.patient_code = f"{patient.patient_id}-{random.randint(100000, 999999)}"
#                 patient.save()
#                 print("CODE GENERATED:", patient.patient_code)  # 👈 DEBUG

#                 # clear session
#                 del request.session['emergency_otp']
#                 del request.session['patient_data']

#                 return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

#             return render(request, 'patient_form.html', {
#                 'error': 'Invalid OTP',
#                 'phone': phone,
#                 'form': form_data,
#                 'otp_sent': True
#             })

#     # GET request
#     return render(request, 'patient_form.html', {
#         'phone': request.user.profile.phone
#     })
        
        
        

# # @login_required
# # def patient_form(request):

# #     patient = Patient.objects.filter(user=request.user).first()

# #     # If patient already exists → show QR
# #     if patient:
# #         return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

# #     if request.method == "POST":
# #         form_data = request.POST
# #         phone = request.user.profile.phone
# #         emergency_contact = request.POST.get('emergency_contact')
# #         entered_otp = request.POST.get('otp')

# #         # validations (same as yours)
# #         if not all(form_data.values()):
# #             return render(request, 'patient_form.html', {
# #                 'error': 'Fill all fields first',
# #                 'phone': phone,
# #                 'form': form_data
# #             })

# #         if not phone or not phone.isdigit() or len(phone) != 10:
# #             return render(request, 'patient_form.html', {
# #                 'error': 'Invalid phone',
# #                 'phone': phone,
# #                 'form': form_data
# #             })

# #         if phone == emergency_contact:
# #             return render(request, 'patient_form.html', {
# #                 'error': 'Phone and emergency contact cannot be same',
# #                 'phone': phone,
# #                 'form': form_data
# #             })

# #         session_otp = request.session.get('emergency_otp')

# #         # 🔹 STEP 1: SEND OTP
# #         if not session_otp:
# #             otp = generate_otp()

# #             request.session['patient_data'] = dict(form_data)
# #             request.session['emergency_otp'] = otp

# #             print("EMERGENCY OTP:", otp)

# #             return render(request, 'patient_form.html', {
# #                 'phone': phone,
# #                 'form': form_data,
# #                 'otp_sent': True
# #             })

# #         # 🔹 STEP 2: VERIFY OTP
# #         else:
# #             if not entered_otp:
# #                 return render(request, 'patient_form.html', {
# #                     'error': 'Enter OTP',
# #                     'phone': phone,
# #                     'form': form_data,
# #                     'otp_sent': True
# #                 })

# #             if str(entered_otp) == str(session_otp):

# #                 data = request.session.get('patient_data')

# #                 patient = Patient.objects.create(
# #                     user=request.user,
# #                     patient_id=f"P{request.user.id}",
# #                     name=request.user.username,
# #                     age=data.get('age') or 0,
# #                     gender=data.get('gender') or "N/A",
# #                     phone=phone,
# #                     blood_group=data.get('blood_group') or "",
# #                     allergies=data.get('allergies') or "",
# #                     emergency_contact=data.get('emergency_contact') or ""
# #                 )

# #                 # clear session
# #                 del request.session['emergency_otp']
# #                 del request.session['patient_data']

# #                 return render(request, 'qr_page.html', {'qr': patient.qr_code.url})

# #             return render(request, 'patient_form.html', {
# #                 'error': 'Invalid OTP',
# #                 'phone': phone,
# #                 'form': form_data,
# #                 'otp_sent': True
# #             })

# #     # GET request
# #     return render(request, 'patient_form.html', {
# #         'phone': request.user.profile.phone
# #     })






# @login_required
# def scan_qr(request):
#     return render(request, 'scan.html')



# from django.contrib.auth import logout
# from django.shortcuts import redirect

# def logout_view(request):
#     logout(request)
#     return redirect('login')
















@login_required
def patient_form(request):
    profile = request.user.profile

    # ❌ Block doctor access
    if profile.role == 'doctor':
        return redirect('doctor_dashboard')

    patient = Patient.objects.filter(user=request.user).first()

    # if not patient:
    #     return redirect('patient_form')  # new for doctor 
    
    if patient:
        return redirect('qr_page')   # new for doctor 

    # ✅ If patient already exists → always show QR
    # if patient:
    #     return render(request, 'qr_page.html', {
    #         'qr': patient.qr_code.url,
    #         'patient': patient
    #     })

    if request.method == "POST":
        form_data = request.POST
        phone = request.user.profile.phone
        emergency_contact = request.POST.get('emergency_contact')
        entered_otp = request.POST.get('otp')

        # ✅ Validate emergency contact
        if not emergency_contact:
            return render(request, 'patient_form.html', {
                'error': 'Enter emergency contact',
                'phone': phone,
                'form': form_data
            })

        # ✅ Required fields validation
        required_fields = ['age', 'gender', 'blood_group', 'allergies', 'emergency_contact']
        if not all(request.POST.get(field) for field in required_fields):
            return render(request, 'patient_form.html', {
                'error': 'Fill all fields first',
                'phone': phone,
                'form': form_data
            })

        # ✅ Phone validation
        if not phone or not phone.isdigit() or len(phone) != 10:
            return render(request, 'patient_form.html', {
                'error': 'Invalid phone',
                'phone': phone,
                'form': form_data
            })

        if phone == emergency_contact:
            return render(request, 'patient_form.html', {
                'error': 'Phone and emergency contact cannot be same',
                'phone': phone,
                'form': form_data
            })

        session_otp = request.session.get('emergency_otp')

        # 🔹 STEP 1: SEND OTP
        if not session_otp:
            otp = generate_otp()

            request.session['patient_data'] = request.POST.dict()
            request.session['emergency_otp'] = otp

            message = client.messages.create(
                body=f"Your OTP is {otp}",
                from_='',
                to=f'+91{emergency_contact}'
            )

            print("OTP SENT TO:", emergency_contact)

            return render(request, 'patient_form.html', {
                'phone': phone,
                'form': form_data,
                'otp_sent': True
            })

        # 🔹 STEP 2: VERIFY OTP
        else:
            if not entered_otp:
                return render(request, 'patient_form.html', {
                    'error': 'Enter OTP',
                    'phone': phone,
                    'form': form_data,
                    'otp_sent': True
                })

            if str(entered_otp) == str(session_otp):

                data = request.session.get('patient_data')

                try:
                    age_value = int(data.get('age')) if data.get('age') else 0
                except:
                    age_value = 0

                # ✅ CREATE PATIENT (SAFE)
                patient = Patient.objects.create(
                    user=request.user,
                    patient_id=f"P{request.user.id}",
                    name=request.user.username,
                    age=age_value,
                    gender=data.get('gender') or "N/A",
                    phone=phone,
                    blood_group=data.get('blood_group') or "",
                    allergies=data.get('allergies') or "",
                    emergency_contact=data.get('emergency_contact') or ""
                )

                # ✅ Generate patient code
                import random
                patient.patient_code = f"{patient.patient_id}-{random.randint(100000, 999999)}"
                patient.save()

                print("✅ PATIENT CREATED:", patient)

                # ✅ Clear session safely
                request.session.pop('emergency_otp', None)
                request.session.pop('patient_data', None)

                # ✅ IMPORTANT FIX: redirect instead of render
                return redirect('patient_form')

            return render(request, 'patient_form.html', {
                'error': 'Invalid OTP',
                'phone': phone,
                'form': form_data,
                'otp_sent': True
            })

    # GET request → show form only if no patient
    return render(request, 'patient_form.html', {
        'phone': request.user.profile.phone
    })




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

    #enuser only doctor access
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'doctor':
          return redirect('login')

    # search = request.GET.get('search')
    search = request.GET.get('search', '')
    patient = None

    if search:
        search = search.strip()

        # 🔥 CASE 1
        if "-" in search:
            patient_code = search.split("-")[0]   # P1
        else:
            patient_code = search

        print("🔍 Extracted patient_id:", patient_code)

        patient = Patient.objects.filter(patient_id=patient_code).first()

    # return render(request, 'doctor_dashboard.html', {
    #     'patient': patient
    # })
    return render(request, 'doctor_dashboard.html', {
      'patient': patient,
      'search': search
  })




# -------------------------
# DOCTOR EDIT PATIENT
# -------------------------
@login_required
def doctor_edit_patient(request, patient_id):

    # 🔒 Ensure only doctor
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'doctor':
        return redirect('doctor_login')

    patient = Patient.objects.filter(patient_id=patient_id).first()
    # ✅ ADD DEBUG HERE (INSIDE FUNCTION)
    # print("PATIENT OBJECT:", patient)
    # if patient:
    #     print("PATIENT DATA:", patient.__dict__)

    

    if not patient:
        return redirect('doctor_dashboard')

    if request.method == "POST":

        # ✅ UPDATE ONLY ALLOWED FIELDS
        patient.age = request.POST.get('age') or patient.age
        patient.gender = request.POST.get('gender') or patient.gender
        patient.blood_group = request.POST.get('blood_group') or patient.blood_group
        patient.allergies = request.POST.get('allergies') or patient.allergies
        patient.emergency_contact = request.POST.get('emergency_contact') or patient.emergency_contact

        # ❗ DO NOT TOUCH PHONE
        # patient.phone = ❌ NEVER CHANGE

        patient.save()

        return redirect('doctor_dashboard')

    return render(request, 'doctor_edit.html', {
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
    

    #add prescriptions error
    # try:
    #     patient = Patient.objects.get(id=patient_id)   # ✅ FIXED
    # except Patient.DoesNotExist:
    #     return HttpResponse("Patient not found")

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
    
    #view-prescriptions error
    # try:
    #     patient = Patient.objects.get(id=patient_id)   # ✅ FIXED
    # except Patient.DoesNotExist:
    #     return HttpResponse("Patient not found")

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



# -------------------------
# QR VIEW 
# -------------------------

@login_required
def qr_page(request):
    patient = Patient.objects.filter(user=request.user).first()

    if not patient:
        return redirect('patient_form')  # safety

    return render(request, 'qr_page.html', {
        'qr': patient.qr_code.url,
        'patient': patient
    })