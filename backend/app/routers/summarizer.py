from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
import logging

from app.utils.database import get_db, SessionLocal
from app.models import Book, Summary
from app.services.summarizer_service import summarizer_service
from app.utils.export_utils import generate_txt_content, generate_pdf_content

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Summarizer"])


# =========================
# ✅ SCHEMA
# =========================
class GenerateRequest(BaseModel):
    book_id: int
    summary_length: str = "medium"
    summary_format: str = "paragraph"


# =========================
# ✅ BACKGROUND WORKER
# =========================
def run_summarization_task(book_id: int, length: str, format: str):
    logger.info(f"🏗️ [Background] Processing Book {book_id}...")
    db = SessionLocal()

    try:
        # 1) Fetch book
        book = db.query(Book).filter(Book.book_id == book_id).first()
        if not book:
            logger.error(f"❌ Book {book_id} not found.")
            return

        if not book.file_path:
            logger.error(f"❌ Book {book_id} missing file_path.")
            book.status = "failed"
            db.commit()
            return

        # 2) Call summarizer service (✅ uses file_path)
        result = summarizer_service.generate_summary(
            file_path=book.file_path,
            length_option=length,
            style=format
        )

        summary_text = result.get("summary_text", "")
        keywords_list = result.get("keywords", []) or []

        # 3) Save summary
        new_summary = Summary(
            book_id=book_id,
            user_id=book.user_id,
            summary_text=summary_text,
            keywords=",".join(keywords_list),
            length_setting=length,
            style_setting=format
        )
        db.add(new_summary)

        # 4) Update book status
        book.status = "completed"
        db.commit()
        logger.info(f"✅ [Background] Book {book_id} Summarization Complete.")

    except Exception as e:
        logger.error(f"❌ [Background] FAILED: {e}", exc_info=True)
        try:
            book = db.query(Book).filter(Book.book_id == book_id).first()
            if book:
                book.status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


# =========================
# ✅ ROUTES
# =========================
@router.post("/generate")
def request_summary(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.book_id == req.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.status = "processing"
    db.commit()

    background_tasks.add_task(
        run_summarization_task,
        req.book_id,
        req.summary_length,
        req.summary_format
    )

    return {"message": "Summary generation started", "status": "processing"}


@router.get("/{book_id}")
def get_latest_summary(book_id: int, db: Session = Depends(get_db)):
    summary = (
        db.query(Summary)
        .filter(Summary.book_id == book_id)
        .order_by(desc(Summary.created_at))
        .first()
    )

    if summary:
        return {
            "status": "completed",
            "summary_text": summary.summary_text,
            "created_at": summary.created_at,
            "length": summary.length_setting,
            "style": summary.style_setting
        }

    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.status == "processing":
        return {"status": "processing", "summary_text": "", "message": "AI is working..."}

    if book.status == "failed":
        return {
            "status": "failed",
            "summary_text": "Generation Failed. Check backend logs.",
            "message": "Error during generation"
        }

    raise HTTPException(status_code=404, detail="Summary not found.")


@router.get("/{book_id}/export")
def export_summary(book_id: int, format: str = "txt", db: Session = Depends(get_db)):
    summary = (
        db.query(Summary)
        .filter(Summary.book_id == book_id)
        .order_by(desc(Summary.created_at))
        .first()
    )
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    date_str = summary.created_at.strftime("%Y-%m-%d") if summary.created_at else "Unknown"

    if format.lower() == "txt":
        content = generate_txt_content(book.title, book.author, date_str, summary.summary_text)
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=summary_{book_id}.txt"}
        )

    elif format.lower() == "pdf":
        pdf_buffer = generate_pdf_content(book.title, book.author, date_str, summary.summary_text)
        try:
            pdf_buffer.seek(0)  # safe reset if it's a BytesIO
        except Exception:
            pass
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=summary_{book_id}.pdf"}
        )

    raise HTTPException(status_code=400, detail="Unsupported format.")


@router.get("/history/{book_id}")
def get_history(book_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Summary)
        .filter(Summary.book_id == book_id)
        .order_by(desc(Summary.created_at))
        .all()
    )


@router.delete("/{summary_id}")
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.summary_id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    db.delete(summary)
    db.commit()
    return {"message": "Deleted"}
