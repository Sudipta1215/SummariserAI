from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

def translate_text(text: str, target_lang: str):
    """
    Translates text to target language using Google Translate with safety chunking.
    Accepts region codes like 'bn-IN' and cleans to 'bn'.
    """
    text = (text or "").strip()
    if not text:
        return None

    try:
        # ✅ Clean language code for GoogleTranslator
        raw = (target_lang or "").strip()
        clean = raw.split("-")[0].lower() if raw else ""

        if not clean:
            return None

        # ✅ Chinese special-case handling
        if clean == "zh":
            if "tw" in raw.lower():
                clean = "zh-TW"
            else:
                clean = "zh-CN"

        translator = GoogleTranslator(source="auto", target=clean)

        # ✅ Safety chunking (Google works best under ~2000 chars)
        max_chunk_size = 2000
        if len(text) <= max_chunk_size:
            return translator.translate(text)

        logger.info(f"Global Translation: Chunking text of length {len(text)}")

        paragraphs = text.split("\n")
        translated_parts = []
        current_chunk = ""

        for p in paragraphs:
            p = p.strip()

            # Preserve blank lines
            if not p:
                if current_chunk.strip():
                    translated_parts.append(translator.translate(current_chunk.strip()))
                    current_chunk = ""
                translated_parts.append("")
                continue

            # Try to add paragraph to current chunk
            if len(current_chunk) + len(p) + 1 <= max_chunk_size:
                current_chunk += p + "\n"
            else:
                # Flush current chunk
                if current_chunk.strip():
                    translated_parts.append(translator.translate(current_chunk.strip()))
                    current_chunk = ""

                # If one paragraph is too big, hard split it
                if len(p) > max_chunk_size:
                    start = 0
                    while start < len(p):
                        piece = p[start:start + max_chunk_size]
                        translated_parts.append(translator.translate(piece))
                        start += max_chunk_size
                else:
                    current_chunk = p + "\n"

        # Flush remaining
        if current_chunk.strip():
            translated_parts.append(translator.translate(current_chunk.strip()))

        return "\n".join(translated_parts)

    except Exception as e:
        logger.error(f"Global Translation Error: {e}")
        return None
