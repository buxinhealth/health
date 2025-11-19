"""Migration script to migrate data from JSON files to PostgreSQL database."""
import os
import json
from datetime import datetime
from app import app
from models import db, ContactMessage, InvestorBooking, PageData, SiteSettings, ContactInfo
from database import init_db

def load_json_file(filepath):
    """Load JSON file, return empty list/dict if not found."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return {} if 'pages' in filepath or 'contact_info' in filepath else []

def migrate_contact_messages():
    """Migrate contact messages from JSON to database."""
    print("Migrating contact messages...")
    messages = load_json_file('data/contact_messages.json')
    
    migrated = 0
    for msg in messages:
        try:
            # Check if already exists
            existing = ContactMessage.query.filter_by(
                email=msg.get('email'),
                subject=msg.get('subject'),
                submitted_at=datetime.fromisoformat(msg.get('submitted_at')) if msg.get('submitted_at') else None
            ).first()
            
            if not existing:
                contact_msg = ContactMessage(
                    full_name=msg.get('full_name', ''),
                    email=msg.get('email', ''),
                    subject=msg.get('subject', ''),
                    message=msg.get('message', ''),
                    status=msg.get('status', 'new'),
                    submitted_at=datetime.fromisoformat(msg.get('submitted_at')) if msg.get('submitted_at') else datetime.utcnow()
                )
                db.session.add(contact_msg)
                migrated += 1
        except Exception as e:
            print(f"Error migrating contact message: {e}")
            continue
    
    db.session.commit()
    print(f"Migrated {migrated} contact messages")

def migrate_investor_bookings():
    """Migrate investor bookings from JSON to database."""
    print("Migrating investor bookings...")
    bookings = load_json_file('data/investors.json')
    
    migrated = 0
    for booking in bookings:
        try:
            # Check if already exists
            existing = InvestorBooking.query.filter_by(
                email=booking.get('email'),
                meeting_date=booking.get('meeting_date'),
                submitted_at=datetime.fromisoformat(booking.get('submitted_at')) if booking.get('submitted_at') else None
            ).first()
            
            if not existing:
                investor_booking = InvestorBooking(
                    full_name=booking.get('full_name', ''),
                    email=booking.get('email', ''),
                    phone=booking.get('phone', ''),
                    country=booking.get('country', ''),
                    meeting_date=booking.get('meeting_date', ''),
                    platform=booking.get('platform', ''),
                    status=booking.get('status', 'pending'),
                    submitted_at=datetime.fromisoformat(booking.get('submitted_at')) if booking.get('submitted_at') else datetime.utcnow()
                )
                db.session.add(investor_booking)
                migrated += 1
        except Exception as e:
            print(f"Error migrating investor booking: {e}")
            continue
    
    db.session.commit()
    print(f"Migrated {migrated} investor bookings")

def migrate_pages_data():
    """Migrate pages data from JSON to database."""
    print("Migrating pages data...")
    pages_data = load_json_file('data/pages.json')
    
    migrated = 0
    for page_name, page_content in pages_data.items():
        if page_name == 'site_settings' or page_name == 'contact_info':
            continue  # Handle separately
        
        try:
            # Check if already exists
            existing = PageData.query.filter_by(page_name=page_name).first()
            
            if existing:
                # Update existing
                existing.content = page_content
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                page_data = PageData(
                    page_name=page_name,
                    content=page_content
                )
                db.session.add(page_data)
                migrated += 1
        except Exception as e:
            print(f"Error migrating page {page_name}: {e}")
            continue
    
    db.session.commit()
    print(f"Migrated {migrated} pages")

def migrate_site_settings():
    """Migrate site settings from JSON to database."""
    print("Migrating site settings...")
    pages_data = load_json_file('data/pages.json')
    site_settings = pages_data.get('site_settings', {})
    
    migrated = 0
    for key, value in site_settings.items():
        try:
            # Check if already exists
            existing = SiteSettings.query.filter_by(key=key).first()
            
            if existing:
                # Update existing
                existing.value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                setting = SiteSettings(
                    key=key,
                    value=json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                )
                db.session.add(setting)
                migrated += 1
        except Exception as e:
            print(f"Error migrating setting {key}: {e}")
            continue
    
    db.session.commit()
    print(f"Migrated {migrated} site settings")

def migrate_contact_info():
    """Migrate contact info from JSON to database."""
    print("Migrating contact info...")
    pages_data = load_json_file('data/pages.json')
    contact_info = pages_data.get('contact_info', {})
    
    if contact_info:
        try:
            # Check if already exists
            existing = ContactInfo.query.first()
            
            if existing:
                # Update existing
                existing.address = contact_info.get('address', '')
                existing.email = contact_info.get('email', '')
                existing.phone = contact_info.get('phone', '')
                existing.map_url = contact_info.get('map_url', '')
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                contact = ContactInfo(
                    address=contact_info.get('address', ''),
                    email=contact_info.get('email', ''),
                    phone=contact_info.get('phone', ''),
                    map_url=contact_info.get('map_url', '')
                )
                db.session.add(contact)
            
            db.session.commit()
            print("Migrated contact info")
        except Exception as e:
            print(f"Error migrating contact info: {e}")

def run_migration():
    """Run all migrations."""
    print("Starting migration from JSON to PostgreSQL...")
    
    with app.app_context():
        # Initialize database
        init_db(app)
        
        # Run migrations
        migrate_contact_messages()
        migrate_investor_bookings()
        migrate_pages_data()
        migrate_site_settings()
        migrate_contact_info()
        
        print("\nMigration completed!")

if __name__ == '__main__':
    run_migration()

