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
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
BACKEND_DIR = os.path.dirname(BASE_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================
# ✅ NLTK & DATABASE SETUP
# =========================================
def download_nltk():
    required = ["punkt", "stopwords"]
    for pkg in required:
        try:
            if pkg == "punkt":
                nltk.data.find("tokenizers/punkt")
            elif pkg == "stopwords":
                nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download(pkg, quiet=True)

download_nltk()
Base.metadata.create_all(bind=engine)

# =========================================
# ✅ APP INITIALIZATION
# =========================================
app = FastAPI(title="Book Summarizer API")

# =========================================
# ✅ CORS SETUP
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8501",
        "https://summariserai-frotnend.onrender.com",  # ✅ Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ✅ STATIC FILES
# =========================================
frames_dir = os.path.join(PROJECT_ROOT, "frontend", "static")
os.makedirs(frames_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=frames_dir), name="static")

# =========================================
# ✅ RATE LIMITING
# =========================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =========================================
# ✅ REGISTER ALL ROUTERS
# =========================================
from app.routers import (
    auth, books, summarizer, workspaces, 
    admin, agent, audio, graph, quiz, 
    translate, translate_sarvam, 
    youtube, 
    meeting  # ✅ Added Meeting Router import
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
app.include_router(translate_sarvam.router, prefix="/translate", tags=["Sarvam AI"])
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(youtube.router, prefix="/youtube", tags=["YouTube Summary"])
app.include_router(meeting.router, prefix="/meeting", tags=["Meeting Summarizer"])

# =========================================
# ✅ ENDPOINTS
# =========================================
@app.get("/api/dashboard/data")
def get_dashboard_data():
    return {
        "stats": {"positive_score": 1.09, "confidence": 64, "positive_count": 12, "neutral_count": 7, "negative_count": 2},
        "trend_data": [{"id": i, "val": v} for i, v in enumerate([2, 2.2, 1.8, 3.5, 4.8, 4.2, 2.5, 3.0, 3.8, 2.2, 2.5], 1)],
        "distribution": [{"name": "Neutral", "value": 64, "color": "#6366F1"}, {"name": "Positive", "value": 36, "color": "#4ADE80"}]
    }

@app.get("/")
def read_root():
    return {"message": "✅ Book Summarizer API is Online"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})
