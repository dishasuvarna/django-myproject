from django.urls import path
from .views import scan_qr,save_location
#from .views import scan_qr_page

urlpatterns = [
    path('scan-qr/', scan_qr),
    path('save-location/', save_location),
    #path('scan-qr/', scan_qr_page),
]