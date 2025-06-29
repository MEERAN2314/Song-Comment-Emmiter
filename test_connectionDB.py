from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

try:
    client = MongoClient(
        os.getenv("MONGODB_URI"),
        serverSelectionTimeoutMS=5000
    )
    # Force a connection test
    client.server_info()
    print("✅ Successfully connected to MongoDB Atlas!")
    print(f"Database: {client[os.getenv('DB_NAME')].name}")
except Exception as e:
    print(f"❌ Connection failed: {e}")