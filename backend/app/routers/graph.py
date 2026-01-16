from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import Book, Summary, User

router = APIRouter(tags=["Knowledge Graph"])

@router.get("/{book_id}")
def generate_knowledge_graph(book_id: int, db: Session = Depends(get_db)):
    # 1. Fetch Data
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
        
    user = db.query(User).filter(User.user_id == book.user_id).first()
    summaries = db.query(Summary).filter(Summary.book_id == book_id).all()

    nodes = []
    edges = []
    
    # 2. Add Central Node (The Book)
    nodes.append({"id": f"Book_{book_id}", "label": book.title, "color": "#E63946"}) # Red

    # 3. Add Author Node
    if book.author:
        author_id = f"Author_{book.author}"
        nodes.append({"id": author_id, "label": book.author, "color": "#457B9D"}) # Blue
        edges.append({"source": author_id, "target": f"Book_{book_id}", "relation": "wrote"})

    # 4. Add User Node (Owner)
    if user:
        user_node_id = f"User_{user.user_id}"
        nodes.append({"id": user_node_id, "label": user.name, "color": "#1D3557"}) # Navy
        edges.append({"source": user_node_id, "target": f"Book_{book_id}", "relation": "uploaded"})

    # 5. Add Summary Nodes & Keywords
    for idx, sm in enumerate(summaries):
        summary_node_id = f"Summary_{sm.summary_id}"
        nodes.append({"id": summary_node_id, "label": f"Summary {idx+1}", "color": "#F4A261"}) # Orange
        edges.append({"source": f"Book_{book_id}", "target": summary_node_id, "relation": "has_summary"})
        
        # Simple Keyword Extraction (Naive approach for demo)
        # In a real app, use NLP (Spacy/NLTK) here
        if sm.summary_text:
            # Extract capitalized words as "Concepts"
            words = set([w.strip(".,") for w in sm.summary_text.split() if w[0].isupper() and len(w) > 4])
            for i, word in enumerate(list(words)[:5]): # Limit to 5 concepts per summary
                concept_id = f"Concept_{word}"
                # Avoid duplicates
                if not any(n['id'] == concept_id for n in nodes):
                    nodes.append({"id": concept_id, "label": word, "color": "#2A9D8F"}) # Teal
                
                edges.append({"source": summary_node_id, "target": concept_id, "relation": "mentions"})

    return {"nodes": nodes, "edges": edges}