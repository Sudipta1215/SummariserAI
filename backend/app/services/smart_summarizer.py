import os
import re
from dotenv import load_dotenv

# 1. Load Env
load_dotenv()

# --- IMPORTS ---
from langchain_groq import ChatGroq
# Use the new text splitter package
from langchain_text_splitters import RecursiveCharacterTextSplitter 
# Use Core prompts
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# Setup LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing in .env")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

def clean_text(text):
    """Task 12: Formatting enhancements"""
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text[0].upper() + text[1:]
    return text

def extract_keywords(text):
    """Task 12: Keyword Extraction"""
    prompt = f"""
    Extract 5-7 key themes or keywords from the text below.
    Return comma-separated list.
    
    TEXT:
    {text[:4000]}
    """
    try:
        response = llm.invoke(prompt)
        return response.content.replace("Keywords:", "").strip()
    except:
        return "General, Summary"

def custom_map_reduce(docs, length, style, detail_level):
    """
    Manually implements Map-Reduce to avoid import errors.
    1. Map: Summarize each chunk.
    2. Reduce: Summarize the combined summaries.
    """
    
    # --- STEP 1: MAP (Summarize Chunks) ---
    map_template = """
    Summarize the following text chunk concisely:
    
    TEXT:
    {text}
    """
    map_prompt = PromptTemplate.from_template(map_template)
    
    chunk_summaries = []
    print(f"📚 Processing {len(docs)} chunks...")
    
    for doc in docs:
        # Invoke LLM directly for each chunk
        formatted_prompt = map_prompt.format(text=doc.page_content)
        response = llm.invoke(formatted_prompt)
        chunk_summaries.append(response.content)

    # --- STEP 2: REDUCE (Merge) ---
    combined_summaries = "\n\n".join(chunk_summaries)
    
    reduce_template = f"""
    You are an expert editor. Merge the following summaries into one final result.
    
    SETTINGS:
    - Length: {length}
    - Style: {style} (If 'Bullet Points', use a bulleted list).
    - Detail: {detail_level}
    
    SUMMARIES TO MERGE:
    {{text}}
    
    FINAL SUMMARY:
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    
    # Invoke LLM for the final merge
    formatted_reduce_prompt = reduce_prompt.format(text=combined_summaries)
    final_response = llm.invoke(formatted_reduce_prompt)
    
    return final_response.content

def generate_smart_summary(text: str, length: str, style: str, detail_level: str):
    """
    Task 11 & 12: Smart Summarization
    """
    # 1. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=6000, 
        chunk_overlap=400,
        separators=["\n\n", "\n", ". ", " "]
    )
    docs = text_splitter.create_documents([text])
    
    # 2. Run Manual Map-Reduce (Bypassing broken chain import)
    raw_summary = custom_map_reduce(docs, length, style, detail_level)
    
    # 3. Post-Process
    final_summary = clean_text(raw_summary)
    keywords = extract_keywords(final_summary)

    return {
        "summary": final_summary,
        "keywords": keywords
    }