# Smart Emergency Medical QR System

## Overview

The **Smart Emergency Medical QR System** is a secure web-based application designed to provide **instant access to critical patient information during emergencies**.

This system allows patients to register once and generate a **QR code containing essential medical details**, which can be accessed by authorized doctors for **quick and efficient treatment**.

---

## Problem Statement

In emergency situations, valuable time is lost in:

* Identifying the patient
* Checking medical history
* Knowing allergies or blood group

This system solves that by providing **instant, secure access** to patient data using QR codes.

---

## Features

### Patient Module

* Secure registration with validation
* Strong password enforcement
* One-time data entry (no modification allowed)
* QR code generation after form submission
* Offline access to basic details:

  * Name
  * Blood Group
  * Allergies
  * Emergency Contact

---

### Doctor Module

* **Strict login (authorized users only)**
* Access restricted using `is_doctor` verification
* Search patient instantly using:

  * Patient ID
    
* View patient details
* Add prescriptions
* Fast access for emergency scenarios

---

### QR Code System

* Contains essential medical information
* Works in:

  * **Offline mode** → basic details
  * **Online mode** → full patient data
* Enables quick scanning and treatment decisions

---

## Security Features

* Strong password validation
* Duplicate prevention (username & phone)
* One-time patient data submission
* Role-based access using `is_doctor`
* Unauthorized users cannot access doctor dashboard

---

## Tech Stack

* **Backend:** Django (Python)
* **Database:** MySQL / SQLite
* **Frontend:** HTML, CSS (Basic UI)
* **QR Generation:** `qrcode` Python library

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

1. Register account
2. Login
3. Fill medical form (only once)
4. QR code generated
5. Use QR in emergencies

---

### Doctor Flow

1. Login with authorized account
2. Search patient using ID / Phone / Aadhaar
3. View details
4. Add prescription

---

## Real-World Impact

* Saves time in emergencies
* Improves treatment accuracy
* Reduces medical errors
* Enables faster decision-making

---

## Author

**Disha G**
Computer Science Engineering Student

---

## Conclusion

This project demonstrates a **real-world healthcare solution** that combines:

* Security
* Speed
* Practical usability

making it highly relevant for **modern emergency systems**.

---
