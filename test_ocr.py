# test_ocr.py
from core.utils.image_OCR import _preprocess_image # Or your main OCR function
import pytesseract

# Provide a path to any test image on your computer
test_path = "path/to/your/test_image.png"

try:
    # Use the same logic your view will use
    text = pytesseract.image_to_string(test_path)
    print("--- OCR SUCCESSFUL ---")
    print(text)
except Exception as e:
    print(f"--- OCR FAILED ---")
    print(e)