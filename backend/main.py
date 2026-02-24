import sys
import os
import nltk
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter
from app.utils.database import engine
from app.models import Base

# =========================================
# ✅ PATH SETUP & LOGGING
# =========================================
# This ensures imports like 'from app...' work even if started from subfolders
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
BACKEND_DIR = os.path.dirname(BASE_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================
# ✅ NLTK & DATABASE SETUP
# =========================================
def download_nltk():
    required = ["punkt", "stopwords", "punkt_tab"] # Added punkt_tab for NLTK 3.9+
    for pkg in required:
        try:
            nltk.data.find(f"tokenizers/{pkg}" if pkg.startswith("punkt") else f"corpora/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)

download_nltk()
Base.metadata.create_all(bind=engine)

# =========================================
# ✅ APP INITIALIZATION
# =========================================
app = FastAPI(title="Book Summarizer API")

# =========================================
# ✅ 1. CORS MIDDLEWARE (MUST BE FIRST)
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8501",
        "https://summariserai-frotnend.onrender.com", # Check for 'frotnend' typo in your Render URL
        "https://summariserai.onrender.com",         # Adding possible correct spelling
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ✅ 2. RATE LIMITING & STATIC FILES
# =========================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create static directory inside backend for easier Render access
static_path = os.path.join(BASE_DIR, "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# =========================================
# ✅ 3. REGISTER ALL ROUTERS
# =========================================
from app.routers import (
    auth, books, summarizer, workspaces, 
    admin, agent, audio, graph, quiz, 
    translate, translate_sarvam, 
    youtube, meeting
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"]) 
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
app.include_router(summarizer.router, prefix="/summary", tags=["Summarizer"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Analytics"]) 
app.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(agent.router, prefix="/agent", tags=["Agent"])
app.include_router(translate.router, prefix="/translate", tags=["Translation"])
app.include_router(translate_sarvam.router, prefix="/translate-sarvam", tags=["Sarvam AI"]) # Fixed prefix overlap
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(youtube.router, prefix="/youtube", tags=["YouTube Summary"])
app.include_router(meeting.router, prefix="/meeting", tags=["Meeting Summarizer"])

# =========================================
# ✅ ENDPOINTS
# =========================================
@app.get("/")
def read_root():
    return {"message": "✅ Book Summarizer API is Online", "docs": "/docs"}

@app.get("/api/dashboard/data")
def get_dashboard_data():
    return {
        "stats": {"positive_score": 1.09, "confidence": 64, "positive_count": 12, "neutral_count": 7, "negative_count": 2},
        "trend_data": [{"id": i, "val": v} for i, v in enumerate([2, 2.2, 1.8, 3.5, 4.8, 4.2, 2.5, 3.0, 3.8, 2.2, 2.5], 1)],
        "distribution": [{"name": "Neutral", "value": 64, "color": "#6366F1"}, {"name": "Positive", "value": 36, "color": "#4ADE80"}]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})
