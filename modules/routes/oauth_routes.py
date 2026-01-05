"""OAuth authentication routes for Fantasy IQ application"""
from flask import redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import os

def register_oauth_routes(app, db):
    """Register all OAuth related routes"""
    
    # Initialize OAuth
    oauth = OAuth(app)
    
    # Configure Google OAuth
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # Get collections from db
    users_collection = db['users']
    
    @app.route('/auth/google')
    def google_login():
        """Initiate Google OAuth login"""
        redirect_uri = url_for('google_callback', _external=True)
        return google.authorize_redirect(redirect_uri)
    
    @app.route('/auth/google/callback')
    def google_callback():
        """Handle Google OAuth callback"""
        try:
            # Get OAuth token
            token = google.authorize_access_token()
            
            # Get user info from Google
            user_info = token.get('userinfo')
            
            if not user_info:
                return redirect('/login-page?error=auth_failed')
            
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0])
            google_id = user_info.get('sub')
            
            # Check if user exists
            existing_user = users_collection.find_one({'email': email})
            
            if existing_user:
                # User exists, log them in
                session['user_id'] = str(existing_user['_id'])
                session['username'] = existing_user['username']
                session['email'] = existing_user['email']
                return redirect('/')
            else:
                # Create new user with Google account
                new_user = {
                    'username': name,
                    'email': email,
                    'password': None,  # No password for OAuth users
                    'google_id': google_id,
                    'wallet': 100,  # Welcome bonus
                    'is_verified': True,  # Google accounts are pre-verified
                    'created_at': datetime.now(),
                    'auth_provider': 'google'
                }
                
                result = users_collection.insert_one(new_user)
                
                # Log the new user in
                session['user_id'] = str(result.inserted_id)
                session['username'] = name
                session['email'] = email
                
                return redirect('/')
                
        except Exception as e:
            print(f"Google OAuth error: {e}")
            return redirect('/login-page?error=auth_failed')
    
    return oauth
