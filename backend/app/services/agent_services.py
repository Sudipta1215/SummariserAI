import os
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

from typing import Annotated, TypedDict, List, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage 
from langchain_groq import ChatGroq
# ✅ Fixed: Use the new dedicated package
from langchain_community.tools import TavilySearchResults
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# --- CONFIGURATION ---

# 2. Setup Free LLM (Groq LLaMA 3)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing! Please check your backend/.env file.")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

# 3. Setup Free Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Setup Search Tool
tavily_tool = TavilySearchResults(max_results=3)

# --- MEMORY (RAG) SERVICE ---
class BookMemory:
    def __init__(self):
        self.vector_store = None
        self.has_book = False  # Track if a book is actually loaded

    def ingest_book(self, text_chunks: List[str]):
        if not text_chunks: 
            return
        docs = [Document(page_content=chunk) for chunk in text_chunks]
        self.vector_store = FAISS.from_documents(docs, embeddings)
        self.has_book = True
        print("✅ Book memory created successfully!")

    def query_book(self, query: str) -> str:
        if not self.vector_store:
            return ""  # Return empty string instead of error text
        
        # Search for top 5 chunks to get good context
        docs = self.vector_store.similarity_search(query, k=5)
        return "\n\n".join([d.page_content for d in docs])

book_memory = BookMemory()

# --- AGENT STATE ---
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    plan: str
    research_data: str
    final_answer: str

# --- AGENT NODES ---

def planner_node(state: AgentState):
    """Orchestrator: Decides if we need the book, the web, or just general knowledge."""
    query = state["messages"][-1].content
    has_book = book_memory.has_book
    
    prompt = f"""You are a smart AI assistant.
    User Query: "{query}"
    
    STATUS: {"Book Uploaded" if has_book else "No Book Uploaded"}
    
    Determine the best way to answer.
    1. If the user asks about the 'uploaded file', 'document', or specific points (e.g. 'point 5'), USE DOCUMENT.
    2. If the user asks a general fact (e.g. 'When was WW2?'), use GENERAL KNOWLEDGE.
    3. Only use WEB SEARCH if explicitly asked or for very recent real-time news.

    Create a concise plan.
    """
    response = llm.invoke(prompt)
    return {"plan": response.content}

def research_node(state: AgentState):
    """Researcher: Fetches context if available, otherwise relies on LLM knowledge."""
    plan = state["plan"]
    query = state["messages"][-1].content
    
    # 1. Try to get Book Context (Only if a book exists)
    book_context = ""
    if book_memory.has_book:
        book_context = book_memory.query_book(query)
    
    # 2. Web Search (Only if strictly necessary)
    web_context = ""
    if "web search" in plan.lower() or "search the internet" in query.lower():
        try:
            print("🌍 Agent is searching the web...")
            results = tavily_tool.invoke(query)
            web_context = "\n".join([r['content'] for r in results])
        except Exception:
            web_context = "Web search failed."

    # If no book is loaded, we explicitly state that so the Reasoner knows.
    if not book_context and not web_context:
        combined_data = "NO_EXTERNAL_CONTEXT_FOUND"
    else:
        combined_data = f"--- UPLOADED DOCUMENT ---\n{book_context}\n\n--- WEB RESULTS ---\n{web_context}"
        
    return {"research_data": combined_data}

def reasoner_node(state: AgentState):
    """Reasoner: The final brain that answers the user."""
    query = state["messages"][-1].content
    data = state["research_data"]
    
    # DISTINCT LOGIC:
    # If we have document data, we strictly use it.
    # If we have NO data (e.g. "When was WW2" with no book), we act like ChatGPT.
    
    if data == "NO_EXTERNAL_CONTEXT_FOUND":
        prompt = f"""You are a helpful AI assistant.
        User Query: {query}
        
        The user has not uploaded a relevant document for this specific query, or the query is general knowledge.
        Answer the question directly using your own knowledge. 
        """
    else:
        prompt = f"""You are a helpful AI assistant.
        User Query: {query}
        
        CONTEXT DATA:
        {data}
        
        INSTRUCTIONS:
        1. If the answer is in the 'UPLOADED DOCUMENT', use that primarily.
        2. If the user asks for "5 questions", generate them based ONLY on the document text.
        3. If the user asks "Explain point 5", look for a numbered list or section 5 in the text.
        4. If the document doesn't contain the answer (e.g. user asks "When was WW2?" but document is about biology), ignore the document and answer using your general knowledge.
        """
        
    response = llm.invoke(prompt)
    return {"final_answer": response.content}

# --- GRAPH CONSTRUCTION ---
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", research_node)
workflow.add_node("reasoner", reasoner_node)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "reasoner")
workflow.add_edge("reasoner", END)
app_graph = workflow.compile()

# --- PUBLIC FUNCTIONS ---
def run_agent(user_query: str):
    inputs = {"messages": [HumanMessage(content=user_query)]}
    result = app_graph.invoke(inputs)
    return result["final_answer"]

def load_book_into_agent(full_text: str):
    if not full_text: return
    print("🧠 Ingesting book into Agent Memory...")
    chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]
    book_memory.ingest_book(chunks)