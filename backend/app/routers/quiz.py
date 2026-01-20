from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
import os

# ✅ Correct Imports for LangChain v0.1+
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from app.utils.database import get_db
from app.models import Book

router = APIRouter(tags=["Quiz"])

# --- 1. DEFINE OUTPUT STRUCTURE ---
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text in the target language")
    options: List[str] = Field(description="A list of 4 options in the target language")
    answer: str = Field(description="The correct option string (must match one of the options)")
    explanation: str = Field(description="A short explanation of why the answer is correct, in the target language")

class QuizList(BaseModel):
    quiz: List[QuizQuestion]

# --- 2. SETUP AI ---
# Ensure GROQ_API_KEY is in your .env file
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3)
parser = PydanticOutputParser(pydantic_object=QuizList)

# --- 3. GENERATE ENDPOINT ---
@router.get("/generate/{book_id}")
def generate_quiz(book_id: int, lang: str = "en-IN", db: Session = Depends(get_db)):
    # Fetch Book Text
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book or not book.extracted_text:
        raise HTTPException(404, "Book text not found")

    # Limit text to avoid token limits (approx 3000 chars)
    context_text = book.extracted_text[:3000]

    # Map Language Codes to Names for better prompting
    lang_map = {
        "en-IN": "English", "hi-IN": "Hindi", "ta-IN": "Tamil",
        "mr-IN": "Marathi", "bn-IN": "Bengali"
    }
    target_language = lang_map.get(lang, "English")

    # --- PROMPT TEMPLATE ---
    prompt = PromptTemplate(
        template="""
        You are an expert educational AI. Generate a quiz based on the following text.
        
        TEXT CONTEXT:
        "{text}"

        INSTRUCTIONS:
        1. Generate 5 multiple-choice questions.
        2. Provide 4 options for each question.
        3. Identify the correct answer.
        4. Provide a brief explanation for the correct answer.
        5. **IMPORTANT:** Translate the Question, Options, Answer, and Explanation into {language}.
        
        {format_instructions}
        """,
        input_variables=["text", "language"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    try:
        # Invoke Chain
        chain = prompt | llm | parser
        result = chain.invoke({"text": context_text, "language": target_language})
        return result
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        raise HTTPException(500, f"Failed to generate quiz: {str(e)}")