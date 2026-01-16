from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import shutil
import os
import fitz  # PyMuPDF

from app.utils.database import get_db
from app.models import Book

# ✅ NO PREFIX HERE (Handled in main.py)
router = APIRouter(tags=["Books"])

# ==========================================
# 📝 PYDANTIC SCHEMAS
# ==========================================
class BookResponse(BaseModel):
    book_id: int
    title: str
    author: Optional[str] = None
    status: str
    is_flagged: bool = False
    
    # ✅ FIX: Use 'created_at' to match your Database Model
    created_at: datetime
    
    # Analytics
    word_count: Optional[int] = 0
    char_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# ==========================================
# ⚙️ HELPER FUNCTIONS
# ==========================================
def extract_text_from_file(file_path: str) -> str:
    text = ""
    try:
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    except Exception as e:
        print(f"Text extraction failed: {e}")
    return text

def process_book_background(book_id: int, file_path: str, db: Session):
    try:
        text = extract_text_from_file(file_path)
        book = db.query(Book).filter(Book.book_id == book_id).first()
        if book:
            book.extracted_text = text
            book.word_count = len(text.split())
            book.char_count = len(text)
            book.status = "completed"
            db.commit()
            print(f"✅ Processed Book {book_id}")
    except Exception as e:
        print(f"❌ Failed to process book {book_id}: {e}")
        book = db.query(Book).filter(Book.book_id == book_id).first()
        if book:
            book.status = "failed"
            db.commit()

# ==========================================
# 📂 ROUTES
# ==========================================

@router.post("/", response_model=BookResponse)
async def upload_book(
    title: str = Form(...),
    author: str = Form(None),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    # 1. Validation
    if not file.filename.lower().endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT allowed")

    # 2. Save File
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Create DB Entry
    new_book = Book(
        title=title,
        author=author,
        user_id=1,  # Default to admin for now
        file_path=file_path,
        status="processing",
        extracted_text="",
        is_flagged=False
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # 4. Background Task
    background_tasks.add_task(process_book_background, new_book.book_id, file_path, db)

    return new_book

@router.get("/", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.created_at.desc()).all()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Delete related summaries first (Foreign Key)
    # Import locally to avoid circular import issues
    from app.models import Summary
    db.query(Summary).filter(Summary.book_id == book_id).delete()
    
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}