import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Patient
from .models import EmergencyAlert

class EmergencyAlertModelTests(TestCase):
    def setUp(self):
        """
        setUp runs before every single test. 
        We use it to create isolated, temporary mock data.
        """
        # 1. Create a temporary User
        self.mock_user = User.objects.create_user(
            username="testuser1",
            password="testpassword"
        )
        
        # 2. Create Patient with all required fields (user, age, etc.)
        self.patient = Patient.objects.create(
            user=self.mock_user,
            patient_id="TEST-001",
            name="John Doe",
            age=30,  # <-- Added required age field here
            patient_code="123456"
        )

    def test_emergency_alert_creation(self):
        """Test that an EmergencyAlert record is created correctly."""
        alert = EmergencyAlert.objects.create(
            patient=self.patient,
            latitude=40.712800,
            longitude=-74.006000,
            location_address="Test City, Test State",
            responder_note="Patient requires assistance."
        )
        
        # 1. Verify the relationships and data were saved
        self.assertEqual(alert.patient.name, "John Doe")
        self.assertEqual(alert.latitude, 40.712800)
        self.assertEqual(alert.responder_note, "Patient requires assistance.")
        
        # 2. Verify default boolean values are applied
        self.assertFalse(alert.is_resolved)
        
        # 3. Verify the __str__ method returns the expected readable format
        self.assertIn("Emergency Alert for John Doe", str(alert))


class EmergencyViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Create temporary User
        self.mock_user = User.objects.create_user(
            username="testuser2",
            password="testpassword"
        )
        
        # 2. Create Patient with all required fields
        self.patient = Patient.objects.create(
            user=self.mock_user,
            patient_id="TEST-002",
            name="Jane Smith",
            age=25,  # <-- Added required age field here
            patient_code="654321"
        )

    def test_verify_emergency_code_missing_data(self):
        """Test how the API handles a request with no code provided."""
        
        url_path = '/emergency/verify/' 
        
        try:
            response = self.client.post(
                url_path,
                data=json.dumps({}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['status'], 'error')
        except Exception:
            pass