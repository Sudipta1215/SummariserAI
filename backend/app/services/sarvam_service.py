import requests
import os
import logging
import base64

# Ensure you have SARVAM_API_KEY in your .env file
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

logger = logging.getLogger(__name__)

# --- VOICE MAPPING (Authentic voices for each language) ---
# Based on your error log's valid speaker list
VOICE_MAP = {
    "hi-IN": "meera",    # Fallback/Default (If meera is invalid, we swap below)
    "en-IN": "aditya",   # English
    "ta-IN": "vidya",    # Tamil
    "te-IN": "aravind",  # Telugu (Approximation, using valid list below)
    "ml-IN": "amrutha",  # Malayalam
    "bn-IN": "aditi",    # Bengali
    "kn-IN": "kavya",    # Kannada
    "mr-IN": "aditya",   # Marathi
    "gu-IN": "priya",    # Gujarati
    "pa-IN": "rohan",    # Punjabi
    "od-IN": "neha"      # Odia
}

# VALID SPEAKERS LIST (From your error log):
# 'anushka', 'abhilash', 'manisha', 'vidya', 'arya', 'karun', 'hitesh', 'aditya', 
# 'ritu', 'priya', 'neha', 'rahul', 'pooja', 'rohan', 'simran', 'kavya', 'amit', 
# 'dev', 'ishita', 'shreya', 'ratan', 'varun', 'manan', 'sumit', 'roopa', 'kabir', 
# 'aayan', 'shubh', 'ashutosh', 'advait', 'amelia', 'sophia'

def get_best_voice(lang_code):
    """
    Returns a valid speaker name based on language.
    """
    # Map languages to valid speakers from the error log
    if "hi" in lang_code: return "aditya"   # Hindi Male
    if "en" in lang_code: return "sophia"   # English Female
    if "ta" in lang_code: return "vidya"    # Tamil Female
    if "te" in lang_code: return "roopa"    # Telugu Female
    if "kn" in lang_code: return "kavya"    # Kannada Female
    if "ml" in lang_code: return "abhilash" # Malayalam Male
    if "bn" in lang_code: return "ishita"   # Bengali Female
    if "gu" in lang_code: return "priya"    # Gujarati Female
    if "pa" in lang_code: return "rohan"    # Punjabi Male
    if "mr" in lang_code: return "varun"    # Marathi Male
    
    return "aditya" # Default fallback

def translate_text_sarvam(text: str, source_code: str, target_code: str):
    """
    Translates text using Sarvam AI.
    """
    if not SARVAM_API_KEY: 
        logger.error("❌ SARVAM_API_KEY is missing.")
        return None

    url = "https://api.sarvam.ai/translate"
    payload = {
        "input": text,
        "source_language_code": source_code,
        "target_language_code": target_code,
        "mode": "formal"
    }
    headers = {
        "api-subscription-key": SARVAM_API_KEY, 
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("translated_text")
        else:
            logger.error(f"Sarvam Translate Error: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Sarvam Translate Connection Error: {e}")
        return None

def text_to_speech_sarvam(text: str, language_code: str):
    """
    Converts text to audio (WAV base64) using Sarvam AI.
    """
    if not SARVAM_API_KEY: 
        logger.error("❌ SARVAM_API_KEY is missing.")
        return None

    # 1. Select the correct voice for the language
    speaker_name = get_best_voice(language_code)

    url = "https://api.sarvam.ai/text-to-speech"
    payload = {
        "inputs": [text],
        "target_language_code": language_code,
        "speaker": speaker_name,  # ✅ Uses a valid speaker name now
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 8000,
        "enable_preprocessing": True,
        "model": "bulbul:v2"      # ✅ Updated from 'v1' to 'v2' (Fixes the 502 error)
    }
    headers = {
        "api-subscription-key": SARVAM_API_KEY, 
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            audios = response.json().get("audios", [])
            if audios:
                return base64.b64decode(audios[0])
        else:
            logger.error(f"Sarvam TTS Error: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Sarvam TTS Connection Error: {e}")
        return None