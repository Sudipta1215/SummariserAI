import fitz  # PyMuPDF
import docx
import os

class BookService:
    def extract_text(self, file_path: str) -> str:
        """Extracts text based on file extension."""
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        elif ext == ".txt":
            return self._extract_txt(file_path)
        else:
            raise ValueError("Unsupported file format")

    def _extract_pdf(self, path):
        try:
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")

    def _extract_docx(self, path):
        try:
            doc = docx.Document(path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {e}")

    def _extract_txt(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading TXT: {e}")

    def chunk_text(self, text: str, chunk_size: int = 500):
        """Splits text into chunks of `chunk_size` words."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += 1
            if current_length >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

# ✅ CORRECT: We create the instance here at the bottom.
book_service = BookService()