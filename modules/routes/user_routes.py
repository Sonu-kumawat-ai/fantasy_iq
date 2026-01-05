"""User profile and session routes for Fantasy IQ application"""
from flask import request, jsonify, session
from datetime import datetime

def register_user_routes(app, db):
    """Register all user profile and session related routes"""
    
    # Get collections from db
    users_collection = db['users']
    
    @app.route('/check-session')
    def check_session():
        if 'username' in session:
            # Get user data from database
            user = users_collection.find_one({'username': session['username']})
            if user:
                return jsonify({
                    'logged_in': True,
                    'username': user['username'],
                    'email': user['email'],
                    'wallet': user['wallet'],
                    'created_at': user.get('created_at', '').isoformat() if user.get('created_at') else None
                })
        return jsonify({'logged_in': False})

    @app.route('/update-profile', methods=['POST'])
    def update_profile():
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            data = request.get_json()
            new_username = data.get('username', '').strip()
            new_email = data.get('email', '').strip()
            
            if not new_username or not new_email:
                return jsonify({'success': False, 'message': 'Username and email are required'}), 400
            
            # Check if new username already exists (if username is being changed)
            current_user = users_collection.find_one({'username': session['username']})
            if new_username != current_user['username']:
                existing_username = users_collection.find_one({'username': new_username})
                if existing_username:
                    return jsonify({'success': False, 'message': 'Username already taken'}), 400
            
            # Check if new email already exists (if email is being changed)
            if new_email != current_user['email']:
                existing_email = users_collection.find_one({'email': new_email})
                if existing_email:
                    return jsonify({'success': False, 'message': 'Email already registered'}), 400
            
            # Update user in database
            users_collection.update_one(
                {'username': session['username']},
                {
                    '$set': {
                        'username': new_username,
                        'email': new_email,
                        'updated_at': datetime.now()
                    }
                }
            )
            
            # Update session with new username
            session['username'] = new_username
            session['email'] = new_email
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'username': new_username,
                'email': new_email
            }), 200
            
        except Exception as e:
            print(f"Error in update_profile: {str(e)}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
