from app.utils.database import SessionLocal
from app.models import User
from app.utils.auth import get_password_hash # Assuming you have this helper

def create_valid_user():
    db = SessionLocal()
    try:
        # Check if any user exists
        existing_user = db.query(User).first()
        if existing_user:
            print(f"✅ A valid user exists with ID: {existing_user.user_id}")
            return

        # Create a new Admin user
        new_user = User(
            name="Admin User",
            email="hi@gmail.com",
            hashed_password=get_password_hash("admin123"), # Change as needed
            role="admin"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✅ Created new user: {new_user.name} with ID: {new_user.user_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_valid_user()