"""
Database initialization and base model.
Sets up SQLAlchemy ORM for the application.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class BaseModel(db.Model):
    """Abstract base model with common fields for all models."""
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
