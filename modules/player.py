"""Player fetching and management functions for Fantasy IQ application"""
import requests
import random
import traceback
from datetime import datetime
import google.generativeai as genai
from modules.config import Config

def fetch_players_for_match(db, match_id, team1_name, team2_name):
    """Fetch players for both teams from SportMonks API"""
    try:
        # First check if players already exist in database
        players_collection = db['players']
        existing_players = list(players_collection.find({'match_id': match_id}, {'_id': 0}))
        
        if existing_players and len(existing_players) >= 22:
            print(f"Using existing {len(existing_players)} players from database for match {match_id}")
            return existing_players
        
        if not Config.SPORTMONKS_API_KEY:
            print("SportMonks API key not configured. Cannot fetch players.")
            return []
        
        players = []
        player_id_map = {}  # Track player IDs to detect duplicates
        
        # Fetch lineup data from SportMonks API for this fixture
        url = f"https://cricket.sportmonks.com/api/v2.0/fixtures/{match_id}"
        params = {
            'api_token': Config.SPORTMONKS_API_KEY,
            'include': 'lineup,batting.batsman,bowling.bowler,localteam,visitorteam'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                print(f"No fixture data found for match {match_id}")
                # Get match date from database if available
                match = db['matches'].find_one({'match_id': match_id})
                match_date = match.get('date') if match else None
                # Generate dummy players if API doesn't have lineup data
                return generate_dummy_players(match_id, team1_name, team2_name, 'cricket', match_date)
            
            fixture = data.get('data', {})
            # Extract match date from fixture
            starting_at = fixture.get('starting_at', '')
            match_date = starting_at.split('T')[0] if 'T' in starting_at else starting_at.split(' ')[0] if starting_at else None
            
            lineup = fixture.get('lineup', [])
            batting = fixture.get('batting', [])
            bowling = fixture.get('bowling', [])
            
            # For upcoming matches, lineup data typically won't have player details
            # SportMonks cricket API provides lineup mainly for completed/live matches
            if not lineup or len(lineup) == 0:
                print(f"No lineup data available for upcoming match {match_id}. Generating dummy players.")
                return generate_dummy_players(match_id, team1_name, team2_name, 'cricket', match_date)
            
            # Check if lineup has actual player data (it's usually empty for future matches)
            has_player_data = any(isinstance(item, dict) and item.get('player') for item in lineup)
            
            if not has_player_data:
                print(f"Lineup exists but no player details for upcoming match {match_id}. Generating dummy players.")
                return generate_dummy_players(match_id, team1_name, team2_name, 'cricket', match_date)
            
            # Process lineup data
            for team_idx, player_data in enumerate(lineup):
                try:
                    player_obj = player_data.get('player', {})
                    if not player_obj:
                        continue
                    
                    original_player_id = str(player_obj.get('id', ''))
                    player_name = player_obj.get('fullname', player_obj.get('firstname', '') + ' ' + player_obj.get('lastname', ''))
                    
                    if not original_player_id or not player_name:
                        continue
                    
                    # Determine team name
                    team_id = player_data.get('team_id')
                    localteam = fixture.get('localteam', {})
                    visitorteam = fixture.get('visitorteam', {})
                    
                    if team_id == localteam.get('id'):
                        team = team1_name
                    elif team_id == visitorteam.get('id'):
                        team = team2_name
                    else:
                        team = team1_name if team_idx < 11 else team2_name
                    
                    # Check for duplicate player ID and generate unique one if needed
                    if original_player_id in player_id_map:
                        unique_player_id = f"{original_player_id}_T{team_idx}"
                        print(f"Duplicate player ID detected: {original_player_id}. Generated unique ID: {unique_player_id}")
                    else:
                        unique_player_id = original_player_id
                        player_id_map[original_player_id] = True
                    
                    # Determine role from position
                    position = player_obj.get('position', {}).get('name', '') if isinstance(player_obj.get('position'), dict) else ''
                    role = determine_cricket_role(position)
                    
                    player_info = {
                        'player_id': unique_player_id,
                        'original_player_id': original_player_id,
                        'name': player_name,
                        'team': team,
                        'position': position,
                        'nationality': player_obj.get('country', {}).get('name', '') if isinstance(player_obj.get('country'), dict) else '',
                        'birth_date': player_obj.get('dateofbirth', ''),
                        'role': role,
                        'match_id': match_id,
                        'created_at': datetime.now()
                    }
                    players.append(player_info)
                    
                except Exception as e:
                    print(f"Error parsing player data: {e}")
                    continue
            
            # If we have players, assign roles based on distribution
            if players:
                # Split players by team
                team1_players = [p for p in players if p['team'] == team1_name]
                team2_players = [p for p in players if p['team'] == team2_name]
                
                assign_roles_by_distribution(team1_players)
                assign_roles_by_distribution(team2_players)
                
                return players
            else:
                # No players found, generate dummy ones
                return generate_dummy_players(match_id, team1_name, team2_name, 'cricket', match_date)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from SportMonks API: {e}")
            # Get match date from database if available
            match = db['matches'].find_one({'match_id': match_id})
            match_date = match.get('date') if match else None
            return generate_dummy_players(match_id, team1_name, team2_name, 'cricket', match_date)
        
    except Exception as e:
        print(f"Error in fetch_players_for_match: {e}")
        import traceback
        traceback.print_exc()
        # Get match date from database if available
        match = db['matches'].find_one({'match_id': match_id})
        match_date = match.get('date') if match else None
        return generate_dummy_players(match_id, team1_name, team2_name, 'cricket', match_date)

def fetch_football_players_for_match(db, match_id, team1_name, team2_name):
    """Fetch players for both football teams from SportMonks API"""
    try:
        # First check if players already exist in database
        players_collection = db['players']
        existing_players = list(players_collection.find({'match_id': match_id}, {'_id': 0}))
        
        if existing_players and len(existing_players) >= 22:
            print(f"Using existing {len(existing_players)} football players from database for match {match_id}")
            return existing_players
        
        if not Config.SPORTMONKS_API_KEY:
            print("SportMonks API key not configured. Cannot fetch players.")
            return []
        
        players = []
        player_id_map = {}  # Track player IDs to detect duplicates
        
        # Fetch lineup data from SportMonks Football API for this fixture
        url = f"https://soccer.sportmonks.com/api/v2.0/fixtures/{match_id}"
        params = {
            'api_token': Config.SPORTMONKS_API_KEY,
            'include': 'lineup,localTeam,visitorTeam'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                print(f"No fixture data found for football match {match_id}")
                # Get match date from database if available
                match = db['matches'].find_one({'match_id': match_id})
                match_date = match.get('date') if match else None
                return generate_dummy_football_players(match_id, team1_name, team2_name, match_date)
            
            fixture = data.get('data', {})
            # Extract match date from fixture
            starting_at = fixture.get('starting_at', '') or fixture.get('time', {}).get('starting_at', {}).get('date_time', '')
            match_date = starting_at.split('T')[0] if 'T' in starting_at else starting_at.split(' ')[0] if starting_at else None
            
            lineup = fixture.get('lineup', {}).get('data', []) if isinstance(fixture.get('lineup'), dict) else []
            
            if not lineup or len(lineup) == 0:
                print(f"No lineup data available for football match {match_id}. Generating dummy players.")
                return generate_dummy_football_players(match_id, team1_name, team2_name, match_date)
            
            # Process lineup data
            for team_idx, player_data in enumerate(lineup):
                try:
                    player_obj = player_data.get('player', {}) if isinstance(player_data.get('player'), dict) else {}
                    if not player_obj:
                        continue
                    
                    original_player_id = str(player_obj.get('player_id', '') or player_obj.get('id', ''))
                    player_name = player_obj.get('display_name', '') or player_obj.get('fullname', '') or player_obj.get('common_name', '')
                    
                    if not original_player_id or not player_name:
                        continue
                    
                    # Determine team name
                    team_id = player_data.get('team_id')
                    localteam = fixture.get('localTeam', {}).get('data', {}) if isinstance(fixture.get('localTeam'), dict) else {}
                    visitorteam = fixture.get('visitorTeam', {}).get('data', {}) if isinstance(fixture.get('visitorTeam'), dict) else {}
                    
                    if team_id == localteam.get('id'):
                        team = team1_name
                    elif team_id == visitorteam.get('id'):
                        team = team2_name
                    else:
                        team = team1_name if team_idx < 11 else team2_name
                    
                    # Check for duplicate player ID
                    if original_player_id in player_id_map:
                        unique_player_id = f"{original_player_id}_T{team_idx}"
                        print(f"Duplicate player ID detected: {original_player_id}. Generated unique ID: {unique_player_id}")
                    else:
                        unique_player_id = original_player_id
                        player_id_map[original_player_id] = True
                    
                    # Determine position/role
                    position_name = player_data.get('position', '') or player_obj.get('position', {}).get('name', '') if isinstance(player_obj.get('position'), dict) else ''
                    role = determine_football_role(position_name)
                    
                    player_info = {
                        'player_id': unique_player_id,
                        'original_player_id': original_player_id,
                        'name': player_name,
                        'team': team,
                        'position': position_name,
                        'nationality': player_obj.get('nationality', ''),
                        'birth_date': player_obj.get('birthdate', ''),
                        'role': role,
                        'match_id': match_id,
                        'created_at': datetime.now()
                    }
                    players.append(player_info)
                    
                except Exception as e:
                    print(f"Error parsing football player data: {e}")
                    continue
            
            # If we have players, return them
            if players:
                return players
            else:
                return generate_dummy_football_players(match_id, team1_name, team2_name, match_date)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from SportMonks Football API: {e}")
            # Get match date from database if available
            match = db['matches'].find_one({'match_id': match_id})
            match_date = match.get('date') if match else None
            return generate_dummy_football_players(match_id, team1_name, team2_name, match_date)
        
    except Exception as e:
        print(f"Error in fetch_football_players_for_match: {e}")
        import traceback
        traceback.print_exc()
        # Get match date from database if available
        match = db['matches'].find_one({'match_id': match_id})
        match_date = match.get('date') if match else None
        return generate_dummy_football_players(match_id, team1_name, team2_name, match_date)

def fetch_players_from_gemini_single_request(team1_name, team2_name, sport_type='cricket', match_date=None):
    """Fetch all 22 players (both teams) in a single Gemini API request to avoid quota issues"""
    try:
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your_gemini_api_key_here':
            return None
        
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Format match date for the prompt
        date_info = f" on {match_date}" if match_date else ""
        
        if sport_type == 'football':
            prompt = f"""List exactly 11 starting players (NO substitutes) from {team1_name} and 11 starting players (NO substitutes) from {team2_name} football teams for their match{date_info}.

IMPORTANT: 
- Provide the starting XI lineup for the match{date_info} if available
- If lineup for this specific match is not available, use the starting XI from their most recent previous match
- DO NOT include substitute players, only the 11 starting players
- Format each line as: TeamName|PlayerName|Position
- Position must be one of: Goalkeeper, Defender, Midfielder, Forward

Example:
{team1_name}|Player Name|Goalkeeper

Keep response minimal, exactly 22 lines total (11 per team)."""
        else:
            prompt = f"""List exactly 11 players from {team1_name} and 11 players from {team2_name} cricket teams for their match{date_info}.

IMPORTANT:
- Provide the playing XI for the match{date_info} if available
- If lineup for this specific match is not available, use the playing XI from their most recent previous match
- Format each line as: TeamName|PlayerName|Role
- Role must be one of: Batsman, Bowler, All-Rounder, Wicket-Keeper

Example:
{team1_name}|Player Name|Batsman

Keep response minimal, exactly 22 lines total (11 per team)."""
        
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return None
        
        # Parse the response
        players_by_team = {team1_name: [], team2_name: []}
        lines = response.text.strip().split('\n')
        
        for line in lines[:22]:  # Limit to 22 players
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('*'):
                continue
            
            # Remove numbering like "1.", "2." etc
            line = line.lstrip('0123456789.').strip()
            line = line.lstrip('*-•').strip()
            
            # Split by |
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    team = parts[0].strip()
                    name = parts[1].strip()
                    role = parts[2].strip().strip('()')
                    
                    # Match team name (case-insensitive, partial match)
                    matched_team = None
                    for team_key in [team1_name, team2_name]:
                        if team.lower() in team_key.lower() or team_key.lower() in team.lower():
                            matched_team = team_key
                            break
                    
                    if matched_team and name and role:
                        players_by_team[matched_team].append({'name': name, 'role': role})
        
        return players_by_team if any(players_by_team.values()) else None
        
    except Exception as e:
        print(f"Error fetching players from Gemini: {e}")
        return None

def generate_dummy_players(match_id, team1_name, team2_name, sport_type='cricket', match_date=None):
    """Generate players using Gemini API or fallback to dummy data"""
    import random
    
    players = []
    
    # Determine roles based on sport type
    if sport_type == 'football':
        default_roles = ['Goalkeeper'] * 1 + ['Defender'] * 4 + ['Midfielder'] * 4 + ['Forward'] * 2
    else:
        default_roles = ['Batsman'] * 4 + ['Bowler'] * 4 + ['All-Rounder'] * 2 + ['Wicket-Keeper'] * 1
    
    # Try to fetch all players in a single Gemini request with match date
    gemini_data = fetch_players_from_gemini_single_request(team1_name, team2_name, sport_type, match_date)
    
    for team_idx, team_name in enumerate([team1_name, team2_name]):
        team_roles = default_roles.copy()
        random.shuffle(team_roles)
        
        # Get Gemini players for this team if available
        gemini_players = gemini_data.get(team_name, []) if gemini_data else []
        
        for i in range(11):
            player_id = f"{match_id}_T{team_idx}_P{i}"
            
            # Use Gemini data if available, otherwise use dummy names
            if gemini_players and i < len(gemini_players):
                player_name = gemini_players[i]['name']
                player_role = gemini_players[i]['role']
            else:
                player_name = f"Player {i+1}"
                player_role = team_roles[i]
            
            player_info = {
                'player_id': player_id,
                'original_player_id': player_id,
                'name': player_name,
                'team': team_name,
                'position': player_role,
                'nationality': '',
                'birth_date': '',
                'role': player_role,
                'match_id': match_id,
                'sport_type': sport_type,
                'created_at': datetime.now()
            }
            players.append(player_info)
    
    return players

def generate_dummy_football_players(match_id, team1_name, team2_name, match_date=None):
    """Generate football players using Gemini API or fallback to dummy data"""
    # Use the main generate_dummy_players function with football sport type
    return generate_dummy_players(match_id, team1_name, team2_name, 'football', match_date)

def determine_cricket_role(position):
    """Determine cricket role from position"""
    if not position:
        return 'All-Rounder'
    
    position_lower = position.lower()
    
    # Check for batsman keywords
    if any(word in position_lower for word in ['bat', 'bats', 'batsman', 'batter', 'opening', 'middle order', 'top order']):
        return 'Batsman'
    
    # Check for bowler keywords
    elif any(word in position_lower for word in ['bowl', 'bowler', 'fast', 'spin', 'pace', 'seam', 'medium']):
        return 'Bowler'
    
    # Check for wicket-keeper keywords
    elif any(word in position_lower for word in ['keep', 'keeper', 'wicket', 'wk']):
        return 'Wicket-Keeper'
    
    # Check for all-rounder keywords
    elif any(word in position_lower for word in ['all', 'rounder', 'all-rounder']):
        return 'All-Rounder'
    
    # Default to All-Rounder
    else:
        return 'All-Rounder'

def determine_football_role(position):
    """Determine football role from position"""
    if not position:
        return 'Midfielder'
    
    position_lower = position.lower()
    
    # Check for goalkeeper
    if any(word in position_lower for word in ['goalkeeper', 'keeper', 'gk']):
        return 'Goalkeeper'
    
    # Check for defender
    elif any(word in position_lower for word in ['defender', 'defence', 'back', 'cb', 'lb', 'rb']):
        return 'Defender'
    
    # Check for midfielder
    elif any(word in position_lower for word in ['midfielder', 'midfield', 'mid', 'cm', 'dm', 'am']):
        return 'Midfielder'
    
    # Check for forward/attacker
    elif any(word in position_lower for word in ['forward', 'attacker', 'striker', 'winger', 'fw', 'st', 'lw', 'rw']):
        return 'Forward'
    
    # Default to Midfielder
    else:
        return 'Midfielder'

def assign_roles_by_distribution(team_players):
    """Assign roles to players based on distribution if too many are All-Rounders"""
    # Count current role distribution
    role_count = {'Batsman': 0, 'Bowler': 0, 'All-Rounder': 0, 'Wicket-Keeper': 0}
    for player in team_players:
        role_count[player['role']] += 1
    
    # If most players are All-Rounders, redistribute
    if role_count['All-Rounder'] > len(team_players) * 0.6:  # More than 60% are All-Rounders
        # Typical cricket team composition: 4 batsmen, 4 bowlers, 2 all-rounders, 1 keeper
        roles_to_assign = ['Batsman'] * 4 + ['Bowler'] * 4 + ['All-Rounder'] * 2 + ['Wicket-Keeper'] * 1
        
        # Shuffle to randomize assignment
        import random
        random.shuffle(roles_to_assign)
        
        # Assign roles to All-Rounder players
        all_rounder_players = [p for p in team_players if p['role'] == 'All-Rounder']
        for i, player in enumerate(all_rounder_players):
            if i < len(roles_to_assign):
                player['role'] = roles_to_assign[i]
