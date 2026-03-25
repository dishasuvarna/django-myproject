from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
import json


# -------------------------
# PROFILE
# -------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10)  # 'patient' or 'doctor'

    def __str__(self):
        return self.user.username


# -------------------------
# PATIENT
# -------------------------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    patient_id = models.CharField(max_length=20)

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, unique=True)

    blood_group = models.CharField(max_length=5)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15)

    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        import json

        # 🔥 Prepare QR data BEFORE saving
        qr_data = {
            "id": self.patient_id,
            "name": self.name,
            "blood_group": self.blood_group,
            "allergies": self.allergies,
            "emergency_contact": self.emergency_contact
        }

        qr_string = json.dumps(qr_data)

        # 🔥 Generate QR
        qr = qrcode.make(qr_string)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        file_name = f"{self.patient_id}.png"

        # 🔥 Assign QR image BEFORE saving
        self.qr_code.save(file_name, File(buffer), save=False)

        # ✅ Save everything once
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# -------------------------
# DOCTOR
# -------------------------
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    doctor_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# -------------------------
# PRESCRIPTION
# -------------------------
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    medicines = models.TextField()
    notes = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name}"