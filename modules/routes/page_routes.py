"""Page rendering routes for Fantasy IQ application"""
from flask import render_template, session, redirect, url_for, request
from datetime import datetime

def register_page_routes(app, db):
    """Register all page/template rendering routes"""
    
    # Get collections from db
    joined_contests_collection = db['joined_contests']
    user_teams_collection = db['user_teams']
    matches_collection = db['matches']
    
    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/home')
    def home():
        username = session.get('username', None)
        return render_template('index.html', username=username)

    @app.route('/login-page')
    def login_page():
        return render_template('login_new.html')

    @app.route('/register-page')
    def register_page():
        return render_template('register.html')

    @app.route('/profile')
    def profile():
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return render_template('profile.html')

    @app.route('/wallet')
    def wallet():
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return render_template('wallet.html')

    @app.route('/about')
    def about():
        username = session.get('username', None)
        return render_template('about.html', username=username)

    @app.route('/contests')
    def contests():
        username = session.get('username', None)
        return render_template('contests.html', username=username)

    @app.route('/contest-details')
    def contest_details():
        username = session.get('username', None)
        return render_template('contest_details.html', username=username)

    @app.route('/points-rules')
    def points_rules():
        username = session.get('username', None)
        return render_template('points_rules.html', username=username)

    @app.route('/joined-contests')
    def joined_contests():
        if 'username' not in session:
            return redirect(url_for('login_page'))
        
        try:
            # Get all joined contests for the user
            contests = list(joined_contests_collection.find(
                {'username': session['username']},
                {'_id': 0}
            ).sort('joined_at', -1))
            
            # Enhance each contest with team status and match status
            for contest in contests:
                # Convert datetime to string
                if 'joined_at' in contest and isinstance(contest['joined_at'], datetime):
                    contest['joined_at'] = contest['joined_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                # Check if user has created a team for this contest
                team = user_teams_collection.find_one({
                    'username': session['username'],
                    'contest_id': contest.get('contest_id')
                })
                contest['has_team'] = team is not None
                
                # Get match information to check if it has started
                match = matches_collection.find_one({'match_id': contest.get('contest_id')})
                if match:
                    match_start_time = match.get('match_start_time')
                    if match_start_time:
                        if isinstance(match_start_time, str):
                            match_start_time = datetime.strptime(match_start_time, '%Y-%m-%d %H:%M:%S')
                        contest['match_started'] = datetime.now() >= match_start_time
                    else:
                        contest['match_started'] = False
                else:
                    contest['match_started'] = False
            
            username = session.get('username', None)
            return render_template('joined_contests.html', username=username, contests=contests)
        except Exception as e:
            print(f"Error loading joined contests: {e}")
            username = session.get('username', None)
            return render_template('joined_contests.html', username=username, contests=[])

    @app.route('/create-team')
    def create_team():
        """Team creation page"""
        if 'username' not in session:
            return redirect(url_for('login_page'))
        
        contest_id = request.args.get('contest_id')
        if not contest_id:
            return redirect(url_for('home'))
        
        username = session.get('username', None)
        return render_template('create_team.html', username=username, contest_id=contest_id)
