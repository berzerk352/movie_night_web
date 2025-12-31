"""Database initialization and migration utilities."""
from models import db


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")


def reset_db(app):
    """Drop all tables and recreate them. USE WITH CAUTION!"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")


def seed_db(app):
    """Seed the database with initial data."""
    from models import Season, Participant
    from datetime import datetime
    
    with app.app_context():
        # Check if data already exists
        if Season.query.first() is not None:
            print("Database already contains data. Skipping seed.")
            return
        
        # Create initial season
        season = Season(
            name="Season 1",
            start_date=datetime.utcnow(),
            is_active=True,
            spreadsheet_tab="General"
        )
        db.session.add(season)
        
        # Create some example participants (optional)
        # participants = ['Alice', 'Bob', 'Charlie']
        # for name in participants:
        #     participant = Participant(name=name)
        #     db.session.add(participant)
        
        db.session.commit()
        print("Database seeded successfully!")
