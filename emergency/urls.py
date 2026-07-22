from django import views
from django.urls import path
from . import views
from .views import scan_qr, save_location, emergency_alert, reverse_location, verify_emergency_code

urlpatterns = [
      path('scan-qr/', scan_qr),
      path('save-location/', save_location),
      path('alert/<str:patient_id>/', emergency_alert),
      path('reverse-location/', reverse_location),
      path('verify/', views.verify_emergency_code_page, name='verify_page'),
      path('verify-code/', views.verify_emergency_code, name='verify_emergency_code'),
  ]