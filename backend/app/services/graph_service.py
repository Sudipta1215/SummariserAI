import json
import logging
# Ensure this import works based on your previous step
from app.services.agent_services import llm

logger = logging.getLogger(__name__)

def extract_graph_relations(text_chunk: str):
    """
    Uses LLM to extract relationships from text.
    Returns a list of {"source": "A", "target": "B", "label": "relation"}
    """
    if not text_chunk:
        return []

    # 1. Prompt the LLM
    prompt = f"""
    Analyze the following text and extract the key relationships between characters, concepts, or places.
    Return ONLY a JSON array of objects with keys: "source", "target", and "label".
    
    Example:
    [
        {{"source": "Harry", "target": "Hagrid", "label": "friend"}},
        {{"source": "Hagrid", "target": "Hogwarts", "label": "groundskeeper"}}
    ]
    
    Text to analyze:
    {text_chunk[:3000]}
    
    JSON Output:
    """
    
    try:
        # 2. Invoke LLM
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # 3. Clean Markdown Code Blocks (Common LLM behavior)
        if "```" in content:
            # Splits by ``` and takes the part inside
            content = content.split("```")[1]
            # Removes "json" if the model wrote ```json
            content = content.replace("json", "").strip()
            
        # 4. Parse JSON
        data = json.loads(content)
        return data
        
    except Exception as e:
        logger.error(f"Graph extraction error: {e}")
        # Return empty list so the app doesn't crash
        return []