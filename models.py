"""Database models for the application."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Text
import json

db = SQLAlchemy()

class ContactMessage(db.Model):
    """Model for contact form messages."""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, read, replied, archived
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class InvestorBooking(db.Model):
    """Model for investor meeting bookings."""
    __tablename__ = 'investor_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    meeting_date = db.Column(db.String(50), nullable=False)  # Store as string for flexibility
    platform = db.Column(db.String(50), nullable=False)  # google_meet, zoom, whatsapp, phone
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'country': self.country,
            'meeting_date': self.meeting_date,
            'platform': self.platform,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PageData(db.Model):
    """Model for storing page content data."""
    __tablename__ = 'page_data'
    
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(50), unique=True, nullable=False)  # index, problem, solution, etc.
    content = db.Column(JSON, nullable=False)  # Store page data as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_name': self.page_name,
            'content': self.content if isinstance(self.content, dict) else json.loads(self.content) if isinstance(self.content, str) else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SiteSettings(db.Model):
    """Model for site-wide settings."""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ContactInfo(db.Model):
    """Model for contact information."""
    __tablename__ = 'contact_info'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(Text, nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    map_url = db.Column(Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'map_url': self.map_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UploadedFile(db.Model):
    """Model for tracking uploaded files in Cloudinary."""
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    cloudinary_url = db.Column(Text, nullable=False)
    cloudinary_public_id = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, video, pdf, other
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'cloudinary_url': self.cloudinary_url,
            'cloudinary_public_id': self.cloudinary_public_id,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

