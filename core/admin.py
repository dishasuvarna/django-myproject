from django.contrib import admin
from .models import Patient, Doctor, Prescription,Profile,MedicalReport


admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Prescription)
admin.site.register(Profile)
admin.site.register(MedicalReport)