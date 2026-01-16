from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import Response
from gtts import gTTS
import io

router = APIRouter(tags=["Audio"])

@router.post("/generate")
async def generate_audio(payload: dict = Body(...)):
    """
    Converts text to MP3 audio in ANY language using Google TTS.
    Default to 'en' if not specified.
    """
    text = payload.get("text")
    lang = payload.get("lang", "en") # Accept language code
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        # Generate audio in memory
        tts = gTTS(text=text, lang=lang)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        return Response(content=audio_fp.read(), media_type="audio/mpeg")
    except Exception as e:
        # Fallback to English if language code fails
        try:
            tts = gTTS(text=text, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            return Response(content=audio_fp.read(), media_type="audio/mpeg")
        except:
            raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")