"""Data models for Squishy."""
from datetime import datetime
from typing import Dict, List, Optional
from squishy.database import db
from sqlalchemy.orm import relationship

class MediaItem(db.Model):
    __tablename__ = 'media_items'
    
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512), nullable=False)
    year = db.Column(db.Integer)
    type = db.Column(db.String(50))
    poster_url = db.Column(db.String(512))
    overview = db.Column(db.Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'media_item',
        'polymorphic_on': type
    }
    
    # Common fields
    video_codec = db.Column(db.String(50))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration = db.Column(db.Float)
    size = db.Column(db.BigInteger)

    @property
    def display_name(self) -> str:
        if self.year:
            return f"{self.title} ({self.year})"
        return self.title

class Movie(MediaItem):
    __tablename__ = 'movies'
    id = db.Column(db.String(36), db.ForeignKey('media_items.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'movie',
    }

class Season:
    """Transient helper class for Season logic compatibility."""
    def __init__(self, number: int):
        self.number = number
        self.episodes = {} # Dict[int, Episode]

    @property
    def sorted_episodes(self):
        return sorted(self.episodes.values(), key=lambda e: e.episode_number or 0)

class TVShow(db.Model):
    __tablename__ = 'tv_shows'
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(255))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(512))
    overview = db.Column(db.Text)
    
    # Relationship to episodes
    # Note: Episode is a MediaItem. We need a way to link it.
    # Episode model has show_id (string). 
    # We can define a relationship using that foreign key logic, 
    # but since show_id column in Episode wasn't defined as FK in previous step, 
    # we need to be careful. 
    # Actually, in Episode model below, I define show_id.
    
    @property
    def seasons(self) -> Dict[int, Season]:
        """Group episodes by season."""
        # Query all episodes for this show
        episodes = Episode.query.filter_by(show_id=self.id).all()
        seasons_dict = {}
        for ep in episodes:
            s_num = ep.season_number
            if s_num not in seasons_dict:
                seasons_dict[s_num] = Season(s_num)
            seasons_dict[s_num].episodes[ep.episode_number] = ep
        return seasons_dict

    @property
    def sorted_seasons(self) -> List[Season]:
        return sorted(self.seasons.values(), key=lambda s: s.number)


class Episode(MediaItem):
    __tablename__ = 'episodes'
    id = db.Column(db.String(36), db.ForeignKey('media_items.id'), primary_key=True)
    season_number = db.Column(db.Integer)
    episode_number = db.Column(db.Integer)
    show_id = db.Column(db.String(36)) # Not strictly invalid to be loose fk
    
    __mapper_args__ = {
        'polymorphic_identity': 'episode',
    }

    @property
    def display_name(self) -> str:
        if self.episode_number:
            return f"S{self.season_number:02d}E{self.episode_number:02d} - {self.title}"
        return self.title


class TranscodeJob(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)
    media_id = db.Column(db.String(36), db.ForeignKey('media_items.id'))
    media = relationship("MediaItem", backref="jobs")
    
    preset_name = db.Column(db.String(50))
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    output_path = db.Column(db.String(512))
    error_message = db.Column(db.Text)
    ffmpeg_command = db.Column(db.Text)
    output_size = db.Column(db.String(50))
    
    progress = db.Column(db.Float, default=0.0)
    current_time = db.Column(db.Float, default=0.0)
    duration = db.Column(db.Float)
    
    ffmpeg_logs = db.Column(db.PickleType, default=[]) # Storing list of strings need pickle or JSON
    # Or just ignore logs persistence for now? 
    # pickle is easiest for list of strings.
    
    def to_dict(self):
        return {
            "id": self.id,
            "media_title": self.media.title if self.media else "Unknown",
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
