# app.py - Production-ready Flask application with database, Cloudinary, and email services
import os
import json
import logging
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and services
from models import db, ContactMessage, InvestorBooking, PageData, SiteSettings, ContactInfo, UploadedFile
from database import init_db
from cloudinary_service import get_cloudinary_service
from email_service import get_email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'ogg', 'mov', 'avi', 'pdf'}

# Initialize database
init_db(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Admin password hash
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123'))

# Helper functions
def get_countries_list():
    """Get list of all countries for dropdown."""
    countries = [
        'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France', 'Italy', 'Spain',
        'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Sweden', 'Norway', 'Denmark', 'Finland',
        'Poland', 'Portugal', 'Greece', 'Ireland', 'Czech Republic', 'Hungary', 'Romania', 'Bulgaria',
        'Croatia', 'Slovakia', 'Slovenia', 'Estonia', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
        'Cyprus', 'Japan', 'China', 'India', 'South Korea', 'Singapore', 'Hong Kong', 'Taiwan',
        'Thailand', 'Malaysia', 'Indonesia', 'Philippines', 'Vietnam', 'New Zealand', 'South Africa',
        'Brazil', 'Mexico', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Venezuela', 'Uruguay',
        'Ecuador', 'Panama', 'Costa Rica', 'Guatemala', 'Honduras', 'El Salvador', 'Nicaragua',
        'Dominican Republic', 'Jamaica', 'Trinidad and Tobago', 'Bahamas', 'Barbados', 'Belize',
        'Israel', 'United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Kuwait', 'Bahrain', 'Oman',
        'Jordan', 'Lebanon', 'Egypt', 'Turkey', 'Russia', 'Ukraine', 'Kazakhstan', 'Belarus',
        'Georgia', 'Armenia', 'Azerbaijan', 'Moldova', 'Albania', 'Bosnia and Herzegovina',
        'Serbia', 'Montenegro', 'North Macedonia', 'Kosovo', 'Iceland', 'Liechtenstein', 'Monaco',
        'San Marino', 'Andorra', 'Vatican City', 'Bangladesh', 'Pakistan', 'Sri Lanka', 'Nepal',
        'Bhutan', 'Myanmar', 'Cambodia', 'Laos', 'Mongolia', 'North Korea', 'Afghanistan',
        'Iran', 'Iraq', 'Syria', 'Yemen', 'Libya', 'Tunisia', 'Algeria', 'Morocco', 'Sudan',
        'Ethiopia', 'Kenya', 'Tanzania', 'Uganda', 'Ghana', 'Nigeria', 'Senegal', 'Ivory Coast',
        'Cameroon', 'Gabon', 'Angola', 'Mozambique', 'Madagascar', 'Mauritius', 'Seychelles',
        'Botswana', 'Namibia', 'Zimbabwe', 'Zambia', 'Malawi', 'Rwanda', 'Burundi', 'Djibouti',
        'Eritrea', 'Somalia', 'Chad', 'Niger', 'Mali', 'Burkina Faso', 'Guinea', 'Sierra Leone',
        'Liberia', 'Togo', 'Benin', 'Gambia', 'Guinea-Bissau', 'Cape Verde', 'São Tomé and Príncipe',
        'Equatorial Guinea', 'Central African Republic', 'Republic of the Congo', 'Democratic Republic of the Congo',
        'Other'
    ]
    return sorted(countries)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_video_url(url):
    """Check if URL is a video."""
    if not url:
        return False
    url_lower = url.lower()
    video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi']
    video_domains = ['youtube.com', 'youtu.be', 'vimeo.com']
    return any(url_lower.endswith(ext) for ext in video_extensions) or any(domain in url_lower for domain in video_domains)

@app.context_processor
def utility_processor():
    """Make utility functions available in templates."""
    return dict(is_video_url=is_video_url)

def admin_required(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Database helper functions
def get_page_data(page_name):
    """Get page data from database."""
    page = PageData.query.filter_by(page_name=page_name).first()
    if page:
        return page.content if isinstance(page.content, dict) else json.loads(page.content) if isinstance(page.content, str) else {}
    return {}

def save_page_data(page_name, content):
    """Save page data to database."""
    page = PageData.query.filter_by(page_name=page_name).first()
    if page:
        page.content = content
        page.updated_at = datetime.utcnow()
    else:
        page = PageData(page_name=page_name, content=content)
        db.session.add(page)
    db.session.commit()

def get_site_settings():
    """Get site settings from database."""
    settings = {}
    site_settings = SiteSettings.query.all()
    for setting in site_settings:
        try:
            value = json.loads(setting.value) if setting.value else None
        except:
            value = setting.value
        settings[setting.key] = value
    
    # Defaults
    defaults = {
        'logo_type': 'text',
        'logo_text': 'HEALTHCARE ROBOT',
        'logo_image_url': '',
        'site_name': 'Healthcare Robot',
        'from_email': os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
    }
    
    for key, default_value in defaults.items():
        if key not in settings:
            settings[key] = default_value
    
    return settings

def save_site_setting(key, value):
    """Save a site setting to database."""
    setting = SiteSettings.query.filter_by(key=key).first()
    if setting:
        setting.value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        setting.updated_at = datetime.utcnow()
    else:
        setting = SiteSettings(
            key=key,
            value=json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        )
        db.session.add(setting)
    db.session.commit()

def get_contact_info():
    """Get contact information from database."""
    contact = ContactInfo.query.first()
    if contact:
        return {
            'address': contact.address or '1 Tesla Road, Austin, TX 78725, USA',
            'email': contact.email or 'info@tesla.com',
            'phone': contact.phone or '+1 (512) 516-8177',
            'map_url': contact.map_url or 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3447.332309852891!2d-97.61868468487999!3d30.22744388181669!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8644b0d1b91350c3%3A0x651c633a5b6f707!2sTesla%20Giga%20Texas!5e0!3m2!1sen!2sus!4v1678888888888!5m2!1sen!2sus'
        }
    return {
        'address': '1 Tesla Road, Austin, TX 78725, USA',
        'email': 'info@tesla.com',
        'phone': '+1 (512) 516-8177',
        'map_url': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3447.332309852891!2d-97.61868468487999!3d30.22744388181669!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8644b0d1b91350c3%3A0x651c633a5b6f707!2sTesla%20Giga%20Texas!5e0!3m2!1sen!2sus!4v1678888888888!5m2!1sen!2sus'
    }

def save_contact_info(address, email, phone, map_url):
    """Save contact information to database."""
    contact = ContactInfo.query.first()
    if contact:
        contact.address = address
        contact.email = email
        contact.phone = phone
        contact.map_url = map_url
        contact.updated_at = datetime.utcnow()
    else:
        contact = ContactInfo(address=address, email=email, phone=phone, map_url=map_url)
        db.session.add(contact)
    db.session.commit()

# Routes
@app.route('/')
def home():
    """Serves the main page."""
    page_data = get_page_data('index')
    site_settings = get_site_settings()
    return render_template('index.html', page_data=page_data, site_settings=site_settings)

@app.route('/problem')
def problem():
    """Serves the Problem page."""
    page_data = get_page_data('problem')
    site_settings = get_site_settings()
    return render_template('problem.html', page_data=page_data, site_settings=site_settings)

@app.route('/solution')
def solution():
    """Serves the Solution page."""
    page_data = get_page_data('solution')
    site_settings = get_site_settings()
    return render_template('solution.html', page_data=page_data, site_settings=site_settings)

@app.route('/methodology')
def methodology():
    """Serves the Methodology page."""
    page_data = get_page_data('methodology')
    site_settings = get_site_settings()
    return render_template('methodology.html', page_data=page_data, site_settings=site_settings)

@app.route('/team')
def team():
    """Serves the Team page."""
    page_data = get_page_data('team')
    team_data = page_data.get('members', []) if page_data else []
    site_settings = get_site_settings()
    return render_template('team.html', team=team_data, page_data=page_data, site_settings=site_settings)

# Contact form
class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired("Please enter your name."), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired("Please enter your email."), Email("Please enter a valid email.")])
    subject = StringField('Subject', validators=[DataRequired("Please enter a subject."), Length(min=5, max=150)])
    message = TextAreaField('Message', validators=[DataRequired("Please enter a message."), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Serves the Contact page."""
    form = ContactForm()
    site_settings = get_site_settings()
    contact_info = get_contact_info()
    
    if form.validate_on_submit():
        # Create message record
        contact_message = ContactMessage(
            full_name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
            status='new'
        )
        db.session.add(contact_message)
        db.session.commit()
        
        # Send emails
        email_service = get_email_service()
        email_service.send_contact_notification(contact_message)
        email_service.send_contact_confirmation(contact_message, from_email=site_settings.get('from_email'))
        
        flash('Your message has been sent successfully.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form, site_settings=site_settings, contact_info=contact_info)

# Admin routes
class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmailForm(FlaskForm):
    to_email = StringField('To Email', validators=[DataRequired("Please enter recipient email."), Email("Please enter a valid email.")])
    subject = StringField('Subject', validators=[DataRequired("Please enter a subject."), Length(min=1, max=200)])
    html_content = TextAreaField('HTML Content', validators=[DataRequired("Please enter email content."), Length(min=1, max=10000)])
    submit = SubmitField('Send Email')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    form = LoginForm()
    if form.validate_on_submit():
        if check_password_hash(ADMIN_PASSWORD_HASH, form.password.data):
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password.', 'error')
    site_settings = get_site_settings()
    return render_template('admin/login.html', form=form, site_settings=site_settings)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    # Get all pages
    pages = {}
    page_list = PageData.query.all()
    for page in page_list:
        pages[page.page_name] = page.content if isinstance(page.content, dict) else json.loads(page.content) if isinstance(page.content, str) else {}
    
    site_settings = get_site_settings()
    return render_template('admin/dashboard.html', pages=pages, site_settings=site_settings)

@app.route('/admin/edit/<page_name>', methods=['GET', 'POST'])
@admin_required
def admin_edit_page(page_name):
    """Edit a specific page."""
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        page_data = get_page_data(page_name)
        
        if page_name == 'team':
            # Handle team page
            members = []
            member_indices = set()
            for key in request.form.keys():
                if key.startswith('member_') and key.endswith('_name') and not key.startswith('deleted_'):
                    try:
                        index = int(key.split('_')[1])
                        member_indices.add(index)
                    except (ValueError, IndexError):
                        continue
            
            for i in sorted(member_indices):
                name = request.form.get(f'member_{i}_name', '').strip()
                if name:
                    member = {
                        'name': name,
                        'title': request.form.get(f'member_{i}_title', '').strip(),
                        'bio': request.form.get(f'member_{i}_bio', '').strip(),
                        'image_url': request.form.get(f'member_{i}_image_url', '').strip(),
                        'linkedin': request.form.get(f'member_{i}_linkedin', '').strip() or None,
                        'twitter': request.form.get(f'member_{i}_twitter', '').strip() or None
                    }
                    members.append(member)
            
            page_data['members'] = members
            page_data['header_title'] = request.form.get('header_title', '')
            page_data['header_description'] = request.form.get('header_description', '')
        else:
            # Handle other pages
            if 'slider_images' in page_data:
                slider_images = []
                for i in range(10):
                    img_url = request.form.get(f'slider_image_{i}', '').strip()
                    if img_url:
                        slider_images.append(img_url)
                page_data['slider_images'] = slider_images
            
            for key in ['title', 'subtitle', 'description', 'footer_note', 'financing']:
                if key in request.form:
                    page_data[key] = request.form.get(key, '')
            
            if 'items' in page_data:
                items = []
                item_count = len([k for k in request.form.keys() if k.startswith('item_') and k.endswith('_title')])
                for i in range(item_count):
                    item = {
                        'icon': request.form.get(f'item_{i}_icon', ''),
                        'title': request.form.get(f'item_{i}_title', ''),
                        'description': request.form.get(f'item_{i}_description', '')
                    }
                    items.append(item)
                page_data['items'] = items
        
        save_page_data(page_name, page_data)
        flash('Page updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    page_data = get_page_data(page_name)
    if not page_data:
        flash('Page not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template(f'admin/edit_{page_name}.html', page_name=page_name, page_data=page_data, site_settings=site_settings)

@app.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload():
    """Handle file uploads to Cloudinary."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            return jsonify({'error': f'Invalid file type: .{file_ext}. Allowed types: {", ".join(sorted(app.config["ALLOWED_EXTENSIONS"]))}'}), 400
        
        # Upload to Cloudinary
        cloudinary_service = get_cloudinary_service()
        result = cloudinary_service.upload_any_file(file)
        
        if result.get('success'):
            # Save to database
            uploaded_file = UploadedFile(
                original_filename=file.filename,
                cloudinary_url=result['url'],
                cloudinary_public_id=result['public_id'],
                file_type=cloudinary_service.get_file_type(file.filename),
                file_size=result.get('bytes')
            )
            db.session.add(uploaded_file)
            db.session.commit()
            
            return jsonify({'url': result['url']})
        else:
            return jsonify({'error': result.get('error', 'Upload failed')}), 500
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Edit site settings including logo."""
    if request.method == 'POST':
        save_site_setting('logo_type', request.form.get('logo_type', 'text'))
        save_site_setting('logo_text', request.form.get('logo_text', 'HEALTHCARE ROBOT'))
        save_site_setting('logo_image_url', request.form.get('logo_image_url', ''))
        save_site_setting('site_name', request.form.get('site_name', 'Healthcare Robot'))
        save_site_setting('from_email', request.form.get('from_email', 'onboarding@resend.dev'))
        
        flash('Site settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    site_settings = get_site_settings()
    return render_template('admin/settings.html', site_settings=site_settings)

@app.route('/admin/send-email', methods=['GET', 'POST'])
@admin_required
def admin_send_email():
    """Admin page for sending emails to users."""
    form = EmailForm()
    site_settings = get_site_settings()
    
    if form.validate_on_submit():
        email_service = get_email_service()
        result = email_service.send_email(
            form.to_email.data,
            form.subject.data,
            form.html_content.data,
            from_email=site_settings.get('from_email')
        )
        
        if result.get('success'):
            flash(f'Email sent successfully to {form.to_email.data}! (ID: {result.get("email_id", "N/A")})', 'success')
        else:
            flash(f'Error sending email: {result.get("error", "Unknown error")}', 'error')
        
        return redirect(url_for('admin_send_email'))
    
    return render_template('admin/send_email.html', form=form, site_settings=site_settings)

@app.route('/api/investor-booking', methods=['POST'])
def investor_booking():
    """Handle investor meeting booking submission."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone', 'country', 'meeting_date', 'platform']
        for field in required_fields:
            if field not in data or not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'success': False, 'error': 'Invalid email address'}), 400
        
        # Validate phone
        phone = re.sub(r'[^\d+]', '', str(data['phone']))
        if len(phone) < 7:
            return jsonify({'success': False, 'error': 'Invalid phone number (must be at least 7 digits)'}), 400
        
        # Create booking record
        investor_booking = InvestorBooking(
            full_name=data['full_name'],
            email=data['email'],
            phone=data['phone'],
            country=data['country'],
            meeting_date=data['meeting_date'],
            platform=data['platform'],
            status='pending'
        )
        db.session.add(investor_booking)
        db.session.commit()
        
        # Send emails
        site_settings = get_site_settings()
        email_service = get_email_service()
        email_service.send_investor_notification(investor_booking)
        email_service.send_investor_confirmation(investor_booking, from_email=site_settings.get('from_email'))
        
        return jsonify({'success': True, 'message': 'Thank you! Your meeting request has been received.'})
    
    except Exception as e:
        logger.error(f"Error processing investor booking: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500

@app.route('/admin/investors')
@admin_required
def admin_investors():
    """Admin page to view all investor bookings."""
    investors = InvestorBooking.query.order_by(InvestorBooking.submitted_at.desc()).all()
    site_settings = get_site_settings()
    investors_data = [inv.to_dict() for inv in investors]
    return render_template('admin/investors.html', investors=investors_data, site_settings=site_settings)

@app.route('/api/countries')
def get_countries():
    """API endpoint to get list of countries."""
    return jsonify(get_countries_list())

@app.route('/admin/contact')
@admin_required
def admin_contact():
    """Admin page to view and manage contact messages."""
    messages = ContactMessage.query.order_by(ContactMessage.submitted_at.desc()).all()
    site_settings = get_site_settings()
    contact_info = get_contact_info()
    messages_data = [msg.to_dict() for msg in messages]
    return render_template('admin/contact.html', messages=messages_data, site_settings=site_settings, contact_info=contact_info)

@app.route('/admin/contact/delete/<int:message_id>', methods=['POST'])
@admin_required
def admin_delete_contact_message(message_id):
    """Delete a contact message."""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully.', 'success')
    return redirect(url_for('admin_contact'))

@app.route('/admin/contact/info', methods=['GET', 'POST'])
@admin_required
def admin_contact_info():
    """Admin page to edit contact information."""
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        address = request.form.get('address', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        map_url = request.form.get('map_url', '').strip()
        
        # Handle map URL conversion if needed
        if map_url and 'maps/place/' in map_url and 'maps/embed' not in map_url:
            import re
            match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', map_url)
            if match:
                lat = match.group(1)
                lng = match.group(2)
                place_match = re.search(r'/place/([^/@]+)', map_url)
                place_name = place_match.group(1).replace('+', ' ') if place_match else None
                
                if place_name:
                    encoded_place = place_name.replace(' ', '+').replace('/', '%2F')
                    map_url = f"https://www.google.com/maps?q={encoded_place}&output=embed"
                else:
                    map_url = f"https://www.google.com/maps?q={lat},{lng}&output=embed"
                
                flash('⚠️ Auto-converted place URL to embed URL. For best results, use the embed URL from Google Maps "Share → Embed a map" option.', 'success')
            else:
                flash('❌ Could not extract coordinates from the URL. Please use the embed URL from Google Maps.', 'error')
                return redirect(url_for('admin_contact_info'))
        
        save_contact_info(address, email, phone, map_url)
        flash('Contact information updated successfully!', 'success')
        return redirect(url_for('admin_contact_info'))
    
    contact_info = get_contact_info()
    return render_template('admin/contact_info.html', contact_info=contact_info, site_settings=site_settings)

# Health check endpoint for Render
@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

