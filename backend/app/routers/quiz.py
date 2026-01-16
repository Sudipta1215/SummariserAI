from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import Book
from app.services.quiz_service import generate_quiz_from_text

# ✅ CORRECTED: Removed prefix="/quiz" (Handled in main.py)
router = APIRouter(tags=["Quiz"])

@router.get("/generate/{book_id}")
def get_quiz(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    
    if not book or not book.extracted_text:
        raise HTTPException(status_code=404, detail="Book not found or empty")
    
    # Generate questions
    questions = generate_quiz_from_text(book.extracted_text)
    
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions")
        
    return {"quiz": questions}