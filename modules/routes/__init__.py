"""Routes package for Fantasy IQ application"""
from modules.routes.page_routes import register_page_routes
from modules.routes.auth_routes import register_auth_routes
from modules.routes.user_routes import register_user_routes
from modules.routes.payment_routes import register_payment_routes
from modules.routes.team_routes import register_team_routes
from modules.routes.contest_routes import register_contest_routes
from modules.routes.oauth_routes import register_oauth_routes

def register_routes(app, db, mail, razorpay_client):
    """Register all routes for the Flask application by importing from separate modules"""
    
    # Register page/template rendering routes
    register_page_routes(app, db)
    
    # Register authentication routes (login, register, OTP)
    register_auth_routes(app, db, mail)
    
    # Register OAuth routes (Google login)
    register_oauth_routes(app, db)
    
    # Register user profile and session routes
    register_user_routes(app, db)
    
    # Register payment and wallet routes
    register_payment_routes(app, db, razorpay_client)
    
    # Register team creation and management routes
    register_team_routes(app, db)
    
    # Register contest related routes
    register_contest_routes(app, db)

__all__ = [
    'register_routes',
    'register_page_routes',
    'register_auth_routes',
    'register_user_routes',
    'register_payment_routes',
    'register_team_routes',
    'register_contest_routes'
]
