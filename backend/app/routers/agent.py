from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# ✅ Import your Agentic RAG functions
from app.services.agent_service import run_agent, load_book_into_agent, book_memory
from app.utils.database import get_db
from app.models import Book

load_dotenv()
router = APIRouter(tags=["Agent"])

class ChatRequest(BaseModel):
    query: str
    book_ids: List[int]
    language: Optional[str] = "English"

@router.post("/chat")
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Handle Book Context (If books are selected)
        if request.book_ids:
            books = db.query(Book).filter(Book.book_id.in_(request.book_ids)).all()
            if books:
                # Combine text from all selected books
                full_text = "\n".join([b.extracted_text for b in books if b.extracted_text])
                # ✅ Load into the Agent's Vector Memory
                load_book_into_agent(full_text)
            else:
                book_memory.has_book = False
        else:
            # ✅ No books selected: Clear memory for General/Web mode
            book_memory.has_book = False
            book_memory.vector_store = None

        # 2. Run the Multi-Agent Workflow (Planner -> Researcher -> Reasoner)
        # This will automatically use Web Search or General Knowledge if needed.
        response = run_agent(request.query)
        
        return {"response": response}

    except Exception as e:
        print(f"❌ Agent Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))