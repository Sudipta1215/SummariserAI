from gtts import gTTS
import io
import logging

logger = logging.getLogger(__name__)

def generate_world_audio(text: str, lang_code: str):
    try:
        text = (text or "").strip()
        if not text:
            return None

        clean_lang = (lang_code or "en").split('-')[0].lower()

        # Google TTS limit is high, but keep it fast
        tts = gTTS(text=text[:1000], lang=clean_lang)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.read()

    except Exception as e:
        logger.error(f"gTTS Error: {e}")
        return None
