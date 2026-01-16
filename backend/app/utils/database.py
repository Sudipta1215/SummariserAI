from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------------------------------------------
# 🔧 POSTGRESQL CONFIGURATION
# ----------------------------------------------------------------
# Ensure the password ('1234') matches what you set for your Postgres server.
# Ensure the database ('booksummarise') exists.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/booksummarise"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # Note: 'check_same_thread' is REMOVED (It is only for SQLite)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()