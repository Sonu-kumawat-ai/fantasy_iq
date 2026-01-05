"""Contest creation and management functions for Fantasy IQ application"""
from datetime import datetime
import traceback
import random
from modules.match import fetch_cricket_matches, fetch_football_matches

def create_contests_for_match(db, match_id, match_name, sport_type='cricket'):
    """Create contests for a specific match"""
    try:
        contests_collection = db['contests']
        
        # Check if contests already exist for this match
        existing = contests_collection.find_one({'match_id': match_id})
        if existing:
            return True
        
        # Get match details from database
        matches_collection = db['matches']
        match = matches_collection.find_one({'match_id': match_id})
        
        # Create multiple contest configurations
        import random
        contest_templates = [
            {'badge': 'Featured', 'entry_fee': 49, 'prize_pool': 1000000, 'max_spots': 10000},
            {'badge': 'Mega', 'entry_fee': 99, 'prize_pool': 2500000, 'max_spots': 15000},
            {'badge': 'Premium', 'entry_fee': 149, 'prize_pool': 5000000, 'max_spots': 20000},
            {'badge': 'Hot', 'entry_fee': 29, 'prize_pool': 500000, 'max_spots': 8000},
        ]
        
        # Select random template
        template = random.choice(contest_templates)
        
        # Create contest with match data
        contest = {
            'match_id': match_id,
            'match_name': match_name,
            'title': match_name,
            'badge': template['badge'],
            'entry_fee': template['entry_fee'],
            'prize_pool': template['prize_pool'],
            'max_spots': template['max_spots'],
            'filled_spots': 0,
            'sport_type': sport_type,
            'status': 'open',
            'created_at': datetime.now()
        }
        
        # Add match details if available
        if match:
            contest['match_date'] = match.get('date')
            contest['match_start_time'] = match.get('match_start_time')
            contest['match_end_time'] = match.get('match_end_time')
            contest['venue'] = match.get('venue')
            contest['teams'] = match.get('teams', [])
            contest['league'] = match.get('league', '')
        
        contests_collection.insert_one(contest)
        return True
        
    except Exception as e:
        traceback.print_exc()
        return False

def sync_matches_and_contests(db):
    """Sync matches and contests from SportMonks API - Called every 6 hours"""
    try:
        matches_collection = db['matches']
        contests_collection = db['contests']
        
        # Fetch matches from API
        cricket_matches = fetch_cricket_matches()
        football_matches = fetch_football_matches()
        
        # Combine all matches
        all_matches = cricket_matches + football_matches
        
        # Process each match
        for match in all_matches:
            match_id = match['match_id']
            sport_type = match.get('sport_type', 'cricket')
            match_name = match.get('name', 'Unknown Match')
            
            # Check if match already exists in database
            existing_match = matches_collection.find_one({'match_id': match_id})
            
            if not existing_match:
                # Insert new match
                matches_collection.insert_one(match)
                # Create contests for this new match
                create_contests_for_match(db, match_id, match_name, sport_type)
            else:
                # Update existing match details (venue, time, etc. might change)
                matches_collection.update_one(
                    {'match_id': match_id},
                    {'$set': match}
                )
        return True
        
    except Exception as e:
        print(f"Error in sync_matches_and_contests: {e}")
        traceback.print_exc()
        return False
