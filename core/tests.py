"""
Tests for core utility functions: PDF extraction, image OCR, and log
scrubbing. These are pure-function tests - they call existing utility
code and check results, without modifying any existing views, models,
or services.

Run with: python manage.py test core
"""

import os
import tempfile

from django.test import TestCase

from core.utils.pdf_processor import extract_text_from_pdf
from core.utils.image_OCR import extract_text_from_image
from core.utils.log_scrubber import scrub_for_log


class PDFExtractionTests(TestCase):
    """Tests for core/utils/pdf_processor.py"""

    def test_missing_file_returns_clean_error(self):
        result = extract_text_from_pdf("this_file_does_not_exist.pdf")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("not found", result["error"].lower())

    def test_non_pdf_extension_is_rejected(self):
        # Create a real temp file, but with a .txt extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"just some text")
            tmp_path = tmp.name

        try:
            result = extract_text_from_pdf(tmp_path)
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
        finally:
            os.remove(tmp_path)

    def test_corrupted_pdf_does_not_crash(self):
        # A file with a .pdf extension but garbage content
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"this is not a real pdf file")
            tmp_path = tmp.name

        try:
            result = extract_text_from_pdf(tmp_path)
            # Should fail gracefully, not raise an exception
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
        finally:
            os.remove(tmp_path)


class ImageOCRTests(TestCase):
    """Tests for core/utils/image_OCR.py"""

    def test_missing_file_returns_clean_error(self):
        result = extract_text_from_image("this_file_does_not_exist.jpg")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("not found", result["error"].lower())

    def test_unsupported_extension_is_rejected(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"not an image")
            tmp_path = tmp.name

        try:
            result = extract_text_from_image(tmp_path)
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
        finally:
            os.remove(tmp_path)

    def test_corrupted_image_does_not_crash(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(b"this is not a real jpg file")
            tmp_path = tmp.name

        try:
            result = extract_text_from_image(tmp_path)
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
        finally:
            os.remove(tmp_path)


class LogScrubberTests(TestCase):
    """Tests for core/utils/log_scrubber.py"""

    def test_phone_number_is_redacted(self):
        result = scrub_for_log("Call me at 9876543210 please")
        self.assertNotIn("9876543210", result)
        self.assertIn("[PHONE_REDACTED]", result)

    def test_email_is_redacted(self):
        result = scrub_for_log("Contact: john@example.com")
        self.assertNotIn("john@example.com", result)
        self.assertIn("[EMAIL_REDACTED]", result)

    def test_long_id_number_is_redacted(self):
        result = scrub_for_log("Patient ID 1234567")
        self.assertNotIn("1234567", result)
        self.assertIn("[ID_REDACTED]", result)

    def test_none_input_returns_none(self):
        result = scrub_for_log(None)
        self.assertIsNone(result)

    def test_plain_text_without_pii_is_unchanged(self):
        original = "Could not connect to Ollama. Is it running?"
        result = scrub_for_log(original)
        self.assertEqual(result, original)
