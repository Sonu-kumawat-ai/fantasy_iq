from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
import secrets
import google.generativeai as genai

# Import all our custom modules
from modules.config import Config
from modules.database import init_database
from modules.payment import init_razorpay
from modules.match import cleanup_expired_matches
from modules.contest import sync_matches_and_contests
from modules.routes import register_routes

# Validate configuration
Config.validate_config()

# Configure Gemini API if available
if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here':
    genai.configure(api_key=Config.GEMINI_API_KEY)
    print("Google Gemini API configured successfully!")
else:
    print("WARNING: Gemini API key not found or not configured!")
    print("Player information will use fallback data. Set GEMINI_API_KEY in .env file")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
CORS(app)

# Configure OAuth settings
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET', '')

# Configure Flask-Mail
app.config['MAIL_SERVER'] = Config.MAIL_SERVER
app.config['MAIL_PORT'] = Config.MAIL_PORT
app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = Config.MAIL_DEFAULT_SENDER

mail = Mail(app)

# Initialize database connection
db, collections = init_database()
print(f"Database initialized with {len(collections)} collections")

# Initialize Razorpay client
razorpay_client = init_razorpay()

# Register all routes
register_routes(app, db, mail, razorpay_client)
print("All routes registered successfully")

# Initialize Background Scheduler
scheduler = BackgroundScheduler()

# Fetch matches every 6 hours
scheduler.add_job(
    func=lambda: sync_matches_and_contests(db), 
    trigger="interval", 
    hours=6,
    id='sync_matches',
    name='Sync matches and contests every 6 hours'
)

# Cleanup expired matches every 2 hours
scheduler.add_job(
    func=lambda: cleanup_expired_matches(db), 
    trigger="interval", 
    hours=2,
    id='cleanup_matches',
    name='Cleanup expired matches every 2 hours'
)

scheduler.start()
print("Background scheduler started:")
print("  - Match sync: every 6 hours")
print("  - Cleanup: every 2 hours")

# Shutdown scheduler when app exits
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # Run cleanup once on startup to clear any expired matches
    print("\n=== STARTUP INITIALIZATION ===")
    print("Running initial cleanup...")
    cleanup_expired_matches(db)
    
    # Sync matches on startup (will run again every 6 hours)
    print("\nFetching latest matches and creating contests...")
    sync_result = sync_matches_and_contests(db)
    print(f"Match sync completed: {'Success' if sync_result else 'Failed'}")
    
    # Get port and debug from environment
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Flask app on port {port} (debug={debug})")
    app.run(debug=debug, port=port)
