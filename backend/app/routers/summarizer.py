from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.utils.database import get_db, SessionLocal
from app.models import Book, Summary
from app.services.summarizer_service import summarizer_service
from app.utils.export_utils import generate_txt_content, generate_pdf_content
import logging
from app.limiter import limiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# --- BACKGROUND WORKER ---
def run_local_summarization_task(book_id: int, length: str, style: str, detail: str):
    logger.info(f"🏗️ [Background] Processing Book {book_id}...")
    db = SessionLocal()
    
    try:
        book = db.query(Book).filter(Book.book_id == book_id).first()
        if not book or not book.extracted_text: 
            return

        clean_text = book.extracted_text.replace("\x00", "")
        if not clean_text.strip():
            book.status = "failed"
            db.commit()
            return

        result = summarizer_service.generate_summary(
            raw_text=clean_text, 
            length_option=length.lower(),
            style=style,
            detail=detail
        )
        
        new_summary = Summary(
            book_id=book_id,
            user_id=book.user_id,
            summary_text=result["summary_text"],
            keywords=result["keywords"],
            length_setting=length,
            style_setting=style
        )
        db.add(new_summary)

        book.status = "completed"
        db.commit()
        logger.info(f"✅ [Background] Saved new version successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to generate summary: {e}")
        try:
            book.status = "failed"
            db.commit()
        except: 
            pass
    finally:
        db.close()

# --- 1. GET LATEST SUMMARY ---
# Path becomes: /summary/{book_id}
@router.get("/{book_id}")
def get_latest_summary(book_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.book_id == book_id)\
                .order_by(desc(Summary.summary_id)).first()
    
    if not summary:
        raise HTTPException(404, "Summary not found")
    
    return {
        "summary": summary.summary_text,
        "keywords": summary.keywords,
        "length": summary.length_setting,
        "style": summary.style_setting
    }

# --- 2. GENERATE SUMMARY ---
# Path becomes: /summary/{book_id} (POST)
@router.post("/{book_id}")
@limiter.limit("5/minute")
async def trigger_summarization(
    request: Request,
    book_id: int, 
    length: str = "Medium", 
    style: str = "Paragraph", 
    detail: str = "Standard",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book: raise HTTPException(404, "Book not found")

    book.status = "processing"
    db.commit()
    
    if background_tasks:
        background_tasks.add_task(run_local_summarization_task, book_id, length, style, detail)
    
    return {"status": "processing", "message": "Started job"}

# --- 3. EXPORT ---
# Path becomes: /summary/{book_id}/export
@router.get("/{book_id}/export")
def export_summary(
    book_id: int, 
    format: str = "txt", 
    db: Session = Depends(get_db)
):
    summary = db.query(Summary).filter(Summary.book_id == book_id)\
                .order_by(desc(Summary.summary_id)).first()
    
    if not summary: raise HTTPException(404, "Summary not found")
        
    book = db.query(Book).filter(Book.book_id == book_id).first()
    date_str = summary.created_at.strftime("%Y-%m-%d")

    if format.lower() == "txt":
        content = generate_txt_content(book.title, book.author, date_str, summary.summary_text)
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=summary_{book_id}.txt"}
        )

    elif format.lower() == "pdf":
        pdf_buffer = generate_pdf_content(book.title, book.author, date_str, summary.summary_text)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=summary_{book_id}.pdf"}
        )
    else:
        raise HTTPException(400, "Unsupported format. Use 'txt' or 'pdf'")

# --- 4. HISTORY ---
# Path becomes: /summary/history/{book_id}
@router.get("/history/{book_id}")
def get_summary_history(book_id: int, db: Session = Depends(get_db)):
    return db.query(Summary).filter(Summary.book_id == book_id)\
             .order_by(desc(Summary.created_at)).all()

# --- 5. FAVORITE ---
# Path becomes: /summary/{summary_id}/favorite
@router.post("/{summary_id}/favorite")
def toggle_favorite(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.summary_id == summary_id).first()
    if not summary: raise HTTPException(404, "Summary not found")
    
    summary.is_favorite = not summary.is_favorite
    db.commit()
    return {"status": "updated", "is_favorite": summary.is_favorite}

# --- 6. DELETE ---
# Path becomes: /summary/{summary_id}
@router.delete("/{summary_id}")
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.summary_id == summary_id).first()
    if not summary: raise HTTPException(404, "Summary not found")
    
    db.delete(summary)
    db.commit()
    return {"status": "deleted"}