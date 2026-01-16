from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.utils.database import Base

# --- 1. USER MANAGEMENT ---
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # ✅ ADMIN FIELDS
    role = Column(String, default="user")  # 'admin' or 'user'
    is_active = Column(Boolean, default=True)  # To ban users
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    books = relationship("Book", back_populates="owner")
    summaries = relationship("Summary", back_populates="user")
    
    # Workspace Relationships
    owned_workspaces = relationship("Workspace", back_populates="owner")
    shared_workspaces = relationship("WorkspaceAccess", back_populates="user")

# --- 2. BOOK MANAGEMENT ---
class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    
    # Content & Status
    extracted_text = Column(Text, nullable=True)
    status = Column(String, default="uploaded") # uploaded, processing, completed, failed
    
    # ✅ ADMIN FIELD (Content Moderation)
    is_flagged = Column(Boolean, default=False) 
    
    # Analytics
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="books")
    summaries = relationship("Summary", back_populates="book")

# --- 3. SUMMARY ENGINE ---
class Summary(Base):
    __tablename__ = "summaries"
    
    summary_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    
    # Generated Content
    summary_text = Column(Text, nullable=False)
    keywords = Column(String, nullable=True)
    chunk_summaries = Column(JSON, nullable=True)
    
    # Version Control & Favorites
    length_setting = Column(String, default="Medium") 
    style_setting = Column(String, default="Paragraph")
    is_favorite = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    book = relationship("Book", back_populates="summaries")
    user = relationship("User", back_populates="summaries")

# --- 4. COLLABORATIVE WORKSPACES ---
class Workspace(Base):
    __tablename__ = "workspaces"
    
    workspace_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String, nullable=False)
    
    content = Column(Text, default="") # Stores the shared notes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_workspaces")
    collaborators = relationship("WorkspaceAccess", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceAccess(Base):
    __tablename__ = "workspace_access"
    
    access_id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.workspace_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    
    permission_level = Column(String, default="view") # 'view' or 'edit'
    
    # Relationships
    workspace = relationship("Workspace", back_populates="collaborators")
    user = relationship("User", back_populates="shared_workspaces")