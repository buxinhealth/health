# Healthcare Robot - Production Deployment System

Complete production-ready Flask application with Neon PostgreSQL, Cloudinary file storage, and Resend email integration, deployed on Render.

## 🚀 Features

- **Database**: Neon PostgreSQL with connection pooling and automatic reconnection
- **File Storage**: Cloudinary integration for images, videos, and PDFs
- **Email System**: Resend integration for admin notifications and user confirmations
- **Admin Panel**: Full admin interface for managing content, messages, and bookings
- **Contact Form**: User-friendly contact form with email notifications
- **Investor Booking**: Meeting request system with calendar picker
- **Production Ready**: Optimized for Render deployment with health checks

## 📋 Prerequisites

- Python 3.11+
- Neon PostgreSQL database
- Cloudinary account
- Resend account
- Render account (for deployment)

## 🛠️ Local Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd health.techbuxin.com
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `env.example` to `.env` and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://...
CLOUDINARY_URL=cloudinary://...
RESEND_API_KEY=your-resend-api-key
ADMIN_PASSWORD=your-admin-password
```

### 4. Initialize Database

```bash
python migrate.py
```

This will:
- Create all database tables
- Migrate existing JSON data to PostgreSQL (if any)

### 5. Run the Application

```bash
python app.py
```

Or with gunicorn for production:

```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
.
├── app.py                 # Main Flask application
├── models.py              # Database models
├── database.py            # Database configuration and connection management
├── cloudinary_service.py  # Cloudinary file upload service
├── email_service.py       # Resend email service
├── migrate.py             # Database migration script
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment configuration
├── render.yaml           # Render infrastructure as code
├── runtime.txt           # Python version specification
├── env.example           # Environment variables template
├── DEPLOYMENT.md         # Detailed deployment guide
├── templates/            # Jinja2 templates
│   ├── admin/           # Admin panel templates
│   ├── base.html        # Base template
│   ├── contact.html     # Contact page
│   └── ...
└── static/              # Static files (CSS, JS, images)
```

## 🗄️ Database Schema

### Tables

- **contact_messages**: Contact form submissions
- **investor_bookings**: Investor meeting requests
- **page_data**: Page content (JSON storage)
- **site_settings**: Site-wide settings
- **contact_info**: Contact information
- **uploaded_files**: Cloudinary file references

## 🔧 Configuration

### Database (Neon PostgreSQL)

The application uses Neon PostgreSQL with:
- Connection pooling
- SSL encryption
- Automatic reconnection
- Connection timeout handling

### Cloudinary

Configured for:
- Image uploads (PNG, JPG, GIF, WebP, etc.)
- Video uploads (MP4, WebM, MOV, etc.)
- PDF uploads
- Automatic file type detection
- Secure file storage

### Email (Resend)

Integrated for:
- Contact form notifications
- Investor booking confirmations
- Admin notifications
- User confirmations

## 🚀 Deployment to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Deploy!

The `render.yaml` file contains all necessary configuration.

## 📝 Admin Panel

Access the admin panel at `/admin/login`

Default credentials:
- Password: Set via `ADMIN_PASSWORD` environment variable (default: `admin123`)

**⚠️ Change the default password in production!**

### Admin Features

- **Dashboard**: Overview of all pages and content
- **Page Editor**: Edit page content (Home, Problem, Solution, Team, etc.)
- **Contact Management**: View and manage contact form messages
- **Investor Bookings**: View and manage meeting requests
- **Site Settings**: Configure logo, site name, email settings
- **File Upload**: Upload images/videos to Cloudinary
- **Email Sender**: Send custom emails to users

## 🔒 Security Features

- Password hashing for admin authentication
- CSRF protection (Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)
- Secure file upload validation
- Environment variable configuration
- SSL/TLS for database connections

## 📧 Email Templates

The application sends automated emails for:

1. **Contact Form Submission**
   - Admin notification with message details
   - User confirmation email

2. **Investor Meeting Request**
   - Admin notification with booking details
   - Investor confirmation email

## 🧪 Testing

### Health Check

```bash
curl http://localhost:5000/health
```

Should return: `{"status": "healthy"}`

### Test Contact Form

1. Visit `/contact`
2. Fill out the form
3. Submit
4. Check admin panel for message
5. Verify emails were sent

### Test Investor Booking

1. Click "Investors are Invited" button
2. Fill out the booking form
3. Submit
4. Check admin panel for booking
5. Verify emails were sent

## 🐛 Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Check SSL mode is set to `require`
- Ensure database is accessible

### File Upload Issues

- Verify Cloudinary credentials
- Check `CLOUDINARY_URL` format
- Review file size limits

### Email Not Sending

- Verify Resend API key
- Check domain verification
- Review Resend dashboard logs

## 📚 API Endpoints

- `GET /` - Home page
- `GET /contact` - Contact page
- `POST /contact` - Submit contact form
- `POST /api/investor-booking` - Submit investor booking
- `GET /api/countries` - Get countries list
- `GET /health` - Health check
- `GET /admin` - Admin dashboard (requires login)
- `POST /admin/upload` - Upload file to Cloudinary

## 🔄 Migration from JSON to Database

The `migrate.py` script automatically migrates existing JSON data:

- Contact messages from `data/contact_messages.json`
- Investor bookings from `data/investors.json`
- Page data from `data/pages.json`
- Site settings and contact info

Run migration:
```bash
python migrate.py
```

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
2. Review application logs
3. Check Render dashboard for service status

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- Flask for the web framework
- Neon for PostgreSQL hosting
- Cloudinary for file storage
- Resend for email delivery
- Render for hosting platform

