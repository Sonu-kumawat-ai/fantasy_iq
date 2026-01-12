"""Admin routes for Fantasy IQ application"""
from flask import render_template, session, redirect, url_for, jsonify, request
from functools import wraps

# Admin email whitelist
ADMIN_EMAIL = 'kumawatsonu086@gmail.com'

def admin_required(f):
    """Decorator to restrict access to admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'username' not in session:
            return redirect(url_for('login_page'))
        
        # Get user's email from database
        db = kwargs.get('db') or args[0] if args else None
        if not db:
            return jsonify({'success': False, 'message': 'Database error'}), 500
        
        users_collection = db['users']
        user = users_collection.find_one({'username': session.get('username')})
        
        # Check if user email matches admin email
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def register_admin_routes(app, db):
    """Register all admin routes"""
    
    users_collection = db['users']
    matches_collection = db['matches']
    contests_collection = db['contests']
    joined_contests_collection = db['joined_contests']
    transactions_collection = db['transactions']
    
    @app.route('/admin')
    def admin_dashboard():
        """Admin dashboard page"""
        # Check if user is logged in
        if 'username' not in session:
            return redirect(url_for('login_page'))
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return redirect(url_for('home'))
        
        return render_template('admin.html')
    
    @app.route('/api/admin/stats')
    def admin_stats():
        """Get admin dashboard statistics"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            total_users = users_collection.count_documents({})
            total_contests = contests_collection.count_documents({})
            total_matches = matches_collection.count_documents({})
            
            # Calculate total revenue from entry fees
            total_revenue = 0
            all_joined = list(joined_contests_collection.find())
            for entry in all_joined:
                contest = contests_collection.find_one({'match_id': entry.get('contest_id')})
                if contest:
                    total_revenue += contest.get('entry_fee', 0)
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'total_contests': total_contests,
                    'total_matches': total_matches,
                    'total_revenue': total_revenue
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/users')
    def admin_users():
        """Get all users"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            users = list(users_collection.find({}, {'_id': 0, 'password': 0}))
            
            # Convert datetime to string
            for u in users:
                if 'created_at' in u:
                    u['created_at'] = str(u['created_at'])
            
            return jsonify({
                'success': True,
                'users': users
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/matches')
    def admin_matches():
        """Get all matches"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            matches = list(matches_collection.find({}, {'_id': 0}))
            
            # Convert datetime to string
            for match in matches:
                if 'created_at' in match:
                    match['created_at'] = str(match['created_at'])
                if 'match_start_time' in match:
                    match['match_start_time'] = str(match['match_start_time'])
                if 'match_end_time' in match:
                    match['match_end_time'] = str(match['match_end_time'])
            
            return jsonify({
                'success': True,
                'matches': matches
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/contests')
    def admin_contests():
        """Get all contests"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            contests = list(contests_collection.find({}, {'_id': 0}))
            
            # Get match names for contests
            for contest in contests:
                match = matches_collection.find_one({'match_id': contest.get('match_id')})
                contest['match_name'] = match.get('name', 'N/A') if match else 'N/A'
                
                if 'created_at' in contest:
                    contest['created_at'] = str(contest['created_at'])
            
            return jsonify({
                'success': True,
                'contests': contests
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/user/<username>', methods=['DELETE'])
    def admin_delete_user(username):
        """Delete a user"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            result = users_collection.delete_one({'username': username})
            
            if result.deleted_count > 0:
                return jsonify({'success': True, 'message': 'User deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'User not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/match/<match_id>', methods=['DELETE'])
    def admin_delete_match(match_id):
        """Delete a match and its related data"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            # Delete match
            result = matches_collection.delete_one({'match_id': match_id})
            
            # Delete related contests
            contests_collection.delete_many({'match_id': match_id})
            
            # Delete related joined contests
            joined_contests_collection.delete_many({'contest_id': match_id})
            
            if result.deleted_count > 0:
                return jsonify({'success': True, 'message': 'Match and related data deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'Match not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/contest/<contest_id>', methods=['DELETE'])
    def admin_delete_contest(contest_id):
        """Delete a contest"""
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        # Check if user is admin
        user = users_collection.find_one({'username': session.get('username')})
        if not user or user.get('email') != ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            result = contests_collection.delete_one({'match_id': contest_id})
            
            # Delete related joined contests
            joined_contests_collection.delete_many({'contest_id': contest_id})
            
            if result.deleted_count > 0:
                return jsonify({'success': True, 'message': 'Contest deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'Contest not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
