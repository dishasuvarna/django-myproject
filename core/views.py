from django.shortcuts import render
from .models import Patient, Doctor

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, "patients.html", {"patients": patients})

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, "doctors.html", {"doctors": doctors})