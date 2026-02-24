import os
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

# Internal project imports
from app.utils.database import get_db
from app.models import User

# =========================================
# ✅ ENVIRONMENT & PATH CONFIGURATION
# =========================================
# This finds the .env file even if running from inside the 'backend' folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# =========================================
# ✅ SECURITY CONFIGURATION
# =========================================
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-if-env-fails")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Getting expiration from .env, converting to int
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(tags=["Authentication"])

# DEBUG: Ensure the key is loaded (you can remove this once it works)
print(f"DEBUG: Loaded SECRET_KEY starting with: {SECRET_KEY[:4]}...")

# =========================================
# ✅ UTILITY FUNCTIONS
# =========================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# =========================================
# ✅ SCHEMAS
# =========================================
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: Optional[str] = None
    password: Optional[str] = None 

# =========================================
# ✅ API ROUTES
# =========================================

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db.expire_all()
    clean_email = user.email.lower().strip()
    
    db_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password"
        )

    access_token = create_access_token(data={"sub": str(db_user.user_id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": {
            "user_id": db_user.user_id,
            "name": db_user.name,
            "role": db_user.role,
            "email": db_user.email
        }
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    clean_email = user.email.lower().strip()
    
    if db.query(User).filter(func.lower(User.email) == clean_email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=clean_email,
        password_hash=get_password_hash(user.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.user_id}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    clean_email = req.email.lower().strip()
    final_password = req.new_password or req.password
    
    if not final_password:
        raise HTTPException(status_code=422, detail="New password is required")

    users = db.query(User).filter(func.lower(User.email) == clean_email).order_by(User.user_id).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    
    target_user = users[-1] 
    if len(users) > 1:
        for u in users[:-1]:
            db.delete(u)
        db.commit()

    new_hash = get_password_hash(final_password)
    db.query(User).filter(User.user_id == target_user.user_id).update(
        {"password_hash": new_hash},
        synchronize_session=False
    )
    db.commit()
    db.expire_all()
    
    return {"message": "Password updated successfully"}