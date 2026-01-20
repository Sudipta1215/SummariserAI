import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure these imports match your project structure exactly
from app.utils.database import get_db
from app.models import User

router = APIRouter(tags=["Authentication"])

# =========================
# ✅ SECURITY CONFIGURATION
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_SECRET_KEY") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- UTILITY FUNCTIONS ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# =========================
# ✅ SCHEMAS
# =========================
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str
    # ✅ Accepts EITHER 'new_password' OR 'password' to prevent frontend mismatch errors
    new_password: Optional[str] = None
    password: Optional[str] = None 

# =========================
# ✅ API ROUTES
# =========================

# 1. LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db.expire_all() # Clear cache to ensure fresh data
    clean_email = user.email.lower().strip()
    
    print(f"\n🔍 LOGIN DEBUG: Checking '{clean_email}'")
    
    # Check for user (Case Insensitive)
    db_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    
    if not db_user:
        print(f"❌ LOGIN FAIL: No user found.")
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Verify Password
    if verify_password(user.password, db_user.password_hash):
        print(f"✅ PASSWORD MATCH! Logging in User ID: {db_user.user_id}")
        return {
            "access_token": create_access_token(data={"sub": str(db_user.user_id)}), 
            "token_type": "bearer", 
            "user": {
                "user_id": db_user.user_id,
                "name": db_user.name,
                "role": db_user.role,
                "email": db_user.email
            }
        }
    else:
        print("❌ LOGIN FAIL: Password Hash Mismatch.")
        raise HTTPException(status_code=401, detail="Incorrect email or password")


# 2. REGISTER
@router.post("/register", status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    clean_email = user.email.lower().strip()
    
    existing_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if existing_user:
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


# 3. FORGOT PASSWORD (Fixes Duplicates & Frontend Mismatch)
@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    clean_email = req.email.lower().strip()
    
    # 1. Handle Hybrid Schema (Frontend might send 'password' or 'new_password')
    final_password = req.new_password or req.password
    if not final_password:
        raise HTTPException(status_code=422, detail="New password is required")

    print(f"\n🔄 RESET DEBUG: Request for '{clean_email}'")

    # 2. Find Users (Handle Duplicates)
    users = db.query(User).filter(func.lower(User.email) == clean_email).order_by(User.user_id).all()
    
    if not users:
        print("❌ RESET FAIL: Email not found.")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Keep the most recent user, delete others
    target_user = users[-1] 
    if len(users) > 1:
        print(f"⚠️ Removing {len(users)-1} duplicate accounts.")
        for u in users[:-1]:
            db.delete(u)
        db.commit()

    # 3. Force Database Update
    new_hash = get_password_hash(final_password)
    
    db.query(User).filter(User.user_id == target_user.user_id).update(
        {"password_hash": new_hash},
        synchronize_session=False
    )
    db.commit()
    db.expire_all() # Clear cache so Login sees the new password immediately
    
    print(f"✅ RESET SUCCESS: Updated User ID {target_user.user_id}")
    return {"message": "Password updated successfully"}