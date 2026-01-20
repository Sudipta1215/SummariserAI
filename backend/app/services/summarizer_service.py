import os
import time
import re
import logging
from typing import Dict, Any, Optional

from google import genai
from google.genai.errors import ClientError
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type

from app.utils.postprocessing import clean_formatting, extract_local_keywords

logger = logging.getLogger(__name__)


def wait_for_files_active(client: genai.Client, files, timeout_seconds: int = 180):
    logger.info("⏳ Gemini performing OCR/Analysis...")
    start = time.time()

    for f in files:
        while True:
            file_obj = client.files.get(name=f.name)
            state = str(file_obj.state).upper()

            if "ACTIVE" in state:
                break
            if "FAILED" in state:
                raise RuntimeError(f"OCR Failed: {file_obj.name}")
            if time.time() - start > timeout_seconds:
                raise TimeoutError("Gemini processing timed out.")

            time.sleep(5)

    logger.info("✅ File is ACTIVE.")


class SummarizerService:
    _instance: Optional["SummarizerService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SummarizerService, cls).__new__(cls)
            cls._instance._initialize_api()
        return cls._instance

    def _initialize_api(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is missing from .env")

        self.client = genai.Client(api_key=self.api_key)

        # ✅ Get primary and fallback from .env
        raw_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.model_name = raw_model.replace("models/", "").strip()
        
        # Add fallback model to the service instance
        raw_fallback = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")
        self.fallback_model = raw_fallback.replace("models/", "").strip()

        logger.info(f"✅ Gemini API Initialized (Primary: {self.model_name}, Fallback: {self.fallback_model})")
    @retry(
        wait=wait_exponential_jitter(initial=10, max=120),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(ClientError),
        reraise=True,
    )
    def generate_summary(
        self,
        file_path: str,
        length_option: str = "medium",
        style: str = "paragraph",
    ) -> Dict[str, Any]:
        uploaded_file = None

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Invalid file path: {file_path}")

            # 1) Upload + OCR wait
            uploaded_file = self.client.files.upload(file=file_path)
            wait_for_files_active(self.client, [uploaded_file])

            # 2) Style normalize
            style_norm = (style or "paragraph").strip().lower()
            is_bullet_mode = style_norm in {"bullet", "bullets", "bullet points", "bullet_points"}

            # 3) Prompt
            if is_bullet_mode:
                style_instruction = (
                    "Format the summary as a vertical list of bullet points. "
                    "Each bullet MUST start with '- ' on a NEW LINE. "
                    "Each bullet should ideally be one sentence. "
                    "Do not use paragraphs."
                )
            else:
                style_instruction = (
                    "Format the summary as cohesive paragraphs. "
                    "Do not use bullet points, dashes, or lists."
                )

            prompt = (
                "Summarize the provided document accurately.\n"
                f"Desired Length: {length_option}\n"
                f"{style_instruction}\n"
                "Provide only the summary text."
            )

            # 4) Generate
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[uploaded_file, prompt],
            )

            raw_text = getattr(response, "text", "") or ""
            polished_text = clean_formatting(raw_text).strip()

            # =========================================
            # 5) STRICT RECONSTRUCTION (FIXED)
            # =========================================
            if is_bullet_mode:
                # Split by newline OR bullet markers that may appear inline
                raw_points = re.split(r"\n|(?<=\s)[-•*]\s", polished_text)

                bullets = []
                for pt in raw_points:
                    clean_pt = pt.strip().lstrip("-*• ").strip()
                    if clean_pt:
                        bullets.append(clean_pt)

                polished_text = "\n".join([f"- {b}" for b in bullets]).strip()

            else:
                # Keep real paragraphs: split by double newline
                paragraphs = [p.strip() for p in polished_text.split("\n\n") if p.strip()]
                clean_paragraphs = []

                for p in paragraphs:
                    # Flatten lines INSIDE the paragraph (prevents line-by-line output)
                    lines = [line.strip() for line in p.splitlines() if line.strip()]
                    # Remove accidental bullet markers at line starts
                    lines = [ln.lstrip("-*• ").strip() for ln in lines]
                    flattened = " ".join(lines).strip()
                    if flattened:
                        clean_paragraphs.append(flattened)

                polished_text = "\n\n".join(clean_paragraphs).strip()

            return {
                "summary_text": polished_text,
                "keywords": extract_local_keywords(polished_text) or [],
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Summarizer Error: {str(e)}", exc_info=True)
            return {"summary_text": f"Error: {str(e)}", "keywords": [], "status": "failed"}

        finally:
            if uploaded_file:
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except Exception:
                    pass


summarizer_service = SummarizerService()
