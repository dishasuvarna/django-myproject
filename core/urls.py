from . import views
from django.urls import include, path
from .views import *

urlpatterns = [

    # Patient
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('patient-form/', views.patient_form, name='patient_form'),
    path('my-prescriptions/', my_prescriptions, name='my_prescriptions'),
    path('qr-page/', views.qr_page, name='qr_page'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('logout/', logout_view, name='logout'),


    #otp
    path("send-otp/", views.send_otp, name="send_otp"),
    path('verify-register-otp/', views.verify_register_otp, name='verify_register_otp'),
    

    # Doctor
    path('doctor-login/', doctor_login, name='doctor_login'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('doctor/edit/<str:patient_id>/', views.doctor_edit_patient, name='doctor_edit_patient'),
    path('scan/', scan_qr, name='scan_qr'),

    # Prescription
    path('add-prescription/<str:patient_id>/', add_prescription, name='add_prescription'),
    path('edit-prescription/<int:prescription_id>/', edit_prescription, name='edit_prescription'),
    path('view-prescriptions/<str:patient_id>/', view_prescriptions, name='view_prescriptions'),

    # medical_report
    path('upload-report/<str:patient_id>/', upload_report, name='upload_report'),

    #  API
    path('get-patient/<str:patient_id>/', get_patient, name='get_patient'),

    path('doctor/logout/', doctor_logout_view, name='doctor_logout'),

    #drf_added
    path('emergency/', include('emergency.urls')), 
]
