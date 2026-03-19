from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),

    path('register-patient-api/', register_patient, name='register_patient_api'),

    path('get-patient/<str:patient_id>/', get_patient, name='get_patient'),
    path('scan/', scan_page, name='scan_page'),

    path('add-prescription/', add_prescription, name='add_prescription'),
    path('view-prescriptions/', view_prescriptions, name='view_prescriptions'),
]