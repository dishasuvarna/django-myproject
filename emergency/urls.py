from django.urls import path
from .views import scan_qr, save_location, emergency_alert, reverse_location

urlpatterns = [
      path('scan-qr/', scan_qr),
      path('save-location/', save_location),
      path('alert/<str:patient_id>/', emergency_alert),
      path('reverse-location/', reverse_location),
  ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('scan-qr/', views.scan_qr, name='scan_qr'),
#     path('alert/<str:patient_id>/', views.emergency_alert, name='emergency_alert'),
#     path('save-location/', views.save_location, name='save_location'),
#     path('reverse-location/', views.reverse_location, name='reverse_location'),
#     path('scan/', views.scan_qr_page, name='scan_qr_page'),
# ]