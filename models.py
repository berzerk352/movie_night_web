"""Database models for Movie Night Web application."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Season(db.Model):  # pylint: disable=too-few-public-methods
    """Represents a movie night season."""
    __tablename__ = 'seasons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    spreadsheet_tab = db.Column(db.String(100), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rolls = db.relationship('Roll', back_populates='season', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert Season object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'spreadsheet_tab': self.spreadsheet_tab,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Participant(db.Model):  # pylint: disable=too-few-public-methods
    """Represents a movie night participant."""
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rolls = db.relationship('Roll', back_populates='participant')

    def to_dict(self):
        """Convert Participant object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Roll(db.Model):  # pylint: disable=too-few-public-methods
    """Represents a single movie night roll/selection."""
    __tablename__ = 'rolls'

    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    movie_title = db.Column(db.String(255), nullable=False)
    roll_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tmdb_id = db.Column(db.Integer, nullable=True)
    tmdb_data = db.Column(db.JSON, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    season = db.relationship('Season', back_populates='rolls')
    participant = db.relationship('Participant', back_populates='rolls')

    def to_dict(self):
        """Convert Roll object to dictionary."""
        return {
            'id': self.id,
            'season_id': self.season_id,
            'participant_id': self.participant_id,
            'participant_name': self.participant.name if self.participant else None,
            'movie_title': self.movie_title,
            'roll_date': self.roll_date.isoformat() if self.roll_date else None,
            'tmdb_id': self.tmdb_id,
            'tmdb_data': self.tmdb_data,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
