from django.urls import path
from . import views

urlpatterns = [

    # Pages
    path("register/", views.register_page),
    path("appointment/", views.appointment_page),

    # APIs
    path("api/register-patient/", views.register_patient),
    path("api/book-appointment/", views.book_appointment),
    path("api/add-prescription/", views.add_prescription),
]