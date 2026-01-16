from fastapi import APIRouter, HTTPException, Body
from app.services.translation_service import translate_text

router = APIRouter(tags=["Translation"])

# Path becomes: /translate/translate
@router.post("/translate")
def translate_content(payload: dict = Body(...)):
    text = payload.get("text")
    target_lang = payload.get("target_lang")
    
    if not text or not target_lang:
        raise HTTPException(status_code=400, detail="Text and target_lang are required")
        
    translated = translate_text(text, target_lang)
    
    if not translated:
        raise HTTPException(status_code=500, detail="Translation failed")
        
    return {"translated_text": translated}