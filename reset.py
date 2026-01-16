import sys
import os
from sqlalchemy import text

# 1. Setup paths to find your modules
current_dir = os.getcwd()
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "backend"))

print("Debugging paths...")

# 2. Correct Import based on your screenshot
try:
    # Your database.py is inside the 'utils' folder
    from backend.app.utils.database import engine
    print("✅ Found engine in: backend.app.utils.database")
except ImportError:
    try:
        # Fallback: Try importing as if 'app' is the root
        from app.utils.database import engine
        print("✅ Found engine in: app.utils.database")
    except ImportError as e:
        print("\n❌ CRITICAL ERROR: Could not find database.py")
        print(f"Python Error: {e}")
        print("Please check if 'database.py' defines a variable named 'engine'.")
        sys.exit(1)

def add_column():
    print("\nAttempting to modify database...")
    try:
        with engine.connect() as conn:
            # The SQL command to add the missing column
            conn.execute(text("ALTER TABLE summaries ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE;"))
            conn.commit()
            print("✅ SUCCESS! The 'is_favorite' column was added.")
    except Exception as e:
        print(f"❌ Database Error: {e}")
        print("Note: If the error says 'column already exists', you are already good to go!")

if __name__ == "__main__":
    add_column()