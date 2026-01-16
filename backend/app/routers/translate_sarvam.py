from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import Response
from app.services.sarvam_service import translate_text_sarvam, text_to_speech_sarvam

router = APIRouter(tags=["Sarvam AI"])

# 1. TRANSLATION ENDPOINT
# Path becomes: /translate/sarvam
@router.post("/sarvam")
def sarvam_translate(payload: dict = Body(...)):
    text = payload.get("text")
    target_lang = payload.get("target_lang")
    source_lang = payload.get("source_lang", "en-IN")
    
    if not text or not target_lang:
        raise HTTPException(status_code=400, detail="Missing text or language code")
    
    result = translate_text_sarvam(text, source_lang, target_lang)
    
    if not result:
        raise HTTPException(status_code=502, detail="Sarvam translation failed (Check API Key)")
        
    return {"translated_text": result}

# 2. TTS ENDPOINT
# Path becomes: /translate/sarvam/tts  <-- FIXED PATH
@router.post("/sarvam/tts")
def sarvam_tts(payload: dict = Body(...)):
    text = payload.get("text")
    target_lang = payload.get("target_lang")
    
    if not text or not target_lang:
        raise HTTPException(status_code=400, detail="Missing text or language code")
        
    audio_bytes = text_to_speech_sarvam(text, target_lang)
    
    if not audio_bytes:
        raise HTTPException(status_code=502, detail="Sarvam TTS failed")
        
    return Response(content=audio_bytes, media_type="audio/wav")