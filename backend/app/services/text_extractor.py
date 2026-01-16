import os
import re
import PyPDF2
import pdfplumber
import docx

# --------------------------------------------------
# BASIC CLEANING
# --------------------------------------------------
def clean_text(text: str) -> str:
    """Normalizes text: removes extra whitespace, fixes line breaks."""
    if not text:
        return ""
    
    text = re.sub(r'\n+', '\n', text)          # collapse many newlines → one
    text = re.sub(r'\s+', ' ', text)           # collapse spaces/tabs → one
    return text.strip()


# --------------------------------------------------
# TXT EXTRACTOR
# --------------------------------------------------
def extract_from_txt(file_path: str) -> str:
    """Tries different encodings to read a text file."""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode text file with supported encodings.")


# --------------------------------------------------
# PDF EXTRACTOR
# --------------------------------------------------
def extract_from_pdf(file_path: str) -> str:
    """Extracts text from PDF. Uses PyPDF2 first, falls back to pdfplumber."""
    text = ""

    # ---- METHOD 1: PyPDF2 (Fast) ----
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            if reader.is_encrypted:
                raise ValueError("PDF is password protected.")

            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception:
        pass  # fallback below

    # ---- METHOD 2: pdfplumber (More accurate) ----
    if not text.strip():
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")

    # Detect scanned PDFs → no text
    if not text.strip():
        raise ValueError("PDF appears to be scanned and contains no extractable text.")

    return text


# --------------------------------------------------
# DOCX EXTRACTOR
# --------------------------------------------------
def extract_from_docx(file_path: str) -> str:
    """Extracts paragraph text from DOCX."""
    try:
        doc_obj = docx.Document(file_path)
        return "\n".join(p.text for p in doc_obj.paragraphs if p.text.strip())
    except Exception as e:
        raise ValueError(f"DOCX extraction failed: {e}")


# --------------------------------------------------
# MAIN FUNCTION (FASTAPI USES THIS)
# --------------------------------------------------
def extract_text(file_path: str) -> dict:
    """
    Detects file type, extracts text, cleans text,
    and returns metadata for DB storage.
    """
    if not os.path.exists(file_path):
        return {"status": "failed", "error": "File not found"}

    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""

    try:
        if ext == ".pdf":
            raw_text = extract_from_pdf(file_path)
        elif ext == ".docx":
            raw_text = extract_from_docx(file_path)
        elif ext == ".txt":
            raw_text = extract_from_txt(file_path)
        else:
            return {"status": "failed", "error": "Unsupported file format"}

        cleaned = clean_text(raw_text)

        if not cleaned.strip():
            return {"status": "failed", "error": "Document is empty or unreadable"}

        return {
            "status": "text_extracted",
            "text": cleaned,
            "word_count": len(cleaned.split()),
            "char_count": len(cleaned),
            "error": None
        }

    except Exception as e:
        return {"status": "extraction_failed", "error": str(e)}
