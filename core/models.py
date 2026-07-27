from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
    phone = models.CharField(max_length=10, blank=True, null=True)


    def __str__(self):
        return self.user.username



# otp
phone = models.CharField(max_length=10, unique=True)
otp = models.CharField(max_length=6, blank=True, null=True)
is_verified = models.BooleanField(default=False)

# -------------------------
# PATIENT
# -------------------------
#otp
emergency_contact = models.CharField(max_length=10)
emergency_otp = models.CharField(max_length=6, blank=True, null=True)
emergency_verified = models.BooleanField(default=False)



class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    patient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    blood_group = models.CharField(max_length=10)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15)
    alert_sent = models.BooleanField(default=False)

    is_pregnant = models.BooleanField(default=False)
    pregnancy_start_date = models.DateField(blank=True, null=True)

    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    #code_new
    patient_code = models.CharField(max_length=15, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        import os
        import json
        
        # site_url = "http://192.168.1.5:8000"
        site_url = os.environ.get('SITE_URL', 'http://192.168.1.5:8000')
        qr_string = f"{site_url}/scan/?patient_id={self.patient_id}"

        # Generate QR
        qr = qrcode.make(qr_string)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        file_name = f"{self.patient_id}.png"

        #  Assign QR image BEFORE saving
        self.qr_code.save(file_name, File(buffer), save=False)

        # Save everything once
        super().save(*args, **kwargs)

    @property
    def pregnancy_month(self):
        if not self.is_pregnant or not self.pregnancy_start_date:
            return None

        today = timezone.localdate()
        months = (today.year - self.pregnancy_start_date.year) * 12
        months += today.month - self.pregnancy_start_date.month

        if today.day < self.pregnancy_start_date.day:
            months -= 1

        return max(1, min(months + 1, 10))

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

    active_until = models.DateField(null=True, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def is_expired(self):
        if not self.active_until:
            return False
        from django.utils import timezone
        return timezone.localdate() > self.active_until

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name}"
    
    


# medical_report
class MedicalReport(models.Model):
      REPORT_TYPES = [
          ('xray', 'X-Ray'),
          ('blood_test', 'Blood Test'),
          ('scan', 'Scan'),
          ('other', 'Other'),
      ]

      EXTRACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('needs_ocr', 'Needs OCR (scanned PDF)'),
        ('low_confidence', 'Low Confidence'),
        ('no_text', 'No Text Detected'),
        ('unsupported', 'Unsupported File Type'),
        ('error', 'Extraction Error'),
    ]

      patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
      doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

      report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
      title = models.CharField(max_length=100)
      file = models.FileField(upload_to='medical_reports/')

      # --- NEW FIELDS ---
      extracted_text = models.TextField(blank=True, null=True)
      ai_summary = models.TextField(blank=True, null=True)
      extraction_status = models.CharField(
        max_length=20, choices=EXTRACTION_STATUS_CHOICES, default='pending'
    )
      ocr_confidence = models.FloatField(blank=True, null=True)
      # --- END NEW FIELDS ---

      uploaded_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      def get_extracted_text(self):
        from core.encryption_service import EncryptionService
        return EncryptionService.decrypt(self.extracted_text) if self.extracted_text else ''

      def get_ai_summary(self):
        from core.encryption_service import EncryptionService
        return EncryptionService.decrypt(self.ai_summary) if self.ai_summary else ''

      def __str__(self):
        return f"{self.patient.name} - {self.title}"

      def __str__(self):
          return f"{self.patient.name} - {self.title}"


class AuditLog(models.Model):
      ACTION_CHOICES = [
          ('create', 'Create'),
          ('update', 'Update'),
          ('delete', 'Delete'),
      ]

      doctor_id = models.CharField(max_length=20)
      action = models.CharField(max_length=10, choices=ACTION_CHOICES)
      record_id = models.CharField(max_length=50)
      timestamp = models.DateTimeField(auto_now_add=True)

      def __str__(self):
          return f"{self.doctor_id} - {self.action} - {self.record_id}"
