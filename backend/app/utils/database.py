import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------------------------------------------
# 🔧 POSTGRESQL CONFIGURATION
# ----------------------------------------------------------------

# 1. Try to get the URL from Render's environment variables.
# 2. Fall back to your local connection if no environment variable is found.
# Use os.environ.get to ensure we can handle a missing key gracefully.
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:1234@localhost/booksummarise"
)

# Render's Internal/External URLs often start with "postgres://".
# SQLAlchemy 2.0 requires "postgresql://" to recognize the driver.
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Configure the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()

# Dependency to get the database session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
