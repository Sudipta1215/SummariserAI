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
# ✅ IMPORT ALL ROUTERS
# =========================================
from app.routers import (
    auth,
    books,
    summarizer,
    workspaces,            # ✅ Workspaces
    admin,
    agent,                 # ✅ Agent
    audio,                 # ✅ Audio
    graph,                 # ✅ Knowledge Graph
    quiz,                  # ✅ Quiz
    translate,             # ✅ Google Translate
    translate_sarvam       # ✅ Sarvam AI
)

# =========================================
# PATH SETUP & LOGGING
# =========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.append(BACKEND_DIR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_nltk():
    required = ["punkt", "stopwords"]
    for pkg in required:
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)
download_nltk()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Summarizer API")

# Mount Static Files
frames_dir = os.path.join(PROJECT_ROOT, "frontend", "static")
if not os.path.exists(frames_dir):
    os.makedirs(frames_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=frames_dir), name="static")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})

# =========================================
# ✅ ROUTER REGISTRATION
# =========================================
app.include_router(auth.router, tags=["Auth"]) 
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"]) # ✅ Registered!
app.include_router(summarizer.router, prefix="/summary", tags=["Summarizer"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(agent.router, prefix="/agent", tags=["Agent"])
app.include_router(translate.router, prefix="/translate", tags=["Translation"])
app.include_router(translate_sarvam.router, prefix="/translate", tags=["Sarvam AI"])

@app.get("/")
def read_root():
    return {"message": "✅ Book Summarizer API is Online"}