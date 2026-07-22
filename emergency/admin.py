from django.contrib import admin
from .models import EmergencyAlert

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view
    list_display = ('patient', 'timestamp', 'is_resolved', 'location_address', 'latitude', 'longitude')
    
    # Sidebar filter options
    list_filter = ('is_resolved', 'timestamp')
    
    # Search bar (allows searching by patient name, patient ID, address, or note)
    search_fields = ('patient__name', 'patient__patient_id', 'responder_note', 'location_address')
    
    # Order by newest alerts first
    ordering = ('-timestamp',)
    
    # Prevent manual modification of the auto-generated timestamp
    readonly_fields = ('timestamp',)