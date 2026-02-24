import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_groq import ChatGroq
from langchain_community.tools import TavilySearchResults
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 1. Load Environment Variables
load_dotenv()

# --- CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
tavily_tool = TavilySearchResults(max_results=3)

# --- MEMORY (RAG) SERVICE ---
class BookMemory:
    def __init__(self):
        self.vector_store = None
        self.has_book = False

    def ingest_book(self, text_chunks: List[str]):
        if not text_chunks: return
        docs = [Document(page_content=chunk) for chunk in text_chunks]
        self.vector_store = FAISS.from_documents(docs, embeddings)
        self.has_book = True
        print("✅ Document memory active!")

    def query_book(self, query: str) -> str:
        if not self.vector_store: return ""
        docs = self.vector_store.similarity_search(query, k=5)
        return "\n\n".join([d.page_content for d in docs])

book_memory = BookMemory()

# --- AGENT STATE (Added chat_history for ChatGPT-like behavior) ---
class AgentState(TypedDict):
    messages: List[BaseMessage]
    chat_history: List[BaseMessage]
    plan: str
    research_data: str
    final_answer: str

# --- AGENT NODES ---

def planner_node(state: AgentState):
    """Intent Router: Distinguishes between Chat, Document, and Web search."""
    query = state["messages"][-1].content
    
    prompt = f"""You are a smart orchestrator.
    User Query: "{query}"
    Document Status: {"Attached" if book_memory.has_book else "None"}
    
    Your task is to categorize the intent:
    - 'CHAT': Greeting, small talk, or general philosophy.
    - 'DOC': Specific questions about the uploaded file or its content.
    - 'WEB': Questions about current events, news, or specialized facts not in a document.
    
    Respond with ONLY the category and a 1-sentence reasoning.
    """
    response = llm.invoke(prompt)
    return {"plan": response.content}

def research_node(state: AgentState):
    """Data Fetcher: Executes the retrieval based on the plan."""
    plan = state["plan"].upper()
    query = state["messages"][-1].content
    
    book_context = ""
    web_context = ""

    # Check for Document Search
    if "DOC" in plan and book_memory.has_book:
        book_context = book_memory.query_book(query)
    
    # Check for Web Search
    if "WEB" in plan or "search" in query.lower():
        try:
            results = tavily_tool.invoke(query)
            web_context = "\n".join([r['content'] for r in results])
        except:
            web_context = "Web search unavailable."

    if not book_context and not web_context:
        combined_data = "GENERAL_KNOWLEDGE_MODE"
    else:
        combined_data = f"DOC_STUFF: {book_context}\n\nWEB_STUFF: {web_context}"
        
    return {"research_data": combined_data}

def reasoner_node(state: AgentState):
    """Final Brain: Consolidates all info into a ChatGPT-style response."""
    query = state["messages"][-1].content
    data = state["research_data"]
    
    system_prompt = """You are a helpful, conversational AI like ChatGPT. 
    1. If the user is just chatting, be friendly and engaging.
    2. If external data is provided, use it to be precise.
    3. Always prioritize information from the 'DOC_STUFF' if it answers the query.
    4. If the info isn't in the document or web results, use your own broad training knowledge."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {data}\n\nUser Question: {query}"}
    ]
    
    response = llm.invoke(messages)
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

# --- HELPER FUNCTIONS ---
def run_agent(user_query: str, history: list = []):
    # This wrapper allows the frontend to pass and receive history
    inputs = {
        "messages": [HumanMessage(content=user_query)],
        "chat_history": history
    }
    result = app_graph.invoke(inputs)
    return result["final_answer"]

def load_book_into_agent(full_text: str):
    if not full_text: return
    chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]
    book_memory.ingest_book(chunks)