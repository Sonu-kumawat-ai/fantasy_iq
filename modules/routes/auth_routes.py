"""Authentication routes for Fantasy IQ application"""
from flask import request, jsonify, session
from datetime import datetime, timedelta
from modules.auth import generate_otp, send_otp_email

def register_auth_routes(app, db, mail):
    """Register all authentication related routes"""
    
    # Get collections from db
    users_collection = db['users']
    
    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not username or not email or not password:
                return jsonify({'success': False, 'message': 'All fields are required'}), 400
            
            # Check if user already exists
            existing_user = users_collection.find_one({'$or': [{'email': email}, {'username': username}]})
            if existing_user:
                return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
            
            # Generate OTP
            otp = generate_otp()
            otp_expires = datetime.now() + timedelta(minutes=10)
            
            # Send OTP email
            if send_otp_email(mail, email, otp, username):
                # Create new user with unverified status
                new_user = {
                    'username': username,
                    'email': email,
                    'password': password,  # In production, use hashed passwords
                    'wallet': 0,
                    'otp': otp,
                    'otp_expires': otp_expires,
                    'is_verified': False,
                    'created_at': datetime.now()
                }
                
                users_collection.insert_one(new_user)
                return jsonify({
                    'success': True, 
                    'message': 'Registration successful! Please check your email for OTP verification.',
                    'email': email
                }), 201
            else:
                return jsonify({'success': False, 'message': 'Failed to send OTP email. Please try again.'}), 500
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/verify-otp', methods=['POST'])
    def verify_otp():
        try:
            data = request.get_json()
            email = data.get('email')
            otp = data.get('otp')
            
            if not email or not otp:
                return jsonify({'success': False, 'message': 'Email and OTP are required'}), 400
            
            # Find user with this email
            user = users_collection.find_one({'email': email})
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            # Check if already verified
            if user.get('is_verified', False):
                return jsonify({'success': False, 'message': 'Email already verified. Please login.'}), 400
            
            # Check if OTP matches
            if user.get('otp') != otp:
                return jsonify({'success': False, 'message': 'Invalid OTP. Please try again.'}), 400
            
            # Check if OTP is expired
            if datetime.now() > user.get('otp_expires', datetime.now()):
                return jsonify({'success': False, 'message': 'OTP has expired. Please register again.'}), 400
            
            # Verify user
            users_collection.update_one(
                {'email': email},
                {
                    '$set': {'is_verified': True},
                    '$unset': {'otp': '', 'otp_expires': ''}
                }
            )
            
            return jsonify({'success': True, 'message': 'Email verified successfully! You can now login.'}), 200
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/resend-otp', methods=['POST'])
    def resend_otp():
        try:
            data = request.get_json()
            email = data.get('email')
            
            if not email:
                return jsonify({'success': False, 'message': 'Email is required'}), 400
            
            # Find user
            user = users_collection.find_one({'email': email})
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            # Check if already verified
            if user.get('is_verified', False):
                return jsonify({'success': False, 'message': 'Email already verified. Please login.'}), 400
            
            # Generate new OTP
            otp = generate_otp()
            otp_expires = datetime.now() + timedelta(minutes=10)
            
            # Send OTP email
            if send_otp_email(mail, email, otp, user['username']):
                # Update OTP in database
                users_collection.update_one(
                    {'email': email},
                    {
                        '$set': {
                            'otp': otp,
                            'otp_expires': otp_expires
                        }
                    }
                )
                return jsonify({'success': True, 'message': 'OTP sent successfully! Please check your email.'}), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to send OTP email. Please try again.'}), 500
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'success': False, 'message': 'Email and password are required'}), 400
            
            # Check if user exists
            user = users_collection.find_one({'email': email, 'password': password})
            
            if user:
                # Check if email is verified
                if not user.get('is_verified', False):
                    return jsonify({
                        'success': False, 
                        'message': 'Please verify your email first. Check your inbox for OTP.',
                        'email': email,
                        'needsVerification': True
                    }), 403
                
                session['username'] = user['username']
                session['email'] = user['email']
                session['wallet'] = user['wallet']
                return jsonify({
                    'success': True, 
                    'message': 'Login successful!',
                    'username': user['username']
                }), 200
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/logout')
    def logout():
        session.clear()
        from flask import redirect, url_for
        return redirect(url_for('home'))
