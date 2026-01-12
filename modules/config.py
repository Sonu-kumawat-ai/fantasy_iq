"""Configuration settings for Fantasy IQ application"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Mail Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Razorpay Configuration
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
    
    # CricAPI Configuration (for cricket matches)
    CRICAPI_KEY = os.getenv('CRICAPI_KEY', '')
    
    # Google Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.getenv('MONGODB_DB', 'fantasy_iq_db')
    
    @staticmethod
    def validate_config():
        """Validate configuration and print warnings"""
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            print("WARNING: Email configuration not found in environment variables!")
            print("OTP verification will not work. Set MAIL_USERNAME and MAIL_PASSWORD in .env file")
        
        if not Config.RAZORPAY_KEY_ID or not Config.RAZORPAY_KEY_SECRET:
            print("WARNING: Razorpay keys not found in environment variables!")
            print("Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env file")
            print("See .env.example for reference")
        
        if not Config.CRICAPI_KEY:
            print("WARNING: CricAPI key not found in environment variables!")
            print("Please set CRICAPI_KEY in .env file")
            print("Get your free API key from: https://www.cricapi.com/")
        
        if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here':
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY)
            print("Google Gemini API configured successfully!")
        else:
            print("WARNING: Gemini API key not found or not configured in environment variables!")
            print("Player information will use fallback data. Set GEMINI_API_KEY in .env file")
