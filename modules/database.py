"""Database connection and collections for Fantasy IQ application"""
from pymongo import MongoClient
from modules.config import Config

def init_database():
    """Initialize MongoDB connection and return database and collections"""
    try:
        client = MongoClient(Config.MONGODB_URI)
        db = client[Config.MONGODB_DB]
        
        # Define collections
        collections = {
            'users': db['users'],
            'transactions': db['transactions'],
            'matches': db['matches'],
            'contests': db['contests'],
            'joined_contests': db['joined_contests'],
            'players': db['players'],
            'user_teams': db['user_teams']
        }
        
        print("MongoDB connected successfully!")
        return db, collections
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        raise
