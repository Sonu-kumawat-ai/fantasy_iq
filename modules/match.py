"""Match fetching and management functions for Fantasy IQ application"""
import requests
import traceback
from datetime import datetime, timedelta
from modules.config import Config

def fetch_cricket_matches():
    """Fetch next 6 upcoming cricket matches from CricAPI"""
    try:
        matches = []
        
        # Calculate today's date
        today = datetime.now().date()
        
        # CricAPI endpoint for cricket schedule (upcoming matches)
        url = "https://api.cricapi.com/v1/cricScore"
        params = {
            'apikey': Config.CRICAPI_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                return []
            
            fixtures = data.get('data', [])
            
            for fixture in fixtures:
                try:
                    # Get match date and time first
                    date_str = fixture.get('dateTimeGMT', '')
                    if not date_str:
                        continue
                    
                    # Only get upcoming matches - skip completed or in-progress matches
                    match_status = fixture.get('status', '').lower()
                    match_started = fixture.get('matchStarted', False)
                    match_ended = fixture.get('matchEnded', False)
                    
                    # Skip if match has already started or ended
                    if match_started or match_ended:
                        continue
                    
                    # Accept statuses that indicate upcoming matches
                    is_upcoming = (
                        not match_status or  # Empty status
                        'not started' in match_status or  # "Match not started"
                        'starts at' in match_status or  # "Match starts at..."
                        match_status in ['fixture', 'upcoming', 'scheduled']
                    )
                    
                    if not is_upcoming:
                        continue
                    
                    # Parse the starting time (CricAPI provides GMT time)
                    try:
                        match_start_time_utc = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                    except Exception:
                        continue
                    
                    # Convert UTC to IST by adding 5 hours 30 minutes
                    match_start_time = match_start_time_utc + timedelta(hours=5, minutes=30)
                    
                    # Only get matches within next 7 days
                    match_date_obj = match_start_time.date()
                    max_date = today + timedelta(days=7)
                    
                    if match_date_obj < today or match_date_obj > max_date:
                        continue
                    
                    # Estimate match end (T20: 3.5 hours, ODI: 8 hours, Test: 6 hours per day)
                    match_type = fixture.get('matchType', 't20').lower()
                    if 'test' in match_type:
                        match_end_time = match_start_time + timedelta(hours=6)
                    elif 'odi' in match_type:
                        match_end_time = match_start_time + timedelta(hours=8)
                    else:
                        match_end_time = match_start_time + timedelta(hours=3, minutes=30)
                    
                    # Get team names from t1 and t2 fields
                    team1 = fixture.get('t1', 'Team A')
                    team2 = fixture.get('t2', 'Team B')
                    
                    # Clean team names (remove abbreviations in brackets)
                    if '[' in team1:
                        team1 = team1.split('[')[0].strip()
                    if '[' in team2:
                        team2 = team2.split('[')[0].strip()
                    
                    # Get venue info
                    venue = fixture.get('venue', 'TBD')
                    
                    # Get series name
                    series_name = fixture.get('series', fixture.get('matchType', 'Cricket Match'))
                    
                    match = {
                        'match_id': str(fixture.get('id')),
                        'name': f"{team1} vs {team2}",
                        'match_type': fixture.get('matchType', 'T20').upper(),
                        'status': 'upcoming',
                        'venue': venue,
                        'date': match_start_time.strftime('%Y-%m-%d'),
                        'dateTimeGMT': date_str,
                        'match_start_time': match_start_time,
                        'match_end_time': match_end_time,
                        'teams': [team1, team2],
                        'sport_type': 'cricket',
                        'league': series_name,
                        'season': '',
                        'round': '',
                        'note': '',
                        'created_at': datetime.now(),
                        'fetched_at': datetime.now()
                    }
                    matches.append(match)
                    
                    if len(matches) >= 6:  # Limit to next 6 matches
                        break
                        
                except Exception:
                    continue
            
            if len(matches) >= 6:
                return matches[:6]
                
        except requests.exceptions.RequestException:
            return []
        
        return matches
        
    except Exception:
        return []

def fetch_football_matches():
    """Fetch next 6 upcoming football matches from TheSportsDB API"""
    try:
        matches = []
        
        # Calculate today's date
        today = datetime.now().date()
        
        # TheSportsDB API endpoint for next 15 events for major leagues
        # Free API key: 3 (test key with limited access)
        leagues = [
            '4328',  # English Premier League
            '4335',  # Spanish La Liga
            '4331',  # German Bundesliga
            '4332',  # Italian Serie A
            '4334',  # French Ligue 1
        ]
        
        for league_id in leagues:
            try:
                url = f"https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php"
                params = {'id': league_id}
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                if not data or 'events' not in data or data.get('events') is None:
                    continue
                
                fixtures = data.get('events', [])
                
                for fixture in fixtures:
                    try:
                        # Get match date and time
                        date_str = fixture.get('dateEvent', '')
                        time_str = fixture.get('strTime', '15:00:00')  # Default time if not available
                        
                        if not date_str:
                            continue
                        
                        # Parse the starting time
                        try:
                            datetime_str = f"{date_str} {time_str}"
                            match_start_time_utc = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                        except Exception:
                            continue
                        
                        # Convert UTC to IST by adding 5 hours 30 minutes
                        match_start_time = match_start_time_utc + timedelta(hours=5, minutes=30)
                        
                        # Only get matches within next 7 days
                        match_date_obj = match_start_time.date()
                        max_date = today + timedelta(days=7)
                        
                        if match_date_obj < today or match_date_obj > max_date:
                            continue
                        
                        # Football match duration (90 minutes + extra time)
                        match_end_time = match_start_time + timedelta(hours=2)
                        
                        # Get team names
                        team1 = fixture.get('strHomeTeam', 'Team A')
                        team2 = fixture.get('strAwayTeam', 'Team B')
                        
                        # Get venue and league info
                        venue = fixture.get('strVenue', 'TBD')
                        league_name = fixture.get('strLeague', 'Football League')
                        
                        # Get match round/stage
                        round_name = fixture.get('intRound', '')
                        
                        match = {
                            'match_id': str(fixture.get('idEvent')),
                            'name': f"{team1} vs {team2}",
                            'match_type': league_name,
                            'status': 'upcoming',
                            'venue': venue,
                            'date': match_start_time.strftime('%Y-%m-%d'),
                            'dateTimeGMT': f"{date_str}T{time_str}",
                            'match_start_time': match_start_time,
                            'match_end_time': match_end_time,
                            'teams': [team1, team2],
                            'sport_type': 'football',
                            'league': league_name,
                            'season': fixture.get('strSeason', ''),
                            'round': str(round_name),
                            'created_at': datetime.now(),
                            'fetched_at': datetime.now()
                        }
                        matches.append(match)
                        
                        if len(matches) >= 6:  # Limit to next 6 matches
                            break
                            
                    except Exception:
                        continue
                
                if len(matches) >= 6:
                    break
                    
            except requests.exceptions.RequestException:
                continue
        
        return matches[:6]
        
    except Exception:
        return []

def cleanup_expired_matches(db):
    """Delete matches, contests, players, user teams that ended more than 1 hour ago, and joined contests after 1 day"""
    try:
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=1)
        cutoff_time_joined = current_time - timedelta(days=1)  # Joined contests cleanup after 1 day
        
        matches_collection = db['matches']
        contests_collection = db['contests']
        players_collection = db['players']
        user_teams_collection = db['user_teams']
        joined_contests_collection = db['joined_contests']
        
        # Find all matches to check their end times
        all_matches = list(matches_collection.find())
        
        deleted_matches = 0
        deleted_contests = 0
        deleted_players = 0
        deleted_teams = 0
        deleted_joined_contests = 0
        
        for match in all_matches:
            match_id = match.get('match_id')
            match_end_time = match.get('match_end_time')
            
            if not match_end_time:
                continue
            
            # Convert match_end_time to datetime if it's a string
            if isinstance(match_end_time, str):
                try:
                    match_end_time = datetime.strptime(match_end_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        match_end_time = datetime.fromisoformat(match_end_time.replace('Z', '+00:00'))
                    except:
                        continue
            
            # Check if match ended more than 1 hour ago
            if match_end_time < cutoff_time:
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
                
                # Delete the match
                matches_collection.delete_one({'match_id': match_id})
                deleted_matches += 1
        
    except Exception:
        pass
