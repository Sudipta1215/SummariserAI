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
    
    # ✅ ADMIN & STATUS FIELDS
    role = Column(String, default="user")  # 'admin' or 'user'
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    books = relationship("Book", back_populates="owner", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Workspace Relationships
    owned_workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    shared_workspaces = relationship("WorkspaceAccess", back_populates="user", cascade="all, delete-orphan")


# --- 2. BOOK MANAGEMENT ---
class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    
    # Content & Status
    extracted_text = Column(Text, nullable=True)
    status = Column(String, default="uploaded") # uploaded, processing, completed, failed
    
    # ✅ ADMIN FIELD (Content Moderation)
    is_flagged = Column(Boolean, default=False) 
    
    # ✅ ANALYTICS & EFFICIENCY TRACKING
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    processing_start = Column(DateTime(timezone=True), nullable=True)
    processing_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="books")
    summaries = relationship("Summary", back_populates="book", cascade="all, delete-orphan")


# --- 3. SUMMARY ENGINE ---
class Summary(Base):
    __tablename__ = "summaries"
    
    summary_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    
    # Generated Content
    summary_text = Column(Text, nullable=False)
    keywords = Column(String, nullable=True)
    chunk_summaries = Column(JSON, nullable=True)
    
    # ✅ STYLE ANALYTICS
    length_setting = Column(String, default="Medium") 
    style_setting = Column(String, default="Paragraph")
    is_favorite = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    book = relationship("Book", back_populates="summaries")
    user = relationship("User", back_populates="summaries")


# --- 4. AUDIT LOGS (For "Real-time Events" Feed) ---
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)   # e.g., "LOGIN", "UPLOAD", "SUMMARIZE"
    details = Column(String, nullable=True)   # e.g., "Summarized 'Biology_Notes.pdf'"
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="audit_logs")


# --- 5. COLLABORATIVE WORKSPACES ---
class Workspace(Base):
    __tablename__ = "workspaces"
    
    workspace_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    content = Column(Text, default="") 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_workspaces")
    collaborators = relationship("WorkspaceAccess", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceAccess(Base):
    __tablename__ = "workspace_access"
    
    access_id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.workspace_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    permission_level = Column(String, default="view") # 'view' or 'edit'
    
    # Relationships
    workspace = relationship("Workspace", back_populates="collaborators")
    user = relationship("User", back_populates="shared_workspaces")