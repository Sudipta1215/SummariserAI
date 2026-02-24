from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import shutil
import os
import fitz  # PyMuPDF for PDF parsing

from app.utils.database import get_db
from app.models import Book, User
from app.routers.auth import get_current_user 

router = APIRouter(tags=["Books"])

class BookResponse(BaseModel):
    book_id: int
    title: str
    author: Optional[str] = None
    status: str
    is_flagged: bool = False
    created_at: datetime
    word_count: int
    char_count: int

    class Config:
        from_attributes = True

@router.post("/", response_model=BookResponse)
async def upload_book(
    title: str = Form(...),
    author: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Setup directory and save the file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Extract Text and Calculate Counts Immediately
    extracted_text = ""
    try:
        if file_path.endswith(".pdf"):
            # Open PDF and extract text from all pages
            doc = fitz.open(file_path)
            extracted_text = "\n".join([page.get_text() for page in doc])
            doc.close()
        elif file_path.endswith(".txt"):
            # Read plain text files
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

    # 3. Calculate metrics
    word_count = len(extracted_text.split())
    char_count = len(extracted_text)

    # 4. Save to Database with real values
    new_book = Book(
        title=title,
        author=author,
        user_id=current_user.user_id,
        file_path=file_path,
        extracted_text=extracted_text, # Save text for summarizer
        status="completed",            # Mark as ready immediately
        word_count=word_count,
        char_count=char_count
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book # Frontend now gets word_count > 0

@router.get("/", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Book).filter(Book.user_id == current_user.user_id).all()

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.book_id == book_id, Book.user_id == current_user.user_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Remove file from disk if it exists
    if os.path.exists(book.file_path):
        os.remove(book.file_path)

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}