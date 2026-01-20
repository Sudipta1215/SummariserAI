from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import Response
import logging

from app.services.audio_service import generate_world_audio  # ✅ use your service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Audio"])

@router.post("/generate")
async def generate_audio(payload: dict = Body(...)):
    """
    Converts text to MP3 audio in many languages using Google gTTS.
    Returns audio/mpeg bytes.
    """
    text = (payload.get("text") or "").strip()
    raw_lang = payload.get("lang") or payload.get("language_code") or "en"

    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    # ✅ Use service (already cleans lang + limits length)
    audio_bytes = generate_world_audio(text=text, lang_code=raw_lang)

    # ✅ fallback to English if language not supported / fails
    if not audio_bytes:
        logger.warning(f"⚠️ Audio generation failed for lang={raw_lang}. Falling back to English.")
        audio_bytes = generate_world_audio(text=text, lang_code="en")

    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Audio generation failed")

    return Response(content=audio_bytes, media_type="audio/mpeg")
