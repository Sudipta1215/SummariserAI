import os
import requests
import logging
import base64
from typing import Optional, List

logger = logging.getLogger(__name__)


class SarvamService:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.base_url = "https://api.sarvam.ai"

        # translate limit ~1000; keep buffer
        self.translate_soft_limit = 900

        # TTS limits can be strict depending on model; use safe slice
        self.tts_soft_limit = 500

    # ✅ VALID SPEAKERS FOR bulbul:v2 (from your logs)
    # anushka, abhilash, manisha, vidya, arya, karun, hitesh
    def get_best_voice(self, lang_code: str) -> str:
        lang = (lang_code or "").lower()

        if any(x in lang for x in ["ta-in", "te-in", "kn-in", "ml-in"]):
            return "vidya"

        if "pa-in" in lang:
            return "hitesh"

        if "mr-in" in lang or "gu-in" in lang:
            return "arya"

        if any(x in lang for x in ["hi-in", "bn-in", "od-in"]):
            return "anushka"

        if "en-in" in lang:
            return "karun"

        # ✅ match your function-style fallback
        return "karun"

    def _headers(self) -> dict:
        return {
            "api-subscription-key": self.api_key or "",
            "Content-Type": "application/json",
        }

    def split_text(self, text: str, max_chars: int = 900) -> List[str]:
        """
        Splits text into chunks at sentence boundaries to stay under Sarvam limit.
        Similar behavior to your function split_text_for_sarvam().
        """
        if not text:
            return []

        text = text.strip()
        sentences = text.split(". ")
        chunks: List[str] = []
        current = ""

        for s in sentences:
            s = s.strip()
            if not s:
                continue

            # add back period
            piece = s if s.endswith(".") else s + "."
            piece += " "

            if len(current) + len(piece) <= max_chars:
                current += piece
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = piece

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def _call_translate_api(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        mode: str,
    ) -> Optional[str]:
        url = f"{self.base_url}/translate"
        payload = {
            "input": text,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
            "mode": mode,
        }

        try:
            res = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            if res.status_code == 200:
                return res.json().get("translated_text")
            logger.error(f"Sarvam API Error ({res.status_code}): {res.text}")
            return None
        except Exception as e:
            logger.error(f"Sarvam Connection Error: {e}")
            return None

    def translate_text(
        self,
        text: str,
        target_lang: str,
        source_lang: str = "en-IN",
        mode: str = "formal",
    ) -> Optional[str]:
        """
        ✅ Always chunk safely (prevents 1000-char failures).
        Joins translated chunks into one output.
        """
        if not self.api_key:
            logger.error("❌ SARVAM_API_KEY is missing.")
            return None

        if not text or not text.strip():
            return ""

        text = text.strip()

        # ✅ Always chunk (safe + consistent)
        chunks = self.split_text(text, max_chars=self.translate_soft_limit)
        translated_results: List[str] = []

        for i, chunk in enumerate(chunks, start=1):
            translated = self._call_translate_api(chunk, source_lang, target_lang, mode)
            if translated:
                translated_results.append(translated.strip())
            else:
                logger.error(f"Sarvam Chunk {i}/{len(chunks)} failed.")
                return None

        return " ".join(translated_results).strip() if translated_results else None

    def text_to_speech(
        self,
        text: str,
        target_lang: str,
        model: str = "bulbul:v2",
        speech_sample_rate: int = 8000,
    ) -> Optional[bytes]:
        """
        ✅ TTS sends only a safe chunk (first 500 chars),
        returns decoded WAV bytes.
        """
        if not self.api_key:
            logger.error("❌ SARVAM_API_KEY is missing.")
            return None

        if not text or not text.strip():
            return None

        safe_text = text.strip()[: self.tts_soft_limit]
        speaker_name = self.get_best_voice(target_lang)

        url = f"{self.base_url}/text-to-speech"
        payload = {
            "inputs": [safe_text],
            "target_language_code": target_lang,
            "speaker": speaker_name,
            "model": model,

            # optional params (keep if you want)
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": speech_sample_rate,
            "enable_preprocessing": True,
        }

        try:
            res = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            if res.status_code == 200:
                audios = res.json().get("audios", [])
                if audios and audios[0]:
                    return base64.b64decode(audios[0])
                logger.error("Sarvam TTS Error: audios missing/empty in response.")
                return None

            logger.error(f"Sarvam TTS Error ({res.status_code}): {res.text}")
            return None
        except Exception as e:
            logger.error(f"Sarvam TTS Connection Error: {e}")
            return None


sarvam_service = SarvamService()
