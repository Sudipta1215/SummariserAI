from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import shutil
import os
import fitz

from app.utils.database import get_db, SessionLocal
from app.models import Book, User
# Now this import will work!
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

def analyze_and_update_book(book_id: int, file_path: str, db_session_maker):
    db: Session = db_session_maker()
    try:
        book = db.query(Book).filter(Book.book_id == book_id).first()
        if not book: return
        text = ""
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        book.extracted_text = text
        book.word_count = len(text.split())
        book.char_count = len(text)
        book.status = "completed"
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

@router.post("/", response_model=BookResponse)
async def upload_book(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    author: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_book = Book(
        title=title,
        author=author,
        user_id=current_user.user_id,
        file_path=file_path,
        status="processing",
        word_count=0,
        char_count=0
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    background_tasks.add_task(analyze_and_update_book, new_book.book_id, file_path, SessionLocal)
    return new_book

@router.get("/", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Book).filter(Book.user_id == current_user.user_id).all()

# In backend/app/routers/books.py
@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.book_id == book_id, Book.user_id == current_user.user_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}