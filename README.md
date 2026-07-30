# VitalScan – Smart Emergency Medical Access System

## Overview

The **Smart Emergency Medical QR System** is a secure web-based application designed to provide **instant access to critical patient information during emergencies**.

This system allows patients to register once and generate a **QR code containing essential medical details**, which can be accessed by authorized doctors for **quick and efficient treatment**.

Accessible by any rescuer, bystander, or first responder scanning the physical QR code or by the patient code during an emergency, who can view only the basic patient details (such as name, blood group, allergies, and emergency contacts) to ensure privacy while providing immediate assistance.

---

## Problem Statement

In emergency situations, valuable time is lost in:

* Identifying the patient
* Checking medical history
* Knowing allergies or blood group

This system solves that by providing **instant, secure access** to patient data using dynamic QR codes backed by local AI processing and automated messaging.

---

## Features

### Patient Module

* Secure registration with phone number verification via Twilio OTP
* Strong password enforcement
* One-time data entry (secured against unauthorized modification)
* Dynamic QR code generation after form submission using the Python qrcode library
* Access to patient basic details:

  * Name
  * Blood Group
  * Allergies
  * Emergency Contact

---

### Doctor Module

* **Strict login (authorized users only)**
* Access restricted using `is_doctor` verification
* Search patient instantly using:

  * Patient ID/Code
    
* View patient details
* Comprehensive profile and record management (view details, upload reports, and edit patient forms with administrative/doctor approval)
* Edit patient(Patient form deatails can be edited with the doctor approval)
* Fast access tailored for high-pressure emergency scenarios

---

### QR Code System

* Contains essential medical information
* Encodes a dynamic URL that redirects scanners to the secure emergency alert page.
* Enables quick scanning via JavaScript geolocation triggers to instantly capture location coordinates.
* Allows optional voice or text recording to explain the patient's current situation.
* Restricts basic detail viewing and automated SMS alerts to designated contacts until explicitly triggered by the user.

---

## Security Features

* Twilio Integration: Automated, secure OTP verification during registration and automated emergency SMS alerts dispatched to designated contacts (supporting multiple phone numbers).
* Multi-Layer Security: Multi-factor authentication, secure location-based verification, JWT nonce safety, and AES-256 encrypted data protection.
* Integrity Controls: Strict duplicate prevention for usernames and phone numbers, alongside one-time patient data submission locks.
* Access Control: Role-based access using is_doctor flags ensuring unauthorized users cannot access clinical dashboards.

---

## Tech Stack

* **Backend:** Django, Django REST Framework (DRF)
* **Database:** MySQL 
* **Frontend:** HTML, CSS, JavaScript
* Communication Service: Twilio API (for OTP and automated emergency SMS)
* AI & Document Processing Libraries:

qrcode (Python library for dynamic QR generation)

PyTesseract & OpenCV (for OCR text extraction from medical documents)

Ollama (for local LLM clinical data parsing and structuring)

---

## Installation & Setup

```bash
# Clone repository
git clone <https://github.com/dishasuvarna/django-myproject>

# Navigate to project
cd myproject

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

---

## How to Use

### Patient Flow

1. Register account with phone validation (Twilio OTP sent to verify the number)
2. Login securely
3. Fill medical form (locked to one-time submission to preserve data accuracy)
4. Dynamic QR code automatically generated along with the unique patient code
5. Use QR code in emergencies

---

### Doctor Flow

1. Login with authorized account
2. Search patient using ID / Code 
3. View details
4. Comprehensive prescription management (add, edit, update, and manage multiple medical records and active/archived statuses)
5. Advanced AI-driven prescription workflow:

OCR Text Extraction (PyTesseract & OpenCV): Seamlessly processes uploaded medical documents and prescription images to extract raw text data with high accuracy.

Ollama Integration: Utilizes local large language models via Ollama to intelligently parse, structure, and interpret clinical text.

Automated Processing & High Precision: Combines robust image processing with local AI to minimize manual data entry errors, structure medical data reliably, and streamline clinical decision-making.

6.Trigger automated emergency SMS alerts to designated contacts (reaching multiple phone numbers safely) when required.

---

## Real-World Impact

* Saves critical time during emergency responses
* Improves treatment accuracy through structured AI data parsing
* Reduces medical errors via automated OCR and local LLM verification
* Enables faster clinical decision-making
* Ensures robust security, privacy, and accountability through Twilio verification, location-based checks, and encrypted data protection

---

## Author

**Disha G**
Computer Science Engineering Student

---

## Conclusion

This project demonstrates a **real-world healthcare solution** that combines:

* Cutting-edge local AI processing (Ollama & PyTesseract)
* Reliable communication infrastructure (Twilio OTP & SMS)
* Exceptional security, speed, and practical usability

making it highly relevant for **modern, secure emergency medical ecosystems.**.

---
