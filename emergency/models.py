from django.db import models
from core.models import Patient

class EmergencyAlert(models.Model):
    # Link each alert to a specific patient
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="emergency_alerts")
    
    # Automatically capture the exact date and time the alert was created
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Location data from your gated access system
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_address = models.CharField(max_length=255, null=True, blank=True)
    
    # The note left by the responder
    responder_note = models.TextField(null=True, blank=True)
    
    # A status flag to track if the emergency has been handled
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Emergency Alert for {self.patient.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"