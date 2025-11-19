# app.py
import os
import json
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import datetime
import resend

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size (for videos)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'ogg', 'mov', 'avi'}

# Resend API configuration
RESEND_API_KEY = "re_6TQiKZ7r_K1H2FiwGNHJ4zh3WwmfmYbwb"
resend.api_key = RESEND_API_KEY

# Initialize Resend client (for newer versions of the library)
try:
    resend_client = resend.Resend(api_key=RESEND_API_KEY)
except (AttributeError, TypeError):
    # Fallback for older versions that don't support Resend() constructor
    resend_client = None

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Admin password (change this in production!)
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')  # Default password: admin123

def load_pages_data():
    """Load page data from JSON file."""
    try:
        with open('data/pages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_pages_data(data):
    """Save page data to JSON file."""
    with open('data/pages.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_investors_data():
    """Load investors booking data from JSON file."""
    try:
        with open('data/investors.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_investors_data(data):
    """Save investors booking data to JSON file."""
    with open('data/investors.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_contact_messages():
    """Load contact messages from JSON file."""
    try:
        with open('data/contact_messages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_contact_messages(data):
    """Save contact messages to JSON file."""
    with open('data/contact_messages.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_contact_info():
    """Get contact information from pages data."""
    pages_data = load_pages_data()
    return pages_data.get('contact_info', {
        'address': '1 Tesla Road, Austin, TX 78725, USA',
        'email': 'info@tesla.com',
        'phone': '+1 (512) 516-8177',
        'map_url': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3447.332309852891!2d-97.61868468487999!3d30.22744388181669!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8644b0d1b91350c3%3A0x651c633a5b6f707!2sTesla%20Giga%20Texas!5e0!3m2!1sen!2sus!4v1678888888888!5m2!1sen!2sus'
    })

def get_countries_list():
    """Get list of all countries for dropdown."""
    # Using a comprehensive list of countries
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

@app.route('/')
def home():
    """Serves the main page."""
    pages_data = load_pages_data()
    page_data = pages_data.get('index', {}) or {}
    site_settings = get_site_settings()
    return render_template('index.html', page_data=page_data, site_settings=site_settings)

@app.route('/problem')
def problem():
    """Serves the Problem page."""
    pages_data = load_pages_data()
    page_data = pages_data.get('problem', {}) or {}
    site_settings = get_site_settings()
    return render_template('problem.html', page_data=page_data, site_settings=site_settings)

@app.route('/solution')
def solution():
    """Serves the Solution page."""
    pages_data = load_pages_data()
    page_data = pages_data.get('solution', {}) or {}
    site_settings = get_site_settings()
    return render_template('solution.html', page_data=page_data, site_settings=site_settings)

@app.route('/methodology')
def methodology():
    """Serves the Methodology page."""
    pages_data = load_pages_data()
    page_data = pages_data.get('methodology', {}) or {}
    site_settings = get_site_settings()
    return render_template('methodology.html', page_data=page_data, site_settings=site_settings)

@app.route('/team')
def team():
    """Serves the Team page."""
    pages_data = load_pages_data()
    team_data = pages_data.get('team', {}).get('members', []) if pages_data.get('team') else []
    page_data = pages_data.get('team', {}) or {}
    site_settings = get_site_settings()
    return render_template('team.html', team=team_data, page_data=page_data, site_settings=site_settings)

class ContactForm(FlaskForm):
    name = StringField('Full Name', 
                       validators=[DataRequired("Please enter your name."), Length(min=2, max=100)])
    email = StringField('Email Address', 
                        validators=[DataRequired("Please enter your email."), Email("Please enter a valid email.")])
    subject = StringField('Subject', 
                          validators=[DataRequired("Please enter a subject."), Length(min=5, max=150)])
    message = TextAreaField('Message', 
                            validators=[DataRequired("Please enter a message."), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Serves the Contact page."""
    form = ContactForm()
    site_settings = get_site_settings()
    contact_info = get_contact_info()
    
    # This block runs when the user clicks "Send Message"
    if form.validate_on_submit():
        # This means the form is valid!
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data
        
        # Create message record
        message_record = {
            'id': str(datetime.now().timestamp()),
            'full_name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'submitted_at': datetime.now().isoformat(),
            'status': 'new'
        }
        
        # Save to file
        messages = load_contact_messages()
        messages.append(message_record)
        save_contact_messages(messages)
        
        # Get email settings
        from_email = site_settings.get('from_email', 'onboarding@resend.dev')
        admin_email = 'buxinhealth@gmail.com'
        
        # Send email to admin
        try:
            admin_email_html = f"""
            <h2>New Contact Form Message</h2>
            <p>You have received a new message from the contact form:</p>
            <ul>
                <li><strong>Full Name:</strong> {name}</li>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>Subject:</strong> {subject}</li>
                <li><strong>Date & Time:</strong> {message_record['submitted_at']}</li>
            </ul>
            <h3>Message:</h3>
            <p>{message.replace(chr(10), '<br>')}</p>
            <p>You can view and manage this message in the admin panel.</p>
            """
            
            if resend_client:
                try:
                    resend_client.emails.send({
                        "from": from_email,
                        "to": admin_email,
                        "subject": f"New Contact Form Message: {subject}",
                        "html": admin_email_html
                    })
                except:
                    resend.Emails.send({
                        "from": from_email,
                        "to": admin_email,
                        "subject": f"New Contact Form Message: {subject}",
                        "html": admin_email_html
                    })
            else:
                resend.Emails.send({
                    "from": from_email,
                    "to": admin_email,
                    "subject": f"New Contact Form Message: {subject}",
                    "html": admin_email_html
                })
        except Exception as e:
            print(f"Error sending admin email: {e}")
        
        # Send confirmation email to user
        try:
            user_email_html = f"""
            <h2>Thank You for Contacting Us</h2>
            <p>Dear {name},</p>
            <p>Thank you for contacting us. We have received your message and will get back to you soon.</p>
            <p><strong>Your Message:</strong></p>
            <p><em>{subject}</em></p>
            <p>Best regards,<br>Healthcare Robot Team</p>
            """
            
            if resend_client:
                try:
                    resend_client.emails.send({
                        "from": from_email,
                        "to": email,
                        "subject": "We Received Your Message",
                        "html": user_email_html
                    })
                except:
                    resend.Emails.send({
                        "from": from_email,
                        "to": email,
                        "subject": "We Received Your Message",
                        "html": user_email_html
                    })
            else:
                resend.Emails.send({
                    "from": from_email,
                    "to": email,
                    "subject": "We Received Your Message",
                    "html": user_email_html
                })
        except Exception as e:
            print(f"Error sending user confirmation email: {e}")
        
        # Give feedback to the user
        flash('Your message has been sent successfully.', 'success')
        return redirect(url_for('contact')) # Redirect to clear the form
    
    # This runs on a GET request (just loading the page)
    # or if the form validation failed
    return render_template('contact.html', form=form, site_settings=site_settings, contact_info=contact_info)

# Admin routes
class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmailForm(FlaskForm):
    to_email = StringField('To Email', 
                          validators=[DataRequired("Please enter recipient email."), Email("Please enter a valid email.")])
    subject = StringField('Subject', 
                         validators=[DataRequired("Please enter a subject."), Length(min=1, max=200)])
    html_content = TextAreaField('HTML Content', 
                                validators=[DataRequired("Please enter email content."), Length(min=1, max=10000)])
    submit = SubmitField('Send Email')

class InvestorBookingForm(FlaskForm):
    full_name = StringField('Full Name', 
                           validators=[DataRequired("Please enter your full name."), Length(min=2, max=100)])
    email = StringField('Email', 
                       validators=[DataRequired("Please enter your email."), Email("Please enter a valid email.")])
    phone = StringField('Phone Number', 
                       validators=[DataRequired("Please enter your phone number."), Length(min=10, max=20)])
    country = SelectField('Country', 
                         validators=[DataRequired("Please select your country.")])
    meeting_date = StringField('Meeting Date & Time', 
                              validators=[DataRequired("Please select a date and time.")])
    platform = SelectField('Meeting Platform', 
                          choices=[
                              ('google_meet', 'Google Meet'),
                              ('zoom', 'Zoom'),
                              ('whatsapp', 'WhatsApp'),
                              ('phone', 'Direct Phone Call')
                          ],
                          validators=[DataRequired("Please select a meeting platform.")])

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

def get_site_settings():
    """Get site settings from pages data."""
    pages_data = load_pages_data()
    return pages_data.get('site_settings', {
        'logo_type': 'text',
        'logo_text': 'HEALTHCARE ROBOT',
        'logo_image_url': '',
        'site_name': 'Healthcare Robot',
        'from_email': 'onboarding@resend.dev'  # Default to test domain
    })

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    pages_data = load_pages_data()
    site_settings = get_site_settings()
    return render_template('admin/dashboard.html', pages=pages_data, site_settings=site_settings)

@app.route('/admin/edit/<page_name>', methods=['GET', 'POST'])
@admin_required
def admin_edit_page(page_name):
    """Edit a specific page."""
    pages_data = load_pages_data()
    site_settings = get_site_settings()
    
    if page_name not in pages_data:
        flash('Page not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Handle form submission
        if page_name == 'team':
            # Handle team page separately
            members = []
            # Get all member indices, excluding deleted ones
            member_indices = set()
            for key in request.form.keys():
                if key.startswith('member_') and key.endswith('_name') and not key.startswith('deleted_'):
                    # Extract index from key like "member_0_name"
                    try:
                        index = int(key.split('_')[1])
                        member_indices.add(index)
                    except (ValueError, IndexError):
                        continue
            
            # Sort indices and create members
            for i in sorted(member_indices):
                name = request.form.get(f'member_{i}_name', '').strip()
                # Only add member if name is not empty (skip deleted/empty members)
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
            
            pages_data['team']['members'] = members
            pages_data['team']['header_title'] = request.form.get('header_title', '')
            pages_data['team']['header_description'] = request.form.get('header_description', '')
        else:
            # Handle other pages
            page_data = pages_data[page_name]
            
            # Update slider images
            if 'slider_images' in page_data:
                slider_images = []
                for i in range(10):  # Support up to 10 images
                    img_url = request.form.get(f'slider_image_{i}', '').strip()
                    if img_url:
                        slider_images.append(img_url)
                page_data['slider_images'] = slider_images
            
            # Update text fields
            for key in ['title', 'subtitle', 'description', 'footer_note', 'financing']:
                if key in request.form:
                    page_data[key] = request.form.get(key, '')
            
            # Update items (for problem, solution pages)
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
        
        save_pages_data(pages_data)
        flash('Page updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    page_data = pages_data[page_name]
    return render_template(f'admin/edit_{page_name}.html', page_name=page_name, page_data=page_data, site_settings=site_settings)

@app.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload():
    """Handle file uploads."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type: .{file_ext}. Allowed types: {", ".join(sorted(app.config["ALLOWED_EXTENSIONS"]))}'}), 400
        
        # Save file first, then check size
        filename = secure_filename(file.filename)
        # Handle duplicate filenames
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(filepath):
            filename = f"{base_name}_{counter}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        
        # Save the file
        file.save(filepath)
        
        # Check actual file size after saving
        actual_size = os.path.getsize(filepath)
        max_size = app.config['MAX_CONTENT_LENGTH']
        if actual_size > max_size:
            # Delete the file if it's too large
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'File too large. Maximum size: {max_size / (1024*1024):.0f}MB, your file: {actual_size / (1024*1024):.2f}MB'}), 400
        
        url = url_for('uploaded_file', filename=filename)
        return jsonify({'url': url})
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Upload error: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'error': f'Upload failed: {error_msg}'}), 500

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Edit site settings including logo."""
    pages_data = load_pages_data()
    
    if request.method == 'POST':
        # Update site settings
        if 'site_settings' not in pages_data:
            pages_data['site_settings'] = {}
        
        pages_data['site_settings']['logo_type'] = request.form.get('logo_type', 'text')
        pages_data['site_settings']['logo_text'] = request.form.get('logo_text', 'HEALTHCARE ROBOT')
        pages_data['site_settings']['logo_image_url'] = request.form.get('logo_image_url', '')
        pages_data['site_settings']['site_name'] = request.form.get('site_name', 'Healthcare Robot')
        pages_data['site_settings']['from_email'] = request.form.get('from_email', 'onboarding@resend.dev')
        
        save_pages_data(pages_data)
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
        try:
            to_email = form.to_email.data
            subject = form.subject.data
            html_content = form.html_content.data
            
            # Send email using Resend API
            print(f"Attempting to send email to {to_email}...")
            print(f"API Key: {RESEND_API_KEY[:10]}...")
            
            # Get the "from" email address from settings
            from_email = site_settings.get('from_email', 'onboarding@resend.dev')
            
            # Try using the client method first (newer API)
            if resend_client:
                try:
                    r = resend_client.emails.send({
                        "from": from_email,
                        "to": to_email,
                        "subject": subject,
                        "html": html_content
                    })
                except (AttributeError, TypeError) as e:
                    print(f"Client method failed, trying module-level API: {e}")
                    # Fallback to module-level API (older version)
                    r = resend.Emails.send({
                        "from": from_email,
                        "to": to_email,
                        "subject": subject,
                        "html": html_content
                    })
            else:
                # Use module-level API (older version)
                r = resend.Emails.send({
                    "from": from_email,
                    "to": to_email,
                    "subject": subject,
                    "html": html_content
                })
            
            # Check the response
            print(f"Resend API Response: {r}")
            print(f"Response type: {type(r)}")
            
            # Resend API returns a dict with 'id' key on success, or an object with .id attribute
            if r:
                # Handle dict response
                if isinstance(r, dict):
                    if 'id' in r:
                        email_id = r.get('id')
                        flash(f'Email sent successfully to {to_email}! (ID: {email_id})<br><small>⚠️ Check spam folder! Emails from test domains often get filtered. View status at <a href="https://resend.com/emails" target="_blank">Resend Dashboard</a></small>', 'success')
                        print(f"Email sent with ID: {email_id}")
                        print(f"⚠️ IMPORTANT: Email may be in spam folder. Check Resend dashboard: https://resend.com/emails")
                    elif 'error' in r:
                        error_msg = r.get('error', {}).get('message', 'Unknown error')
                        print(f"Resend API Error: {r}")
                        
                        # Check for specific Resend domain verification error
                        if "verify a domain" in error_msg.lower() or "testing emails" in error_msg.lower():
                            flash(f'<strong>Domain Verification Required:</strong><br>{error_msg}<br><br><strong>To fix this:</strong><ol style="margin: 10px 0; padding-left: 20px;"><li>Go to <a href="https://resend.com/domains" target="_blank">resend.com/domains</a> and verify your domain</li><li>Update the "From Email" address in <a href="{url_for("admin_settings")}">Site Settings</a> to use your verified domain (e.g., noreply@yourdomain.com)</li><li>Then try sending again</li></ol>', 'error')
                        else:
                            flash(f'Error sending email: {error_msg}', 'error')
                    else:
                        flash(f'Email sent successfully to {to_email}! Response: {r}', 'success')
                # Handle object response (newer SDK)
                elif hasattr(r, 'id'):
                    email_id = r.id
                    flash(f'Email sent successfully to {to_email}! (ID: {email_id})<br><small>⚠️ Check spam folder! Emails from test domains often get filtered. View status at <a href="https://resend.com/emails" target="_blank">Resend Dashboard</a></small>', 'success')
                    print(f"Email sent with ID: {email_id}")
                    print(f"⚠️ IMPORTANT: Email may be in spam folder. Check Resend dashboard: https://resend.com/emails")
                else:
                    flash(f'Email sent successfully to {to_email}! Response: {r}', 'success')
                    print(f"Unexpected response format: {r}")
            else:
                flash(f'No response from email service. Please check the console for details.', 'error')
                print(f"Empty response from Resend API")
            
            return redirect(url_for('admin_send_email'))
        except Exception as e:
            error_msg = str(e)
            print(f"Exception occurred: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Check for specific Resend domain verification error
            if "verify a domain" in error_msg.lower() or "testing emails" in error_msg.lower():
                flash(f'<strong>Domain Verification Required:</strong><br>{error_msg}<br><br><strong>To fix this:</strong><ol style="margin: 10px 0; padding-left: 20px;"><li>Go to <a href="https://resend.com/domains" target="_blank">resend.com/domains</a> and verify your domain</li><li>Update the "From Email" address in <a href="{url_for("admin_settings")}">Site Settings</a> to use your verified domain (e.g., noreply@yourdomain.com)</li><li>Then try sending again</li></ol>', 'error')
            else:
                flash(f'Error sending email: {error_msg}', 'error')
    
    return render_template('admin/send_email.html', form=form, site_settings=site_settings)

@app.route('/api/investor-booking', methods=['POST'])
def investor_booking():
    """Handle investor meeting booking submission."""
    try:
        data = request.get_json()
        
        # Debug logging
        print(f"Received booking data: {data}")
        
        if not data:
            print("Error: No JSON data received")
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone', 'country', 'meeting_date', 'platform']
        for field in required_fields:
            if field not in data or not data.get(field):
                error_msg = f'{field} is required'
                print(f"Validation error: {error_msg}")
                return jsonify({'success': False, 'error': error_msg}), 400
        
        # Validate email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            print(f"Validation error: Invalid email - {data['email']}")
            return jsonify({'success': False, 'error': 'Invalid email address'}), 400
        
        # Validate phone (basic validation - accept 7+ digits as some countries have shorter numbers)
        phone = re.sub(r'[^\d+]', '', str(data['phone']))
        if len(phone) < 7:
            print(f"Validation error: Invalid phone - {data['phone']} (cleaned: {phone})")
            return jsonify({'success': False, 'error': 'Invalid phone number (must be at least 7 digits)'}), 400
        
        # Create booking record
        booking = {
            'id': str(datetime.now().timestamp()),
            'full_name': data['full_name'],
            'email': data['email'],
            'phone': data['phone'],
            'country': data['country'],
            'meeting_date': data['meeting_date'],
            'platform': data['platform'],
            'submitted_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Save to file
        investors = load_investors_data()
        investors.append(booking)
        save_investors_data(investors)
        
        # Get site settings for email
        site_settings = get_site_settings()
        from_email = site_settings.get('from_email', 'onboarding@resend.dev')
        admin_email = 'buxinhealth@gmail.com'  # Admin email
        
        # Platform display names
        platform_names = {
            'google_meet': 'Google Meet',
            'zoom': 'Zoom',
            'whatsapp': 'WhatsApp',
            'phone': 'Direct Phone Call'
        }
        platform_name = platform_names.get(data['platform'], data['platform'])
        
        # Send email to admin
        try:
            admin_email_html = f"""
            <h2>New Investor Meeting Request</h2>
            <p>A new investor has requested a meeting:</p>
            <ul>
                <li><strong>Name:</strong> {data['full_name']}</li>
                <li><strong>Email:</strong> {data['email']}</li>
                <li><strong>Phone:</strong> {data['phone']}</li>
                <li><strong>Country:</strong> {data['country']}</li>
                <li><strong>Meeting Date & Time:</strong> {data['meeting_date']}</li>
                <li><strong>Platform:</strong> {platform_name}</li>
            </ul>
            <p>Please review this booking in the admin panel.</p>
            """
            
            if resend_client:
                try:
                    resend_client.emails.send({
                        "from": from_email,
                        "to": admin_email,
                        "subject": f"New Investor Meeting Request from {data['full_name']}",
                        "html": admin_email_html
                    })
                except:
                    resend.Emails.send({
                        "from": from_email,
                        "to": admin_email,
                        "subject": f"New Investor Meeting Request from {data['full_name']}",
                        "html": admin_email_html
                    })
            else:
                resend.Emails.send({
                    "from": from_email,
                    "to": admin_email,
                    "subject": f"New Investor Meeting Request from {data['full_name']}",
                    "html": admin_email_html
                })
        except Exception as e:
            print(f"Error sending admin email: {e}")
        
        # Send confirmation email to investor
        try:
            investor_email_html = f"""
            <h2>Meeting Request Confirmed</h2>
            <p>Dear {data['full_name']},</p>
            <p>Thank you for your interest! We have received your meeting request.</p>
            <h3>Your Meeting Details:</h3>
            <ul>
                <li><strong>Date & Time:</strong> {data['meeting_date']}</li>
                <li><strong>Platform:</strong> {platform_name}</li>
            </ul>
            <p>We will review your request and get back to you shortly to confirm the meeting details.</p>
            <p>Best regards,<br>Healthcare Robot Team</p>
            """
            
            if resend_client:
                try:
                    resend_client.emails.send({
                        "from": from_email,
                        "to": data['email'],
                        "subject": "Your Meeting Request Has Been Received",
                        "html": investor_email_html
                    })
                except:
                    resend.Emails.send({
                        "from": from_email,
                        "to": data['email'],
                        "subject": "Your Meeting Request Has Been Received",
                        "html": investor_email_html
                    })
            else:
                resend.Emails.send({
                    "from": from_email,
                    "to": data['email'],
                    "subject": "Your Meeting Request Has Been Received",
                    "html": investor_email_html
                })
        except Exception as e:
            print(f"Error sending investor confirmation email: {e}")
        
        return jsonify({'success': True, 'message': 'Thank you! Your meeting request has been received.'})
    
    except Exception as e:
        print(f"Error processing investor booking: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500

@app.route('/admin/investors')
@admin_required
def admin_investors():
    """Admin page to view all investor bookings."""
    investors = load_investors_data()
    site_settings = get_site_settings()
    # Sort by most recent first
    investors.reverse()
    return render_template('admin/investors.html', investors=investors, site_settings=site_settings)

@app.route('/api/countries')
def get_countries():
    """API endpoint to get list of countries."""
    return jsonify(get_countries_list())

@app.route('/admin/contact')
@admin_required
def admin_contact():
    """Admin page to view and manage contact messages."""
    messages = load_contact_messages()
    site_settings = get_site_settings()
    contact_info = get_contact_info()
    # Sort by most recent first
    messages.reverse()
    return render_template('admin/contact.html', messages=messages, site_settings=site_settings, contact_info=contact_info)

@app.route('/admin/contact/delete/<message_id>', methods=['POST'])
@admin_required
def admin_delete_contact_message(message_id):
    """Delete a contact message."""
    messages = load_contact_messages()
    messages = [msg for msg in messages if msg.get('id') != message_id]
    save_contact_messages(messages)
    flash('Message deleted successfully.', 'success')
    return redirect(url_for('admin_contact'))

def convert_place_url_to_embed(place_url):
    """Try to convert a Google Maps place URL to embed URL."""
    import re
    # Extract coordinates from place URL
    # Pattern: @lat,lng
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', place_url)
    if match:
        lat = match.group(1)
        lng = match.group(2)
        # Create embed URL with coordinates
        embed_url = f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3000!2d{lng}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzDCsDI4JzIyLjciTiA3N8KwMjknMDUuMyJF!5e0!3m2!1sen!2sus!4v1234567890123!5m2!1sen!2sus"
        return embed_url
    return None

@app.route('/admin/contact/info', methods=['GET', 'POST'])
@admin_required
def admin_contact_info():
    """Admin page to edit contact information."""
    pages_data = load_pages_data()
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        # Update contact info
        if 'contact_info' not in pages_data:
            pages_data['contact_info'] = {}
        
        pages_data['contact_info']['address'] = request.form.get('address', '')
        pages_data['contact_info']['email'] = request.form.get('email', '')
        pages_data['contact_info']['phone'] = request.form.get('phone', '')
        map_url = request.form.get('map_url', '').strip()
        
        # Check if it's a regular place URL and try to convert it
        if map_url and 'maps/place/' in map_url and 'maps/embed' not in map_url:
            # Try to extract coordinates and create embed URL
            import re
            match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', map_url)
            if match:
                lat = match.group(1)
                lng = match.group(2)
                # Extract place name if available
                place_match = re.search(r'/place/([^/@]+)', map_url)
                place_name = place_match.group(1).replace('+', ' ') if place_match else None
                
                # Create embed URL using coordinates (no API key needed)
                # Use a simple embed format that Google Maps accepts
                if place_name:
                    # Use place name for better results
                    encoded_place = place_name.replace(' ', '+').replace('/', '%2F')
                    # Simple embed URL format
                    map_url = f"https://www.google.com/maps?q={encoded_place}&output=embed"
                else:
                    # Use coordinates directly
                    map_url = f"https://www.google.com/maps?q={lat},{lng}&output=embed"
                
                flash(f'⚠️ Auto-converted place URL to embed URL. The map may not display perfectly. For best results, please: 1) Go to Google Maps, 2) Click "Share" → "Embed a map", 3) Copy the embed URL from there.', 'success')
            else:
                flash('❌ Could not extract coordinates from the URL. Please use the embed URL from Google Maps "Share → Embed a map" option, not a regular place URL.', 'error')
                return redirect(url_for('admin_contact_info'))
        
        pages_data['contact_info']['map_url'] = map_url
        
        save_pages_data(pages_data)
        flash('Contact information updated successfully!', 'success')
        return redirect(url_for('admin_contact_info'))
    
    contact_info = get_contact_info()
    return render_template('admin/contact_info.html', contact_info=contact_info, site_settings=site_settings)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)