from django.urls import path
from .views import scan_qr, save_location, emergency_alert, reverse_location

urlpatterns = [
      path('scan-qr/', scan_qr),
      path('save-location/', save_location),
      path('alert/<str:patient_id>/', emergency_alert),
      path('reverse-location/', reverse_location),
  ]