from django.urls import path
from . import views

urlpatterns = [
    path('register-patient/', views.register_patient),
    path('book-appointment/', views.book_appointment),
    path('add-prescription/', views.add_prescription),
    path("register/", views.register_page),
    path("appointment/", views.appointment_page)
]