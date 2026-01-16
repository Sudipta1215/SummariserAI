import json
import logging
# Ensure agent_services.py is correct and llm is available
from app.services.agent_services import llm

logger = logging.getLogger(__name__)

def generate_quiz_from_text(text_chunk: str):
    """
    Generates 5 Multiple Choice Questions (MCQ) from text.
    Returns a list of {"question": str, "options": [str], "answer": str}
    """
    if not text_chunk:
        return []

    prompt = f"""
    Generate 5 multiple-choice questions based on the following text.
    Return ONLY a raw JSON array. Do not wrap in markdown or code blocks.
    
    Format:
    [
        {{
            "question": "What is the capital of France?",
            "options": ["Berlin", "Madrid", "Paris", "Rome"],
            "answer": "Paris"
        }}
    ]
    
    Text:
    {text_chunk[:3000]}
    
    JSON Output:
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Cleanup Markdown if present (e.g. ```json ... ```)
        if "```" in content:
            content = content.split("```")[1]
            content = content.replace("json", "").strip()
            
        data = json.loads(content)
        return data
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        return []