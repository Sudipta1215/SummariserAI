from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response

from app.services.sarvam_service import sarvam_service

# ✅ Keep prefix empty here if you are adding prefix="/translate" in main.py
router = APIRouter(tags=["Sarvam AI"])

class TranslationRequest(BaseModel):
    text: str
    target_language_code: str

@router.post("/sarvam")
async def translate_indic(request: TranslationRequest):
    result = sarvam_service.translate_text(
        request.text,
        request.target_language_code
    )
    if not result:
        raise HTTPException(status_code=502, detail="Sarvam Translation API failed")

    return {"translated_text": result}

@router.post("/sarvam/tts")
async def tts_indic(request: TranslationRequest):
    # ✅ service now returns WAV bytes (already decoded)
    audio_bytes = sarvam_service.text_to_speech(
        request.text,
        request.target_language_code
    )
    if not audio_bytes:
        raise HTTPException(status_code=502, detail="Sarvam TTS API failed")

    return Response(content=audio_bytes, media_type="audio/wav")
