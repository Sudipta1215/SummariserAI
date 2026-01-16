# backend/promote_admin.py
import sys
import os

# Add the current directory to Python path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import SessionLocal
from app.models import User

def promote_user():
    db = SessionLocal()
    
    print("--- 👑 Admin Promoter ---")
    email = input("Enter the email address you use to login: ").strip()
    
    # Find the user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"❌ Error: No user found with email '{email}'")
        return

    # Update role
    print(f"Current Role: {user.role}")
    user.role = "admin"
    db.commit()
    
    print(f"✅ Success! User '{user.name}' is now an ADMIN.")
    print("Please logout and login again to see the Admin Dashboard.")

if __name__ == "__main__":
    promote_user()