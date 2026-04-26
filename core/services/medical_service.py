from dataclasses import asdict, dataclass

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core.models import AuditLog, Doctor, MedicalReport, Patient, Prescription



@dataclass(frozen=True)
class MedicalRecord:
    patient_id: str
    doctor_id: str
    type: str
    title: str
    description: str
    file_url: str | None
    created_at: object
    updated_at: object

    def to_dict(self):
        return asdict(self)


class MedicalService:
    """Central service layer for medical records, prescriptions, and reports."""

    @staticmethod
    def addPrescription(data):
        patient = _resolve_patient(data)
        doctor = _resolve_doctor(data)
        medicines = _required_text(data, "medicines")
        notes = _required_text(data, "notes")

        prescription = Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            medicines=medicines,
            notes=notes,
        )
        _log_audit_action(doctor, "create", prescription.id)


        return prescription

    @staticmethod
    def uploadReport(data):
        patient = _resolve_patient(data)
        doctor = _resolve_doctor(data)
        report_type = _required_value(data, "report_type")
        title = _required_value(data, "title")
        report_file = _required_value(data, "file")

        report = MedicalReport.objects.create(
            patient=patient,
            doctor=doctor,
            report_type=report_type,
            title=title,
            file=report_file,
        )
        _log_audit_action(doctor, "create", report.id)

        return report

    @staticmethod
    def getPatientRecords(patientId):
        patient = Patient.objects.get(patient_id=patientId)
        prescriptions = (
            Prescription.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-created_at")
        )
        reports = (
            MedicalReport.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-uploaded_at")
        )
        medical_records = _merge_medical_records(prescriptions, reports)

        return {
            "patient": patient,
            "prescriptions": prescriptions,
            "reports": reports,
            "medical_records": medical_records,
        }

    @staticmethod
    def updateMedicalRecord(data):
        record_type = _required_value(data, "type")

        if record_type == "prescription":
            return MedicalService.updatePrescription(data)

        if record_type == "report":
            return MedicalService.updateReport(data)

        raise ValidationError("type must be prescription or report")

    @staticmethod
    def updatePrescription(data):
        doctor = _resolve_doctor(data)
        prescription = Prescription.objects.select_related("patient", "doctor").get(
            id=_required_value(data, "record_id")
        )

        if not _doctor_owns_record(doctor, prescription):
            return _read_only_response(_prescription_to_medical_record(prescription))

        prescription.medicines = _required_text(data, "medicines")
        prescription.notes = _required_text(data, "notes")
        prescription.save()
        _log_audit_action(doctor, "update", prescription.id)

        return {
            "allowed": True,
            "read_only": False,
            "record": _prescription_to_medical_record(prescription),
        }

    @staticmethod
    def updateReport(data):
        doctor = _resolve_doctor(data)
        report = MedicalReport.objects.select_related("patient", "doctor").get(
            id=_required_value(data, "record_id")
        )

        if not _doctor_owns_record(doctor, report):
            return _read_only_response(_report_to_medical_record(report))

        report.report_type = _required_value(data, "report_type")
        report.title = _required_value(data, "title")

        if data.get("file"):
            report.file = data["file"]

        report.save()
        _log_audit_action(doctor, "update", report.id)

        return {
            "allowed": True,
            "read_only": False,
            "record": _report_to_medical_record(report),
        }

    @staticmethod
    def canEditMedicalRecord(data):
        doctor = _resolve_doctor(data)
        record = _resolve_medical_record(data)
        return _doctor_owns_record(doctor, record)


def addPrescription(data):
    return MedicalService.addPrescription(data)


def uploadReport(data):
    return MedicalService.uploadReport(data)


def getPatientRecords(patientId):
    return MedicalService.getPatientRecords(patientId)


def updateMedicalRecord(data):
    return MedicalService.updateMedicalRecord(data)


def updatePrescription(data):
    return MedicalService.updatePrescription(data)


def updateReport(data):
    return MedicalService.updateReport(data)


def canEditMedicalRecord(data):
    return MedicalService.canEditMedicalRecord(data)


def _resolve_patient(data):
    patient = data.get("patient")
    if patient is not None:
        return patient

    patient_id = data.get("patient_id") or data.get("patientId")
    if not patient_id:
        raise ValidationError("patient_id is required")

    return Patient.objects.get(patient_id=patient_id)


def _resolve_doctor(data):
    doctor = data.get("doctor")
    if doctor is not None:
        return doctor

    user = data.get("user") or data.get("doctor_user") or data.get("doctorUser")
    if user is not None:
        return Doctor.objects.get(user=user)

    doctor_id = data.get("doctor_id") or data.get("doctorId")
    if doctor_id:
        return Doctor.objects.get(doctor_id=doctor_id)

    raise ObjectDoesNotExist("Doctor could not be resolved")


def _required_text(data, key):
    value = _required_value(data, key)
    value = value.strip() if isinstance(value, str) else value
    if not value:
        raise ValidationError(f"{key} is required")
    return value


def _required_value(data, key):
    value = data.get(key)
    if not value:
        raise ValidationError(f"{key} is required")
    return value


def _merge_medical_records(prescriptions, reports):
    records = [
        *[_prescription_to_medical_record(prescription) for prescription in prescriptions],
        *[_report_to_medical_record(report) for report in reports],
    ]
    return sorted(records, key=lambda record: record.created_at, reverse=True)


def _prescription_to_medical_record(prescription):
    return MedicalRecord(
        patient_id=prescription.patient.patient_id,
        doctor_id=prescription.doctor.doctor_id,
        type="prescription",
        title="Prescription",
        description=(
            f"Medicines: {prescription.medicines}\n"
            f"Notes: {prescription.notes}"
        ),
        file_url=None,
        created_at=_record_created_at(prescription),
        updated_at=_record_updated_at(prescription),
    )


def _report_to_medical_record(report):
    return MedicalRecord(
        patient_id=report.patient.patient_id,
        doctor_id=report.doctor.doctor_id,
        type="report",
        title=report.title,
        description=report.get_report_type_display(),
        file_url=_report_file_url(report),
        created_at=_record_created_at(report),
        updated_at=_record_updated_at(report),
    )


def _report_file_url(report):
    if not report.file:
        return None

    try:
        return report.file.url
    except ValueError:
        return None


def _resolve_medical_record(data):
    record_type = _required_value(data, "type")
    record_id = _required_value(data, "record_id")

    if record_type == "prescription":
        return Prescription.objects.select_related("patient", "doctor").get(id=record_id)

    if record_type == "report":
        return MedicalReport.objects.select_related("patient", "doctor").get(id=record_id)

    raise ValidationError("type must be prescription or report")


def _doctor_owns_record(doctor, record):
    return record.doctor_id == doctor.id and record.doctor.doctor_id == doctor.doctor_id


def _read_only_response(record):
    return {
        "allowed": False,
        "read_only": True,
        "message": "Only the doctor who created this record can edit it.",
        "record": record,
    }


def _record_created_at(record):
    return getattr(record, "created_at", None) or getattr(record, "uploaded_at", None)


def _record_updated_at(record):
    return (
        getattr(record, "updated_at", None)
        or getattr(record, "modified_at", None)
        or _record_created_at(record)
    )


def _log_audit_action(doctor, action, record_id):
    try:
        AuditLog.objects.create(
            doctor_id=doctor.doctor_id,
            action=action,
            record_id=str(record_id),
        )
    except Exception:
        pass
