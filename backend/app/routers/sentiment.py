from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from textblob import TextBlob
import math
import random 

from app.utils.database import get_db
from app.models import Book, Summary

router = APIRouter(tags=["Analytics"])

@router.get("/arc/{book_id}")
def get_sentiment_arc(book_id: int, points: int = 20, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    summary = db.query(Summary).filter(Summary.book_id == book_id).first()
    
    text = ""
    if summary and summary.summary_text:
        text = summary.summary_text
    elif book and book.extracted_text:
        text = book.extracted_text
        
    if not text:
        return {"book_id": book_id, "data": []}

    n = len(text)
    
    # Ensure minimum points for a line graph
    if n < 500: points = min(5, n)
    if points < 2: points = 2

    chunk_size = math.ceil(n / points)
    data_points = []
    
    for i in range(points):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, n)
        chunk = text[start:end]
        
        if not chunk.strip():
            continue
            
        try:
            blob = TextBlob(chunk)
            polarity = blob.sentiment.polarity
            
            # ✅ SMART SNIPPET LOGIC
            # Find the sentence that best explains the score
            sentences = blob.sentences
            best_sentence = chunk[:100] # Default fallback

            if sentences:
                if polarity > 0.05:
                    # For positive chunks, show the MOST positive sentence
                    best_sentence = max(sentences, key=lambda s: s.sentiment.polarity)
                elif polarity < -0.05:
                    # For negative chunks, show the MOST negative sentence
                    best_sentence = min(sentences, key=lambda s: s.sentiment.polarity)
                else:
                    # For neutral, just show the first one
                    best_sentence = sentences[0]
            
            # Clean up the snippet
            snippet = str(best_sentence).replace("\n", " ").strip()
            if len(snippet) > 150: snippet = snippet[:150] + "..."
            
        except Exception as e:
            print(f"Error processing chunk: {e}")
            polarity = 0.0
            snippet = chunk[:50] + "..."
        
        label = "Neutral"
        if polarity > 0.05: label = "Positive"
        elif polarity < -0.05: label = "Negative"

        data_points.append({
            "progress": int((i / points) * 100), 
            "sentiment": round(polarity, 2),
            "label": label,
            "snippet": f'"{snippet}"' # Add quotes for display
        })

    return {"data": data_points}