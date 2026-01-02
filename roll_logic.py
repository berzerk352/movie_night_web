"""Core movie roll logic adapted from movie_night_roll project."""
import random
from models import db, Season, Participant, Roll
from sheets_integration import get_movies_from_sheet, get_participants_from_sheet


def get_eligible_participants(season_id, custom_participants=None):
    """
    Get list of eligible participants for a roll.

    Args:
        season_id: ID of the current season
        custom_participants: Optional list of specific participants to include

    Returns:
        List of participant names eligible for rolling
    """
    season = Season.query.get(season_id)
    if not season:
        return []

    # Get all participants from Google Sheets
    all_participants = get_participants_from_sheet(season.spreadsheet_tab)

    # Get participants who have already been rolled this season
    rolled_participants = db.session.query(Participant.name).join(Roll).filter(
        Roll.season_id == season_id
    ).all()
    rolled_names = {name for (name,) in rolled_participants}

    # Filter based on custom list or use all
    if custom_participants:
        eligible = [p for p in custom_participants if p not in rolled_names]
    else:
        eligible = [p for p in all_participants if p not in rolled_names]

    return eligible


def perform_roll(season_id, custom_participants=None):
    """
    Perform a movie night roll.

    Args:
        season_id: ID of the season to roll for
        custom_participants: Optional list of specific participants

    Returns:
        Dictionary with roll results or None if error
    """
    season = Season.query.get(season_id)
    if not season:
        return {'error': 'Season not found'}

    # Get eligible participants
    eligible = get_eligible_participants(season_id, custom_participants)

    if not eligible:
        return {'error': 'No eligible participants available'}

    # Randomly select a participant
    selected_name = random.choice(eligible)

    # Get or create participant in database
    participant = Participant.query.filter_by(name=selected_name).first()
    if not participant:
        participant = Participant(name=selected_name)
        db.session.add(participant)
        db.session.flush()

    # Get movies from this participant
    movies = get_movies_from_sheet(season.spreadsheet_tab)
    participant_movies = [
        movie for movie, submitter in movies
        if submitter.strip().upper() == selected_name.upper()
    ]

    if not participant_movies:
        return {'error': f'No movies found for {selected_name}'}

    # Randomly select a movie
    selected_movie = random.choice(participant_movies)

    # Create roll record
    roll = Roll(
        season_id=season_id,
        participant_id=participant.id,
        movie_title=selected_movie
    )
    db.session.add(roll)
    db.session.commit()

    return {
        'success': True,
        'participant': selected_name,
        'movie': selected_movie,
        'roll_id': roll.id,
        'eligible_count': len(eligible)
    }


def get_season_roster(season_id):
    """
    Get the roster of participants who have been rolled this season.

    Args:
        season_id: ID of the season

    Returns:
        List of participant names
    """
    rolls = Roll.query.filter_by(season_id=season_id).join(Participant).all()
    return [roll.participant.name for roll in rolls]


def reset_season_roster(season_id):
    """
    Reset the season roster (delete all rolls for the season).

    Args:
        season_id: ID of the season to reset

    Returns:
        Boolean indicating success
    """
    try:
        Roll.query.filter_by(season_id=season_id).delete()
        db.session.commit()
        return True
    except Exception as e:  # pylint: disable=broad-exception-caught
        db.session.rollback()
        print(f"Error resetting season roster: {e}")
        return False
