from django.urls import path
from .views import (
    register,
    login_view,
    logout_view,
    admin_dashboard,
    doctor_dashboard,
    patient_dashboard,
    register_patient
)

urlpatterns = [
    # -------------------------
    # AUTHENTICATION
    # -------------------------
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # -------------------------
    # DASHBOARDS
    # -------------------------
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),

    # -------------------------
    # QR API (PATIENT REGISTRATION)
    # -------------------------
    path('register-patient-api/', register_patient, name='register_patient_api'),
]