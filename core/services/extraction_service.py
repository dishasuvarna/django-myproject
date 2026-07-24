# import os
# from core.utils.pdf_processor import extract_text_from_pdf
# from core.utils.image_OCR import extract_text_from_image
# from core.encryption_service import EncryptionService

# from core.services.ai_summary_service import AISummaryService

# PDF_EXTENSIONS = ('.pdf',)
# IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')


# class ExtractionService:
#     """
#     Runs OCR/text extraction on an already-saved MedicalReport's file
#     and stores the result back onto that report. Designed to never raise -
#     if extraction fails, the report just gets an 'error' status instead of
#     breaking the upload flow.
#     """

#     @staticmethod
#     def process_report(report):
#         try:
#             file_path = report.file.path
#         except Exception:
#             report.extraction_status = 'error'
#             report.save(update_fields=['extraction_status'])
#             return report

#         ext = os.path.splitext(file_path)[1].lower()

#         try:
#             if ext in PDF_EXTENSIONS:
#                 result = extract_text_from_pdf(file_path)
#                 ExtractionService._apply_pdf_result(report, result)
#             elif ext in IMAGE_EXTENSIONS:
#                 result = extract_text_from_image(file_path)
#                 ExtractionService._apply_image_result(report, result)
#             else:
#                 report.extraction_status = 'unsupported'
#         #except Exception:
#             #report.extraction_status = 'error'
#         except Exception as e:
#             print("EXTRACTION PROCESSING ERROR:", scrub_for_log(e))
#             report.extraction_status = 'error'

#         if report.extraction_status in ('success', 'low_confidence'):
#             try:
#                 plain_text = EncryptionService.decrypt(report.extracted_text)
#                 summary_result = AISummaryService.generate_summary(plain_text)
#                 if summary_result['success']:
#                     report.ai_summary = EncryptionService.encrypt(summary_result['summary'])
#                 else:
#                     print("AI SUMMARY SKIPPED:", scrub_for_log(summary_result['error']))

#             except Exception as e:
#                 from core.utils.log_scrubber import scrub_for_log
#                 print("AI SUMMARY ERROR:", scrub_for_log(e))
#                 # print(f"DEBUG: Error caught: {scrub_for_log(e)}", flush=True)


#         report.save(update_fields=['extracted_text', 'extraction_status', 'ocr_confidence', 'ai_summary'])
#         return report

#     @staticmethod
#     def _apply_pdf_result(report, result):
#         if result.get('success'):
#             report.extracted_text = EncryptionService.encrypt(result['text'])
#             report.extraction_status = 'success'
#         elif result.get('needs_ocr'):
#             report.extraction_status = 'needs_ocr'
#         else:
#             report.extraction_status = 'error'

#     @staticmethod
#     def _apply_image_result(report, result):
#         if result.get('success'):
#             report.extracted_text = EncryptionService.encrypt(result['text'])
#             report.ocr_confidence = result.get('confidence')
#             report.extraction_status = (
#                 'low_confidence' if result.get('low_confidence') else 'success'
#             )
#         elif result.get('no_text_detected'):
#             report.extraction_status = 'no_text'
#         else:
#             report.extraction_status = 'error'



import os
from core.utils.pdf_processor import extract_text_from_pdf
from core.utils.image_OCR import extract_text_from_image
from core.encryption_service import EncryptionService
from core.services.ai_summary_service import AISummaryService
from core.utils.log_scrubber import scrub_for_log

PDF_EXTENSIONS = ('.pdf',)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')


class ExtractionService:
    """
    Runs OCR/text extraction on an already-saved MedicalReport's file
    and stores the result back onto that report. Designed to never raise -
    if extraction fails, the report just gets an 'error' status instead of
    breaking the upload flow.
    """

    @staticmethod
    def process_report(report):
        try:
            file_path = report.file.path
        except Exception:
            report.extraction_status = 'error'
            report.save(update_fields=['extraction_status'])
            return report

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext in PDF_EXTENSIONS:
                result = extract_text_from_pdf(file_path)
                ExtractionService._apply_pdf_result(report, result)
            elif ext in IMAGE_EXTENSIONS:
                result = extract_text_from_image(file_path)
                ExtractionService._apply_image_result(report, result)
            else:
                report.extraction_status = 'unsupported'
        except Exception as e:
            print("EXTRACTION PROCESSING ERROR:", scrub_for_log(e))
            report.extraction_status = 'error'

        if report.extraction_status in ('success', 'low_confidence'):
            try:
                plain_text = EncryptionService.decrypt(report.extracted_text)
                summary_result = AISummaryService.generate_summary(plain_text)
                if summary_result['success']:
                    report.ai_summary = EncryptionService.encrypt(summary_result['summary'])
                else:
                    print("AI SUMMARY SKIPPED:", scrub_for_log(summary_result['error']))
            except Exception as e:
                print("AI SUMMARY ERROR:", scrub_for_log(e))

        report.save(update_fields=['extracted_text', 'extraction_status', 'ocr_confidence', 'ai_summary'])
        return report

    @staticmethod
    def _apply_pdf_result(report, result):
        if result.get('success'):
            report.extracted_text = EncryptionService.encrypt(result['text'])
            report.extraction_status = 'success'
        elif result.get('needs_ocr'):
            report.extraction_status = 'needs_ocr'
        else:
            report.extraction_status = 'error'

    @staticmethod
    def _apply_image_result(report, result):
        if result.get('success'):
            report.extracted_text = EncryptionService.encrypt(result['text'])
            report.ocr_confidence = result.get('confidence')
            report.extraction_status = (
                'low_confidence' if result.get('low_confidence') else 'success'
            )
        elif result.get('no_text_detected'):
            report.extraction_status = 'no_text'
        else:
            report.extraction_status = 'error'