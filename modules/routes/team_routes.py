"""Team creation and management routes for Fantasy IQ application"""
from flask import request, jsonify, session
from datetime import datetime

def register_team_routes(app, db):
    """Register all team creation and management routes"""
    
    # Get collections from db
    user_teams_collection = db['user_teams']
    players_collection = db['players']
    contests_collection = db['contests']
    matches_collection = db['matches']
    
    @app.route('/get-user-team')
    def get_user_team():
        """Get user's existing team for a contest"""
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            contest_id = request.args.get('contest_id')
            if not contest_id:
                return jsonify({'success': False, 'message': 'Contest ID required'}), 400
            
            team = user_teams_collection.find_one({
                'username': session['username'],
                'contest_id': contest_id
            }, {'_id': 0})
            
            if team:
                return jsonify({'success': True, 'team': team}), 200
            else:
                return jsonify({'success': False, 'message': 'No team found'}), 404
            
        except Exception as e:
            print(f"Error fetching user team: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/get-players')
    def get_players():
        """Get players for a match"""
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            contest_id = request.args.get('contest_id')
            if not contest_id:
                return jsonify({'success': False, 'message': 'Contest ID required'}), 400
            
            # Get contest details first
            contest = contests_collection.find_one({'match_id': contest_id}, {'_id': 0})
            if not contest:
                return jsonify({'success': False, 'message': 'Contest not found'}), 404
            
            # Get players from database ONLY
            players = list(players_collection.find(
                {'match_id': contest_id},
                {'_id': 0}
            ))
            
            # Players should already exist (fetched when user joined contest)
            if not players:
                return jsonify({
                    'success': False, 
                    'message': 'Players not available yet. Please try joining the contest again.',
                    'players': []
                }), 404
            
            return jsonify({
                'success': True,
                'players': players,
                'contest': contest
            }), 200
            
        except Exception as e:
            print(f"Error fetching players: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/save-team', methods=['POST'])
    def save_team():
        """Save or update user's team"""
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            data = request.get_json()
            contest_id = data.get('contest_id')
            selected_players = data.get('selected_players')
            captain_id = data.get('captain_id')
            vice_captain_id = data.get('vice_captain_id')
            
            if not contest_id or not selected_players or not captain_id or not vice_captain_id:
                return jsonify({'success': False, 'message': 'Invalid team data'}), 400
            
            if len(selected_players) != 11:
                return jsonify({'success': False, 'message': 'Team must have exactly 11 players'}), 400
            
            if captain_id == vice_captain_id:
                return jsonify({'success': False, 'message': 'Captain and Vice-Captain must be different'}), 400
            
            # Check if match has started
            match = matches_collection.find_one({'match_id': contest_id})
            if match:
                match_start_time = match.get('match_start_time')
                if match_start_time:
                    if isinstance(match_start_time, str):
                        match_start_time = datetime.strptime(match_start_time, '%Y-%m-%d %H:%M:%S')
                    if datetime.now() >= match_start_time:
                        return jsonify({'success': False, 'message': 'Cannot create/edit team after match has started'}), 400
            
            team_data = {
                'username': session['username'],
                'contest_id': contest_id,
                'selected_players': selected_players,
                'captain_id': captain_id,
                'vice_captain_id': vice_captain_id,
                'updated_at': datetime.now()
            }
            
            # Check if team already exists
            existing_team = user_teams_collection.find_one({
                'username': session['username'],
                'contest_id': contest_id
            })
            
            if existing_team:
                # Update existing team
                user_teams_collection.update_one(
                    {'username': session['username'], 'contest_id': contest_id},
                    {'$set': team_data}
                )
                message = 'Team updated successfully!'
            else:
                # Create new team
                team_data['created_at'] = datetime.now()
                user_teams_collection.insert_one(team_data)
                message = 'Team created successfully!'
            
            return jsonify({'success': True, 'message': message}), 200
            
        except Exception as e:
            print(f"Error saving team: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
