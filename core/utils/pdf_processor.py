import os
import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Opens a PDF and returns the text from all pages.


    Returns a dict:
        {
            "success": bool,
            "text": str,          # extracted text (empty string if none)
            "error": str or None, # error message if success is False
            "needs_ocr": bool     # True if PDF opened fine but has no extractable text
        }
    """
    result = {
        "success": False,
        "text": "",
        "error": None,
        "needs_ocr": False,
    }

    # 1. Check the file actually exists before trying to open it
    if not os.path.exists(pdf_path):
        result["error"] = f"File not found: {pdf_path}"
        return result

    # 2. Check it's actually a file (not a directory) and has a .pdf extension
    if not os.path.isfile(pdf_path):
        result["error"] = f"Path is not a file: {pdf_path}"
        return result

    if not pdf_path.lower().endswith(".pdf"):
        result["error"] = f"File does not appear to be a PDF: {pdf_path}"
        return result

    doc = None
    try:
        # 3. Handle corrupted / invalid / password-protected PDFs
        doc = pymupdf.open(pdf_path)

        if doc.is_encrypted:
            # Try to unlock with an empty password (some "protected" PDFs use this)
            if not doc.authenticate(""):
                result["error"] = "PDF is password-protected and could not be opened."
                return result

        full_text = ""
        for page in doc:
            full_text += page.get_text("text") + "\n"

        full_text = full_text.strip()

        # 4. Handle scanned/image-only PDFs (opened fine, but no extractable text)
        if not full_text:
            result["needs_ocr"] = True
            result["error"] = "No extractable text found. This PDF may be scanned/image-based (OCR needed)."
            return result

        result["success"] = True
        result["text"] = full_text
        return result

    except pymupdf.FileDataError:
        result["error"] = "File is corrupted or not a valid PDF."
        return result
    except Exception as e:
        result["error"] = f"Unexpected error extracting text: {e}"
        return result
    finally:
        if doc is not None:
            doc.close()


# --- Test it immediately ---
if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..', 'DISHA G Certificate.pdf')
    result = extract_text_from_pdf(file_path)

    if result["success"]:
        print("✅ Extraction successful. First 500 chars:\n")
        print(result["text"][:500])
    elif result["needs_ocr"]:
        print("⚠️  PDF opened but has no text layer — needs OCR step.")
        print(result["error"])
    else:
        print("❌ Extraction failed.")
        print(result["error"])



    


