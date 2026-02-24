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

# Path fixes for Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
sys.path.append(BASE_DIR)

from app.limiter import limiter
from app.utils.database import engine
from app.models import Base

# =========================================
# ✅ NLTK SETUP (Production Fix)
# =========================================
# Set a specific path for NLTK data so Render doesn't lose it
nltk_data_path = os.path.join(BASE_DIR, "nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

def download_nltk():
    required = ["punkt", "punkt_tab", "stopwords", "averaged_perceptron_tagger"]
    for pkg in required:
        try:
            nltk.download(pkg, download_dir=nltk_data_path, quiet=True)
        except Exception as e:
            print(f"Error downloading {pkg}: {e}")

download_nltk()

# =========================================
# ✅ DATABASE & LOGGING
# =========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Summarizer API")

# =========================================
# ✅ CORS SETUP (Added Production URL)
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://summariser-ai-frontend.onrender.com", # 👈 Add your React URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Rest of your routers and endpoints stay the same)
