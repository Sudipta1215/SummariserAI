from fastapi import APIRouter, HTTPException, Body
from app.services.translation_service import translate_text

# ✅ Recommended: keep NO prefix here if main.py does prefix="/translate"
router = APIRouter(tags=["Translation"])

@router.post("/translate")
def translate_content(payload: dict = Body(...)):
    text = (payload.get("text") or "").strip()

    # Frontend may send either key
    target_lang = payload.get("target_lang") or payload.get("target_language_code")

    if not text or not target_lang:
        raise HTTPException(status_code=400, detail="Missing 'text' or language code")

    # ✅ Google wants "bn", "hi", "en" (not "bn-IN", "en-US")
    clean_lang = target_lang.split("-")[0].lower()

    # ✅ Chinese special case
    if clean_lang == "zh":
        # Optional: detect zh-TW if frontend sends it
        if "tw" in target_lang.lower():
            clean_lang = "zh-TW"
        else:
            clean_lang = "zh-CN"

    translated = translate_text(text, clean_lang)

    if not translated:
        raise HTTPException(status_code=500, detail="Global Translation failed")

    return {"translated_text": translated}
