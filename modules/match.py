"""Match fetching and management functions for Fantasy IQ application"""
import requests
import traceback
from datetime import datetime, timedelta
from modules.config import Config

def fetch_cricket_matches():
    """Fetch next 6 upcoming cricket matches from SportMonks API"""
    try:
        if not Config.SPORTMONKS_API_KEY:
            print("SportMonks API key not configured. Cannot fetch matches.")
            return []
        
        matches = []
        
        # Calculate today's date
        today = datetime.now().date()
        
        # SportMonks API endpoint for cricket fixtures
        # Fetch upcoming fixtures
        url = f"https://cricket.sportmonks.com/api/v2.0/fixtures"
        params = {
            'api_token': Config.SPORTMONKS_API_KEY,
            'filter[status]': 'NS',  # NS = Not Started (upcoming)
            'include': 'localteam,visitorteam,venue,league',
            'sort': 'starting_at',
            'per_page': 50  # Fetch more to have options
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                print("No fixtures data received from SportMonks API")
                return []
            
            fixtures = data.get('data', [])
            
            for fixture in fixtures:
                try:
                    # Get match date and time
                    starting_at = fixture.get('starting_at', '')
                    if not starting_at:
                        continue
                    
                    # Parse the starting time (SportMonks provides UTC time in ISO format)
                    # Format: 2025-11-11T15:00:00.000000Z
                    try:
                        # Remove the 'Z' and split off microseconds
                        if starting_at.endswith('Z'):
                            starting_at = starting_at[:-1]  # Remove 'Z'
                        
                        # Parse datetime with or without microseconds
                        if '.' in starting_at:
                            match_start_time_utc = datetime.strptime(starting_at, '%Y-%m-%dT%H:%M:%S.%f')
                        else:
                            match_start_time_utc = datetime.strptime(starting_at, '%Y-%m-%dT%H:%M:%S')
                    except Exception as e:
                        print(f"Error parsing date '{starting_at}': {e}")
                        continue
                    
                    # Convert UTC to IST by adding 5 hours 30 minutes
                    match_start_time = match_start_time_utc + timedelta(hours=5, minutes=30)
                    
                    # Check if match is from today onwards
                    match_date_obj = match_start_time.date()
                    if match_date_obj < today:
                        continue
                    
                    # Estimate match end (T20: 3.5 hours, ODI: 8 hours)
                    match_end_time = match_start_time + timedelta(hours=4)
                    
                    # Get team names
                    localteam = fixture.get('localteam', {})
                    visitorteam = fixture.get('visitorteam', {})
                    team1 = localteam.get('name', 'Team A') if localteam else 'Team A'
                    team2 = visitorteam.get('name', 'Team B') if visitorteam else 'Team B'
                    
                    # Get venue and league info (handle None values)
                    venue_data = fixture.get('venue')
                    venue = venue_data.get('name', 'TBD') if venue_data and isinstance(venue_data, dict) else 'TBD'
                    
                    league_data = fixture.get('league')
                    league_name = league_data.get('name', 'Cricket League') if league_data and isinstance(league_data, dict) else 'Cricket League'
                    
                    # Get match type from league or round
                    match_type = fixture.get('type', 'T20')
                    if not match_type or match_type == '':
                        match_type = league_name
                    
                    match = {
                        'match_id': str(fixture.get('id')),
                        'name': f"{team1} vs {team2}",
                        'match_type': match_type,
                        'status': 'upcoming',
                        'venue': venue,
                        'date': match_start_time.strftime('%Y-%m-%d'),
                        'dateTimeGMT': starting_at,
                        'match_start_time': match_start_time,
                        'match_end_time': match_end_time,
                        'teams': [team1, team2],
                        'sport_type': 'cricket',
                        'league': league_name,
                        'season': fixture.get('season_id', ''),
                        'round': fixture.get('round', ''),
                        'note': fixture.get('note', ''),
                        'created_at': datetime.now(),
                        'fetched_at': datetime.now()
                    }
                    matches.append(match)
                    
                    if len(matches) >= 6:  # Limit to next 6 matches
                        break
                        
                except Exception as e:
                    print(f"Error parsing fixture: {e}")
                    continue
            
            if len(matches) >= 6:
                return matches[:6]
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from SportMonks API: {e}")
            return []
        
        # Return matches (empty list if none found)
        if not matches:
            print("No upcoming matches found from SportMonks API.")
        
        return matches
        
    except Exception as e:
        print(f"Unexpected error in fetch_cricket_matches: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_football_matches():
    """Fetch next 6 upcoming football matches from SportMonks API"""
    try:
        if not Config.SPORTMONKS_API_KEY:
            print("SportMonks API key not configured. Cannot fetch matches.")
            return []
        
        matches = []
        
        # Calculate today's date and date range for next 30 days
        today = datetime.now().date()
        end_date = today + timedelta(days=30)
        
        # SportMonks Football API endpoint for fixtures between dates
        url = f"https://soccer.sportmonks.com/api/v2.0/fixtures/between/{today}/{end_date}"
        params = {
            'api_token': Config.SPORTMONKS_API_KEY,
            'include': 'localTeam,visitorTeam,venue,league'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                print("No fixtures data received from SportMonks Football API")
                return []
            
            fixtures = data.get('data', [])
            
            for fixture in fixtures:
                try:
                    # Get match date and time
                    starting_at = fixture.get('starting_at', '') or fixture.get('time', {}).get('starting_at', {}).get('date_time', '')
                    if not starting_at:
                        continue
                    
                    # Parse the starting time (SportMonks provides UTC time in ISO format)
                    try:
                        # Remove the 'Z' and split off microseconds if present
                        if starting_at.endswith('Z'):
                            starting_at = starting_at[:-1]
                        
                        # Parse datetime with different formats
                        if 'T' in starting_at:
                            # ISO format: 2025-11-11T15:00:00 or 2025-11-11T15:00:00.000000
                            if '.' in starting_at:
                                match_start_time_utc = datetime.strptime(starting_at, '%Y-%m-%dT%H:%M:%S.%f')
                            else:
                                match_start_time_utc = datetime.strptime(starting_at, '%Y-%m-%dT%H:%M:%S')
                        else:
                            # Simple format: 2025-11-22 15:00:00
                            match_start_time_utc = datetime.strptime(starting_at, '%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        print(f"Error parsing date '{starting_at}': {e}")
                        continue
                    
                    # Convert UTC to IST by adding 5 hours 30 minutes
                    match_start_time = match_start_time_utc + timedelta(hours=5, minutes=30)
                    
                    # Check if match is from today onwards
                    match_date_obj = match_start_time.date()
                    if match_date_obj < today:
                        continue
                    
                    # Football match duration (90 minutes + extra time)
                    match_end_time = match_start_time + timedelta(hours=2)
                    
                    # Get team names
                    localteam = fixture.get('localTeam', {})
                    visitorteam = fixture.get('visitorTeam', {})
                    team1 = localteam.get('data', {}).get('name', 'Team A') if isinstance(localteam.get('data'), dict) else localteam.get('name', 'Team A') if localteam else 'Team A'
                    team2 = visitorteam.get('data', {}).get('name', 'Team B') if isinstance(visitorteam.get('data'), dict) else visitorteam.get('name', 'Team B') if visitorteam else 'Team B'
                    
                    # Get venue and league info (handle None values)
                    venue_data = fixture.get('venue')
                    if venue_data:
                        venue = venue_data.get('data', {}).get('name', 'TBD') if isinstance(venue_data.get('data'), dict) else venue_data.get('name', 'TBD') if isinstance(venue_data, dict) else 'TBD'
                    else:
                        venue = 'TBD'
                    
                    league_data = fixture.get('league')
                    if league_data:
                        league_name = league_data.get('data', {}).get('name', 'Football League') if isinstance(league_data.get('data'), dict) else league_data.get('name', 'Football League') if isinstance(league_data, dict) else 'Football League'
                    else:
                        league_name = 'Football League'
                    
                    # Get match round/stage
                    round_name = fixture.get('round', {}).get('data', {}).get('name', '') if isinstance(fixture.get('round'), dict) else fixture.get('stage', {}).get('name', '')
                    
                    match = {
                        'match_id': str(fixture.get('id')),
                        'name': f"{team1} vs {team2}",
                        'match_type': league_name,
                        'status': 'upcoming',
                        'venue': venue,
                        'date': match_start_time.strftime('%Y-%m-%d'),
                        'dateTimeGMT': fixture.get('starting_at', ''),
                        'match_start_time': match_start_time,
                        'match_end_time': match_end_time,
                        'teams': [team1, team2],
                        'sport_type': 'football',
                        'league': league_name,
                        'season': fixture.get('season_id', ''),
                        'round': round_name,
                        'created_at': datetime.now(),
                        'fetched_at': datetime.now()
                    }
                    matches.append(match)
                    
                    if len(matches) >= 6:  # Limit to next 6 matches
                        break
                        
                except Exception as e:
                    print(f"Error parsing football fixture: {e}")
                    continue
            
            if len(matches) >= 6:
                return matches[:6]
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from SportMonks Football API: {e}")
            return []
        
        # Return matches (empty list if none found)
        if not matches:
            print("No upcoming football matches found from SportMonks API.")
        
        return matches
        
    except Exception as e:
        print(f"Unexpected error in fetch_football_matches: {e}")
        import traceback
        traceback.print_exc()
        return []

def cleanup_expired_matches(db):
    """Delete matches, contests, players, user teams that ended more than 1 hour ago, and joined contests after 1 day"""
    try:
        print("Running cleanup_expired_matches...")
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=1)
        cutoff_time_joined = current_time - timedelta(days=1)  # Joined contests cleanup after 1 day
        
        print(f"Current time: {current_time}, Cutoff time: {cutoff_time}, Joined contests cutoff: {cutoff_time_joined}")
        
        matches_collection = db['matches']
        contests_collection = db['contests']
        players_collection = db['players']
        user_teams_collection = db['user_teams']
        joined_contests_collection = db['joined_contests']
        
        # Find all matches to check their end times
        all_matches = list(matches_collection.find())
        print(f"Total matches in database: {len(all_matches)}")
        
        deleted_matches = 0
        deleted_contests = 0
        deleted_players = 0
        deleted_teams = 0
        deleted_joined_contests = 0
        
        for match in all_matches:
            match_id = match.get('match_id')
            match_end_time = match.get('match_end_time')
            
            if not match_end_time:
                print(f"Match {match_id} has no end time, skipping")
                continue
            
            # Convert match_end_time to datetime if it's a string
            if isinstance(match_end_time, str):
                try:
                    match_end_time = datetime.strptime(match_end_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        match_end_time = datetime.fromisoformat(match_end_time.replace('Z', '+00:00'))
                    except:
                        print(f"Could not parse match_end_time for match {match_id}: {match_end_time}")
                        continue
            
            # Check if match ended more than 1 hour ago
            if match_end_time < cutoff_time:
                print(f"Deleting expired match: {match_id} (ended at {match_end_time})")
                
                # Delete all contests for this match
                result = contests_collection.delete_many({'match_id': match_id})
                deleted_contests += result.deleted_count
                
                # Delete all players for this match
                result = players_collection.delete_many({'match_id': match_id})
                deleted_players += result.deleted_count
                
                # Delete all user teams for this contest
                result = user_teams_collection.delete_many({'contest_id': match_id})
                deleted_teams += result.deleted_count
                
                # Delete joined contest entries only if match ended more than 1 day ago
                if match_end_time < cutoff_time_joined:
                    result = joined_contests_collection.delete_many({'contest_id': match_id})
                    deleted_joined_contests += result.deleted_count
                    print(f"  - Also deleted {result.deleted_count} joined contest entries (match ended > 1 day ago)")
                
                # Delete the match
                matches_collection.delete_one({'match_id': match_id})
                deleted_matches += 1
        
        if deleted_matches > 0:
            print(f"Cleanup completed: {deleted_matches} matches, {deleted_contests} contests, {deleted_players} players, {deleted_teams} user teams, and {deleted_joined_contests} joined contests deleted")
        else:
            print("No expired matches to clean up")
        
    except Exception as e:
        print(f"Error in cleanup_expired_matches: {e}")
        import traceback
        traceback.print_exc()
