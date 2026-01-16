import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from langdetect import detect, LangDetectException

# ---------------------------------------------------------
# SETUP NLTK RESOURCES
# ---------------------------------------------------------
def setup_nltk():
    resources = ['punkt', 'stopwords', 'punkt_tab']
    for res in resources:
        try:
            nltk.data.find(f'tokenizers/{res}')
        except LookupError:
            try:
                nltk.data.find(f'corpora/{res}')
            except LookupError:
                nltk.download(res, quiet=True)

setup_nltk()

# ---------------------------------------------------------
# 1. CLEANING
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    # Remove non-printable characters (keep ASCII)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    # Remove multiple spaces
    text = re.sub(r" {2,}", " ", text)
    # Normalize paragraph breaks (max 2 newlines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

# ---------------------------------------------------------
# 2. LANGUAGE DETECTION
# ---------------------------------------------------------
def detect_language(text: str) -> str:
    try:
        # Detect on a sample to be faster
        return detect(text[:500])
    except LangDetectException:
        return "unknown"

# ---------------------------------------------------------
# 3. SENTENCE SEGMENTATION (With Protection)
# ---------------------------------------------------------
ABBREVIATIONS = ["mr", "mrs", "ms", "dr", "prof", "inc", "jr", "sr", "etc", "e.g", "i.e", "vs"]
# Initialize tokenizer once
try:
    from nltk.tokenize import PunktSentenceTokenizer
    tokenizer = PunktSentenceTokenizer()
except:
    tokenizer = None

def protect_abbreviations(text: str) -> str:
    for abbr in ABBREVIATIONS:
        # Protect Mr. -> Mr<prd>
        text = re.sub(rf"\b{abbr}\.", f"{abbr}<prd>", text, flags=re.IGNORECASE)
    return text

def protect_decimals(text: str) -> str:
    # Protect 1.5 -> 1<prd>5
    return re.sub(r"(\d)\.(\d)", r"\1<prd>\2", text)

def restore_placeholders(text: str) -> str:
    return text.replace("<prd>", ".")

def segment_sentences(text: str):
    if not text.strip():
        return []
    
    # 1. Protect special cases
    protected = protect_abbreviations(text)
    protected = protect_decimals(protected)
    
    # 2. Tokenize
    if tokenizer:
        raw_sentences = tokenizer.tokenize(protected)
    else:
        raw_sentences = sent_tokenize(protected) # Fallback

    # 3. Restore and Filter
    return [restore_placeholders(s).strip() for s in raw_sentences if len(s.strip()) > 1]

# ---------------------------------------------------------
# 4. STOP WORD HANDLING (Task Requirement)
# ---------------------------------------------------------
def remove_stop_words(text: str, language='english') -> str:
    """
    Removes common stop words. Can be enabled/disabled in orchestrator.
    """
    try:
        stop_words = set(stopwords.words(language))
        words = word_tokenize(text)
        filtered_words = [w for w in words if w.lower() not in stop_words]
        return " ".join(filtered_words)
    except:
        # If language not supported, return original
        return text

# ---------------------------------------------------------
# 5. TEXT STATISTICS
# ---------------------------------------------------------
def calculate_text_stats(text: str, sentences: list = None):
    if not text.strip():
        return {"word_count": 0, "char_count": 0, "sentence_count": 0, "reading_time_minutes": 0}

    words = word_tokenize(text)
    if not sentences:
        sentences = segment_sentences(text)

    word_count = len(words)
    
    return {
        "word_count": word_count,
        "char_count": len(text),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(word_count / len(sentences), 1) if sentences else 0,
        "reading_time_minutes": round(word_count / 200, 2)
    }

# ---------------------------------------------------------
# 6. CHUNKING
# ---------------------------------------------------------
def chunk_text(text: str, chunk_size=600, overlap=100):
    sentences = segment_sentences(text)
    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0
    chunk_id = 1

    for sentence in sentences:
        sent_word_count = len(word_tokenize(sentence))
        
        # Check if adding this sentence exceeds chunk size
        if current_word_count + sent_word_count > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                "chunk_id": chunk_id,
                "text": " ".join(current_chunk),
                "word_count": current_word_count
            })
            chunk_id += 1
            
            # Create Overlap (Backtrack)
            overlap_buffer = []
            overlap_count = 0
            for s in reversed(current_chunk):
                s_len = len(word_tokenize(s))
                if overlap_count + s_len < overlap:
                    overlap_buffer.insert(0, s)
                    overlap_count += s_len
                else:
                    break
            
            current_chunk = overlap_buffer
            current_word_count = overlap_count

        current_chunk.append(sentence)
        current_word_count += sent_word_count

    # Add final chunk
    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "text": " ".join(current_chunk),
            "word_count": current_word_count
        })

    return chunks

# ---------------------------------------------------------
# 7. ORCHESTRATOR (The Pipeline)
# ---------------------------------------------------------
def preprocess_for_summarization(text: str, chunk_size=1000, remove_stops=False):
    """
    Returns the bundle of data required for the summarizer.
    Does NOT run the AI model itself (Separation of Concerns).
    """
    validation_warnings = []

    # 1. Validation
    if not text or len(text.strip()) < 50:
        return {"error": "Text is too short to summarize."}
    
    # 2. Clean
    cleaned_text = clean_text(text)
    
    # 3. Detect Language
    language = detect_language(cleaned_text)
    if language != 'en':
        validation_warnings.append(f"Detected non-English text ({language}).")

    # 4. Stop Words (Optional Task Requirement)
    if remove_stops and language == 'en':
        cleaned_text = remove_stop_words(cleaned_text)

    # 5. Segment
    sentences = segment_sentences(cleaned_text)

    # 6. Stats
    stats = calculate_text_stats(cleaned_text, sentences)
    if stats['word_count'] > 100000:
        validation_warnings.append("Text is very long (>100k words).")

    # 7. Chunk
    chunks = chunk_text(cleaned_text, chunk_size=chunk_size)

    # Return the Data Bundle (As requested in Task 8)
    return {
        "cleaned_text": cleaned_text,
        "language": language,
        "sentences": sentences,
        "stats": stats,
        "chunks": chunks,
        "warnings": validation_warnings
    } 