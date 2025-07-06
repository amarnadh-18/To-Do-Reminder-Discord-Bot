import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            # Get MongoDB connection string from environment variable
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            if not mongo_uri:
                raise ValueError("MONGODB_URI environment variable is not set")
            self.client = MongoClient(mongo_uri)
            self.db = self.client['todo_bot']
            print("✅ Connected to MongoDB successfully!")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a specific collection from the database"""
        if self.db is None:
            raise RuntimeError("Database connection is not established.")
        return self.db[collection_name]
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed.")

# Global database instance
try:
    db = Database()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
    db = None
