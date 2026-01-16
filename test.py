from sqlalchemy import create_engine

# 1. Define your URL
url = "postgresql+psycopg2://postgres:1234@localhost:5432/bookdatabase"

# 2. Try to connect
try:
    engine = create_engine(url)
    connection = engine.connect()
    print("✅ Success! Connected to bookdatabase.")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")