from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
import json

# ✅ CORRECT IMPORTS FOR NEW LANGCHAIN
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.utils.database import get_db
from app.models import Book

router = APIRouter(tags=["KnowledgeGraph"])

# --- DATA MODELS ---
class Node(BaseModel):
    id: str
    label: str
    type: str = Field(description="Type of entity: Character, Location, Concept, Event")
    details: str = Field(description="Brief description or bio of the entity")

class Edge(BaseModel):
    source: str
    target: str
    relation: str = Field(description="Relationship label, e.g., 'friend of', 'located in'")

class GraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

# --- AI SETUP ---
# Ensure GROQ_API_KEY is set in your .env file
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3)
parser = PydanticOutputParser(pydantic_object=GraphData)

@router.get("/generate/{book_id}")
def generate_graph(book_id: int, type: str = "network", db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book or not book.extracted_text:
        raise HTTPException(404, "Book not found or empty")

    # Limit text to fit context window (approx 4000 chars)
    text_sample = book.extracted_text[:4000]

    # Define prompt based on visual type
    if type == "mindmap":
        instruction = """
        Generate a hierarchical Mind Map structure.
        - The central node should be the Book Title.
        - Level 1 nodes: Main Themes or Chapters.
        - Level 2 nodes: Key concepts, events, or characters within those themes.
        - Edges should represent 'contains' or 'relates to'.
        """
    else: # Network (standard knowledge graph)
        instruction = """
        Extract key entities (Characters, Locations, Concepts) and their relationships.
        - Focus on the most important connections.
        - Avoid creating disconnected islands.
        """

    prompt = PromptTemplate(
        template="""
        Analyze the following text and extract a Knowledge Graph.
        
        TEXT: "{text}"
        
        INSTRUCTION: {instruction}
        
        {format_instructions}
        """,
        input_variables=["text", "instruction"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    try:
        chain = prompt | llm | parser
        result = chain.invoke({"text": text_sample, "instruction": instruction})
        return result
    except Exception as e:
        print(f"Graph Gen Error: {e}")
        # Return empty structure on failure so frontend doesn't crash
        return {"nodes": [], "edges": []}