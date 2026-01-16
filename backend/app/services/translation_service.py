from deep_translator import GoogleTranslator

def translate_text(text: str, target_lang: str):
    """
    Translates text to the target language using Google Translate.
    """
    try:
        # GoogleTranslator handles chunking automatically for long text
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation Error: {e}")
        return None