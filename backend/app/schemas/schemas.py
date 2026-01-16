from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    name: str
    role: str
    created_at: datetime

    # ✅ Fix for Pydantic V2 Warning
    model_config = ConfigDict(from_attributes=True)

# --- BOOK SCHEMAS ---
class BookBase(BaseModel):
    title: str
    author: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    book_id: int
    user_id: int
    file_path: str
    uploaded_at: datetime
    
    # ✅ RESTORED MISSING FIELDS (Crucial for Frontend)
    status: str
    word_count: Optional[int] = 0
    char_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

# --- SUMMARY SCHEMAS ---
class SummaryBase(BaseModel):
    summary_text: str

class SummaryCreate(SummaryBase):
    book_id: int
    
class SummaryResponse(SummaryBase):
    summary_id: int
    book_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)