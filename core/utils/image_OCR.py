import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, UnidentifiedImageError


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")

# Below this average Tesseract word-confidence, we flag the result as low-confidence
LOW_CONFIDENCE_THRESHOLD = 50


def _preprocess_image(image_path):
    """
    Loads an image and applies basic preprocessing to improve OCR accuracy:
    - Convert to grayscale
    - Apply thresholding to boost contrast
    - Deskew (correct rotation/tilt) if possible

    Returns a preprocessed OpenCV image (numpy array), or None if unreadable.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Otsu's thresholding handles poor lighting/contrast reasonably well
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Attempt deskew based on text orientation
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only rotate if the skew is meaningful (avoid over-correcting near-straight images)
        if abs(angle) > 0.5:
            (h, w) = thresh.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            thresh = cv2.warpAffine(
                thresh, matrix, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )

    return thresh


def extract_text_from_image(image_path):
    """
    Extracts text from an image using Tesseract OCR.

    Returns a dict:
        {
            "success": bool,
            "text": str,             # extracted text (empty string if none)
            "error": str or None,    # error message if success is False
            "confidence": float,     # average word confidence (0-100)
            "low_confidence": bool,  # True if confidence is below threshold
            "no_text_detected": bool # True if image is valid but contains no text
        }
    """
    result = {
        "success": False,
        "text": "",
        "error": None,
        "confidence": 0.0,
        "low_confidence": False,
        "no_text_detected": False,
    }

    # 1. Check file exists
    if not os.path.exists(image_path):
        result["error"] = f"File not found: {image_path}"
        return result

    if not os.path.isfile(image_path):
        result["error"] = f"Path is not a file: {image_path}"
        return result

    # 2. Check extension is a supported image format
    if not image_path.lower().endswith(SUPPORTED_EXTENSIONS):
        result["error"] = f"Unsupported file format. Supported: {SUPPORTED_EXTENSIONS}"
        return result

    # 3. Verify it's actually a valid, non-corrupted image
    try:
        with Image.open(image_path) as im:
            im.verify()
    except (UnidentifiedImageError, OSError) as e:
        result["error"] = f"File is corrupted or not a valid image: {e}"
        return result

    # 4. Preprocess (grayscale, threshold, deskew) to improve accuracy
    try:
        processed_img = _preprocess_image(image_path)
        if processed_img is None:
            result["error"] = "Could not read image data for processing."
            return result
    except Exception as e:
        result["error"] = f"Error during image preprocessing: {e}"
        return result

    # 5. Run OCR with confidence data
    try:
        data = pytesseract.image_to_data(
            processed_img, output_type=pytesseract.Output.DICT
        )
    except pytesseract.TesseractError as e:
        result["error"] = f"Tesseract OCR error: {e}"
        return result
    except Exception as e:
        result["error"] = f"Unexpected error during OCR: {e}"
        return result

    # 6. Assemble text and compute average confidence (ignore -1 = no detection)
    words = []
    confidences = []
    for i, word in enumerate(data["text"]):
        conf = int(data["conf"][i]) if str(data["conf"][i]).lstrip("-").isdigit() else -1
        if word.strip():
            words.append(word)
            if conf >= 0:
                confidences.append(conf)

    full_text = " ".join(words).strip()
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # 7. Handle "no text detected" case (e.g., photo of a person/object, not a document)
    if not full_text:
        result["no_text_detected"] = True
        result["error"] = "No text detected in image. It may not contain a document."
        return result

    result["success"] = True
    result["text"] = full_text
    result["confidence"] = round(avg_confidence, 2)
    result["low_confidence"] = avg_confidence < LOW_CONFIDENCE_THRESHOLD

    return result


# --- Test it immediately ---
if __name__ == "__main__":
    fixed_path = r"C:\Users\disha\django_projects\myproject\core\test_images\titled_doc.jpg"
    result = extract_text_from_image(fixed_path)

    if result["success"]:
        print("Success! OCR worked.")
    else:
        print(f"Error: {result['error']}")
    print(result)

    if result["success"]:
        print(f"✅ Extraction successful (confidence: {result['confidence']}%)")
        if result["low_confidence"]:
            print("⚠️  Warning: confidence is low, result may be unreliable.")
        print("\nFirst 500 chars:\n")
        print(result["text"][:500])
    elif result["no_text_detected"]:
        print("⚠️  No text found in image — may not be a document.")
    else:
        print("❌ Extraction failed.")
        print(result["error"])