from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# LangChain / Groq Imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.utils.database import get_db
from app.models import Book

# Load Environment Variables
load_dotenv()

router = APIRouter(tags=["Agent"])

# --- API KEY SETUP ---
api_key = os.getenv("GROQ_API_KEY")

# Initialize Model
if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found. Please check your .env file.")
    llm = None
else:
    try:
        # ✅ UPDATED MODEL NAME HERE
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
        print("✅ Groq AI Connected Successfully")
    except Exception as e:
        print(f"⚠️ Groq Init Error: {e}")
        llm = None

# --- REQUEST SCHEMA ---
class ChatRequest(BaseModel):
    query: str
    book_ids: List[int]
    language: Optional[str] = "English"

# --- ROUTE ---
@router.post("/chat")
def chat_with_books(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Check Model Status
    if not llm:
        return {"response": "⚠️ System Error: AI API Key is invalid or missing. Check backend logs."}

    # 2. Fetch Text from Selected Books
    books = db.query(Book).filter(Book.book_id.in_(request.book_ids)).all()
    
    if not books:
        return {"response": "I couldn't find those books in the database."}

    # 3. Combine Context
    combined_context = ""
    for book in books:
        text = book.extracted_text or ""
        # Limit text to avoid exceeding token limits (approx 6k chars per book)
        combined_context += f"\n--- BOOK: {book.title} ---\n{text[:6000]}...\n"

    if not combined_context.strip():
        return {"response": "The selected books appear to be empty."}

    # 4. Construct Prompt
    system_prompt = """You are a helpful Book Assistant. 
    Answer the user's question based ONLY on the provided Book Context below.
    If the answer is not in the context, say "I couldn't find that information in the selected books."
    
    IMPORTANT: Answer in {language}.
    """
    
    human_prompt = """
    Context:
    {context}
    
    Question: 
    {question}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    # 5. Run Chain
    try:
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({
            "language": request.language,
            "context": combined_context,
            "question": request.query
        })
        return {"response": response}
    
    except Exception as e:
        print(f"❌ AI Generation Error: {e}")
        return {"response": f"AI Error: {str(e)}"}