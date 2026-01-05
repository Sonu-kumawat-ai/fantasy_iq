"""Contest related routes for Fantasy IQ application"""
from flask import request, jsonify, session
from datetime import datetime
from modules.player import fetch_players_for_match, fetch_football_players_for_match
from modules.contest import sync_matches_and_contests
from modules.match import cleanup_expired_matches

def register_contest_routes(app, db):
    """Register all contest related routes"""
    
    # Get collections from db
    contests_collection = db['contests']
    joined_contests_collection = db['joined_contests']
    players_collection = db['players']
    matches_collection = db['matches']
    transactions_collection = db['transactions']
    users_collection = db['users']
    
    @app.route('/sync-matches', methods=['POST'])
    def sync_matches():
        """Manually trigger match and contest sync (admin endpoint)"""
        try:
            result = sync_matches_and_contests(db)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/get-contests', methods=['GET'])
    def get_contests():
        """Get contests from database, optionally filtered by sport type"""
        try:
            sport_type = request.args.get('sport', 'all')
            
            # Build query based on sport type
            if sport_type == 'all':
                # Get all contests regardless of sport type
                query = {'status': 'open'}
                limit = 50  # Show more contests when displaying all sports
            else:
                # Get contests for specific sport
                query = {'sport_type': sport_type, 'status': 'open'}
                limit = 20  # Show fewer when filtering by specific sport
            
            # Get contests, sorted by match start time (earliest first)
            contests = list(contests_collection.find(
                query,
                {'_id': 0}
            ).sort('match_start_time', 1).limit(limit))  # 1 for ascending order (earliest first)
            
            # Convert datetime objects to strings for JSON serialization
            for contest in contests:
                if 'created_at' in contest and isinstance(contest['created_at'], datetime):
                    contest['created_at'] = contest['created_at'].isoformat()
                if 'match_start_time' in contest and isinstance(contest['match_start_time'], datetime):
                    contest['match_start_time'] = contest['match_start_time'].isoformat()
                if 'match_end_time' in contest and isinstance(contest['match_end_time'], datetime):
                    contest['match_end_time'] = contest['match_end_time'].isoformat()
            
            return jsonify({
                'success': True,
                'contests': contests,
                'count': len(contests),
                'sport': sport_type
            }), 200
            
        except Exception as e:
            print(f"Error in get_contests: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/pay-entry-fee', methods=['POST'])
    def pay_entry_fee():
        """Process entry fee payment from wallet"""
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            data = request.get_json()
            contest_id = data.get('contest_id')
            entry_fee = data.get('entry_fee')
            
            if not contest_id or entry_fee is None:
                return jsonify({'success': False, 'message': 'Invalid request'}), 400
            
            # Check if user has already joined this contest
            existing_entry = joined_contests_collection.find_one({
                'username': session['username'],
                'contest_id': contest_id
            })
            
            if existing_entry:
                return jsonify({
                    'success': False,
                    'message': 'You have already joined this contest!',
                    'already_joined': True
                }), 400
            
            # Get contest details first to check match start time
            contest = contests_collection.find_one({'match_id': contest_id})
            if not contest:
                return jsonify({'success': False, 'message': 'Contest not found'}), 404
            
            # Check if match has already started
            match_start_time = contest.get('match_start_time')
            if match_start_time:
                if isinstance(match_start_time, str):
                    match_start_time = datetime.fromisoformat(match_start_time.replace('Z', '+00:00'))
                
                current_time = datetime.now()
                if current_time >= match_start_time:
                    return jsonify({
                        'success': False, 
                        'message': 'Contest closed! Match has already started.',
                        'match_started': True
                    }), 400
            
            # Get user's current wallet balance
            user = users_collection.find_one({'username': session['username']})
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            current_balance = user.get('wallet', 0)
            
            # Check if user has sufficient balance
            if current_balance < entry_fee:
                return jsonify({
                    'success': False, 
                    'message': 'Insufficient balance',
                    'current_balance': current_balance,
                    'required': entry_fee
                }), 400
            
            # Deduct entry fee from wallet
            new_balance = current_balance - entry_fee
            users_collection.update_one(
                {'username': session['username']},
                {'$set': {'wallet': new_balance}}
            )
            
            # Update session
            session['wallet'] = new_balance
            
            # Record transaction
            transaction = {
                'username': session['username'],
                'email': session['email'],
                'type': 'debit',
                'amount': entry_fee,
                'status': 'success',
                'description': f'Entry fee for contest {contest_id}',
                'contest_id': contest_id,
                'method': 'Wallet',
                'created_at': datetime.now()
            }
            transactions_collection.insert_one(transaction)
            
            # Record joined contest (contest details already fetched earlier)
            joined_contest = {
                'username': session['username'],
                'email': session['email'],
                'contest_id': contest_id,
                'contest_title': contest.get('title') if contest else 'Unknown Contest',
                'entry_fee': entry_fee,
                'prize_pool': contest.get('prize_pool') if contest else 0,
                'badge': contest.get('badge') if contest else 'Joined',
                'status': 'active',
                'joined_at': datetime.now()
            }
            
            # Create joined_contests collection if not exists and insert
            joined_contests_collection.insert_one(joined_contest)
            
            # Fetch and store players for this match
            teams = contest.get('teams', [])
            sport_type = contest.get('sport_type', 'cricket')  # Default to cricket for backwards compatibility
            
            if len(teams) >= 2:
                team1_name = teams[0]
                team2_name = teams[1]
                
                # Check if players already exist for this match
                existing_players = players_collection.count_documents({'match_id': contest_id, 'sport_type': sport_type})
                
                if existing_players == 0:
                    # Fetch players from API based on sport type
                    if sport_type == 'football':
                        players = fetch_football_players_for_match(db, contest_id, team1_name, team2_name)
                    else:
                        players = fetch_players_for_match(db, contest_id, team1_name, team2_name)
                    
                    # Store players in database
                    if players:
                        players_collection.insert_many(players)
            
            return jsonify({
                'success': True,
                'message': 'Payment successful',
                'new_balance': new_balance,
                'redirect_url': f'/create-team?contest_id={contest_id}'
            }), 200
            
        except Exception as e:
            print(f"Error in pay_entry_fee: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/get-joined-contests', methods=['GET'])
    def get_joined_contests():
        """Get all contests joined by the user"""
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            # Get all joined contests for the user
            joined_contests = list(joined_contests_collection.find(
                {'username': session['username']},
                {'_id': 0}
            ).sort('joined_at', -1))
            
            # Convert datetime to string
            for contest in joined_contests:
                if 'joined_at' in contest and isinstance(contest['joined_at'], datetime):
                    contest['joined_at'] = contest['joined_at'].isoformat()
            
            # Calculate stats
            total_joined = len(joined_contests)
            total_spent = sum(c.get('entry_fee', 0) for c in joined_contests)
            live_contests = sum(1 for c in joined_contests if c.get('status') == 'active')
            
            return jsonify({
                'success': True,
                'contests': joined_contests,
                'stats': {
                    'total_joined': total_joined,
                    'total_spent': total_spent,
                    'live_contests': live_contests
                }
            }), 200
            
        except Exception as e:
            print(f"Error in get_joined_contests: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/get-matches', methods=['GET'])
    def get_matches():
        """Get matches from database"""
        try:
            sport_type = request.args.get('sport', 'cricket')
            
            # Get matches for the specified sport
            matches = list(matches_collection.find(
                {'sport_type': sport_type},
                {'_id': 0}
            ).sort('date', 1).limit(10))
            
            # Convert datetime objects to strings
            for match in matches:
                if 'created_at' in match and isinstance(match['created_at'], datetime):
                    match['created_at'] = match['created_at'].isoformat()
                if 'fetched_at' in match and isinstance(match['fetched_at'], datetime):
                    match['fetched_at'] = match['fetched_at'].isoformat()
                if 'match_start_time' in match and isinstance(match['match_start_time'], datetime):
                    match['match_start_time'] = match['match_start_time'].isoformat()
                if 'match_end_time' in match and isinstance(match['match_end_time'], datetime):
                    match['match_end_time'] = match['match_end_time'].isoformat()
            
            return jsonify({
                'success': True,
                'matches': matches,
                'count': len(matches)
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/get-contest-details', methods=['GET'])
    def get_contest_details():
        """Get single contest details by match_id"""
        try:
            contest_id = request.args.get('id')
            
            if not contest_id:
                return jsonify({'success': False, 'message': 'Contest ID required'}), 400
            
            # Get contest from database
            contest = contests_collection.find_one(
                {'match_id': contest_id},
                {'_id': 0}
            )
            
            if not contest:
                return jsonify({'success': False, 'message': 'Contest not found'}), 404
            
            # Convert datetime objects to strings
            if 'created_at' in contest and isinstance(contest['created_at'], datetime):
                contest['created_at'] = contest['created_at'].isoformat()
            if 'match_start_time' in contest and isinstance(contest['match_start_time'], datetime):
                contest['match_start_time'] = contest['match_start_time'].isoformat()
            if 'match_end_time' in contest and isinstance(contest['match_end_time'], datetime):
                contest['match_end_time'] = contest['match_end_time'].isoformat()
            
            return jsonify({
                'success': True,
                'contest': contest
            }), 200
            
        except Exception as e:
            print(f"Error in get_contest_details: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/manual-cleanup')
    def manual_cleanup():
        """Manually trigger cleanup (for testing)"""
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        try:
            cleanup_expired_matches(db)
            return jsonify({'success': True, 'message': 'Cleanup triggered successfully'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
