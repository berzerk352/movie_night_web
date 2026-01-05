"""Main Flask application for Movie Night Web."""
import os

from flask import Flask, render_template, request, jsonify

from config import config
from models import db, Season, Participant, Roll
from database import init_db
from roll_logic import (
    perform_roll,
    get_eligible_participants,
    get_season_roster,
    reset_season_roster
)
from sheets_integration import (
    get_participants_from_sheet,
    get_movies_by_participant
)
from tmdb_integration import enrich_movie_data


def create_app(config_name='default'):
    """Application factory pattern."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config[config_name])

    # Initialize database
    init_db(flask_app)

    return flask_app


app = create_app(os.getenv('FLASK_ENV', 'development'))


# ============================================================================
# Web Routes (HTML Pages)
# ============================================================================

@app.route('/')
def index():
    """Main page."""
    # Get the active season
    season = Season.query.filter_by(is_active=True).first()
    
    # Get the most recent roll for the active season
    latest_roll = None
    if season:
        latest_roll = Roll.query.filter_by(season_id=season.id)\
            .order_by(Roll.roll_date.desc())\
            .first()
    
    return render_template('index.html', latest_roll=latest_roll)


@app.route('/history')
def history():
    """View roll history."""
    return render_template('history.html')


@app.route('/seasons')
def seasons_page():
    """Manage seasons."""
    return render_template('seasons.html')


# ============================================================================
# API Routes - Seasons
# ============================================================================

@app.route('/api/seasons', methods=['GET'])
def api_get_seasons():
    """Get all seasons."""
    all_seasons = Season.query.order_by(Season.created_at.desc()).all()
    return jsonify([s.to_dict() for s in all_seasons])


@app.route('/api/seasons', methods=['POST'])
def api_create_season():
    """Create a new season."""
    data = request.json

    # Deactivate other seasons if this one is active
    if data.get('is_active', True):
        Season.query.update({'is_active': False})

    season = Season(
        name=data['name'],
        spreadsheet_tab=data.get('spreadsheet_tab', 'General'),
        is_active=data.get('is_active', True)
    )
    db.session.add(season)
    db.session.commit()

    return jsonify(season.to_dict()), 201


@app.route('/api/seasons/<int:season_id>', methods=['GET'])
def api_get_season(season_id):
    """Get a specific season."""
    season = Season.query.get_or_404(season_id)
    return jsonify(season.to_dict())


@app.route('/api/seasons/<int:season_id>', methods=['PUT'])
def api_update_season(season_id):
    """Update a season."""
    season = Season.query.get_or_404(season_id)
    data = request.json

    if 'name' in data:
        season.name = data['name']
    if 'spreadsheet_tab' in data:
        season.spreadsheet_tab = data['spreadsheet_tab']
    if 'is_active' in data:
        if data['is_active']:
            # Deactivate other seasons
            Season.query.filter(Season.id != season_id).update({'is_active': False})
        season.is_active = data['is_active']

    db.session.commit()
    return jsonify(season.to_dict())


@app.route('/api/seasons/<int:season_id>/roster', methods=['GET'])
def api_get_season_roster(season_id):
    """Get the roster for a season."""
    roster = get_season_roster(season_id)
    return jsonify({'roster': roster})


@app.route('/api/seasons/<int:season_id>/roster', methods=['DELETE'])
def api_reset_season_roster(season_id):
    """Reset the season roster."""
    success = reset_season_roster(season_id)
    if success:
        return jsonify({'message': 'Season roster reset successfully'})
    return jsonify({'error': 'Failed to reset season roster'}), 500


# ============================================================================
# API Routes - Participants
# ============================================================================

@app.route('/api/participants', methods=['GET'])
def api_get_participants():
    """Get all participants from database."""
    participants = Participant.query.order_by(Participant.name).all()
    return jsonify([p.to_dict() for p in participants])


@app.route('/api/participants/sheet', methods=['GET'])
def api_get_participants_from_sheet():
    """Get participants from Google Sheets."""
    season_id = request.args.get('season_id', type=int)

    if season_id:
        season = Season.query.get_or_404(season_id)
        tab = season.spreadsheet_tab
    else:
        tab = 'General'

    participants = get_participants_from_sheet(tab)
    return jsonify({'participants': participants})


@app.route('/api/participants/<int:participant_id>/movies', methods=['GET'])
def api_get_participant_movies(participant_id):
    """Get movies for a specific participant."""
    participant = Participant.query.get_or_404(participant_id)
    season_id = request.args.get('season_id', type=int)

    if season_id:
        season = Season.query.get_or_404(season_id)
        tab = season.spreadsheet_tab
    else:
        tab = 'General'

    movies = get_movies_by_participant(participant.name, tab)
    return jsonify({'movies': movies})


# ============================================================================
# API Routes - Rolls
# ============================================================================

@app.route('/api/rolls', methods=['GET'])
def api_get_rolls():
    """Get all rolls, optionally filtered by season."""
    season_id = request.args.get('season_id', type=int)

    query = Roll.query
    if season_id:
        query = query.filter_by(season_id=season_id)

    rolls = query.order_by(Roll.roll_date.desc()).all()
    return jsonify([r.to_dict() for r in rolls])


@app.route('/api/rolls', methods=['POST'])
def api_perform_roll():
    """Perform a new roll."""
    data = request.json
    season_id = data.get('season_id')
    custom_participants = data.get('participants')

    if not season_id:
        # Get active season
        season = Season.query.filter_by(is_active=True).first()
        if not season:
            return jsonify({'error': 'No active season found'}), 400
        season_id = season.id

    result = perform_roll(season_id, custom_participants)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result), 201


@app.route('/api/rolls/<int:roll_id>', methods=['GET'])
def api_get_roll(roll_id):
    """Get a specific roll."""
    roll = Roll.query.get_or_404(roll_id)
    return jsonify(roll.to_dict())


@app.route('/api/rolls/<int:roll_id>', methods=['PUT'])
def api_update_roll(roll_id):
    """Update a roll (e.g., add notes or TMDB data)."""
    roll = Roll.query.get_or_404(roll_id)
    data = request.json

    if 'notes' in data:
        roll.notes = data['notes']
    if 'tmdb_id' in data:
        roll.tmdb_id = data['tmdb_id']
    if 'tmdb_data' in data:
        roll.tmdb_data = data['tmdb_data']

    db.session.commit()
    return jsonify(roll.to_dict())


@app.route('/api/rolls/<int:roll_id>/enrich', methods=['POST'])
def api_enrich_roll(roll_id):
    """Enrich a roll with TMDB data."""
    roll = Roll.query.get_or_404(roll_id)

    tmdb_data = enrich_movie_data(roll.movie_title)

    if tmdb_data:
        roll.tmdb_id = tmdb_data.get('tmdb_id')
        roll.tmdb_data = tmdb_data
        db.session.commit()
        return jsonify(roll.to_dict())

    return jsonify({'error': 'Could not fetch TMDB data'}), 404


@app.route('/api/rolls/<int:roll_id>', methods=['DELETE'])
def api_delete_roll(roll_id):
    """Delete a roll."""
    roll = Roll.query.get_or_404(roll_id)
    db.session.delete(roll)
    db.session.commit()
    return jsonify({'message': 'Roll deleted successfully'})


# ============================================================================
# API Routes - Utilities
# ============================================================================

@app.route('/api/eligible', methods=['GET'])
def api_get_eligible():
    """Get eligible participants for rolling."""
    season_id = request.args.get('season_id', type=int)

    if not season_id:
        season = Season.query.filter_by(is_active=True).first()
        if not season:
            return jsonify({'error': 'No active season found'}), 400
        season_id = season.id

    eligible = get_eligible_participants(season_id)
    return jsonify({'eligible': eligible, 'count': len(eligible)})


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(_error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(_error):
    """Handle 500 errors."""
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
