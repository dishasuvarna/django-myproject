from . import views
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),

    # 👤 Patient
    path('patient-form/', patient_form, name='patient_form'),
    path('my-prescriptions/', my_prescriptions, name='my_prescriptions'),
    path('logout/', logout_view, name='logout'),
    

    # 👨‍⚕️ Doctor
    path('doctor-login/', doctor_login, name='doctor_login'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),

    # 🔥 QR Scanner Page (IMPORTANT)
    path('scan/', scan_qr, name='scan_qr'),

    # 💊 Prescription
    path('add-prescription/<str:patient_id>/', add_prescription, name='add_prescription'),


    path('view-prescriptions/<str:patient_id>/', view_prescriptions, name='view_prescriptions'),

    # path('view-prescriptions/<str:patient_id>/', my_prescriptions, name='view_prescriptions'),

    path('my-prescriptions/', my_prescriptions, name='my_prescriptions'),


    # 📡 API
    path('get-patient/<str:patient_id>/', get_patient, name='get_patient'),


    #otp
    path('verify-register-otp/', views.verify_register_otp, name='verify_register_otp'),

    #otp_new
    path("send-otp/", views.send_otp, name="send_otp"),
]