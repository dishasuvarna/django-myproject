import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
REQUEST_TIMEOUT_SECONDS = 60

# Minimum characters of extracted text required before we bother summarizing.
# Avoids sending near-empty text to the model and getting a nonsense summary.
MIN_TEXT_LENGTH = 20

# Keep the prompt constrained: summarize only what's present, no inference,
# no added medical advice, no filling gaps. This matters a lot for medical text.
SUMMARY_PROMPT_TEMPLATE = (
    "You are summarizing a medical document for a doctor's quick reference. "
    "Summarize ONLY the information explicitly present in the text below. "
    "Do NOT infer a diagnosis, do NOT add medical advice, and do NOT include "
    "any detail that is not literally stated in the text. "
    "If the text is unclear or incomplete, say so plainly instead of guessing. "
    "Keep the summary to 2-4 sentences.\n\n"
    "TEXT:\n{text}\n\nSUMMARY:"
)

class AISummaryService:
    """
    Generates a short summary of extracted medical text using a local
    Ollama model. Designed to never raise - any failure (Ollama not running,
    timeout, empty text) results in a clear status instead of a crash.
    """

    @staticmethod
    def generate_summary(text):
        """
        Returns a dict:
            {
                "success": bool,
                "summary": str,
                "error": str or None,
            }
        """
        result = {"success": False, "summary": "", "error": None}

        if not text or len(text.strip()) < MIN_TEXT_LENGTH:
            result["error"] = "Text too short to summarize."
            return result

        prompt = SUMMARY_PROMPT_TEMPLATE.format(text=text.strip())

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.ConnectionError:
            result["error"] = "Could not connect to Ollama. Is it running?"
            return result
        except requests.exceptions.Timeout:
            result["error"] = "Ollama request timed out."
            return result
        except Exception as e:
            result["error"] = f"Unexpected error contacting Ollama: {e}"
            return result

        if response.status_code != 200:
            result["error"] = f"Ollama returned status {response.status_code}."
            return result

        try:
            data = response.json()
            summary_text = data.get("response", "").strip()
        except Exception as e:
            result["error"] = f"Could not parse Ollama response: {e}"
            return result

        if not summary_text:
            result["error"] = "Ollama returned an empty summary."
            return result

        result["success"] = True
        result["summary"] = summary_text
        return result