# Deployment Guide for Render

This guide will help you deploy the Healthcare Robot application to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Cloudinary account with API credentials
3. Resend account with API key
4. Neon PostgreSQL database (already configured)

## Step 1: Prepare Environment Variables

Before deploying, gather all required environment variables:

### Required Environment Variables

```
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=postgresql://neondb_owner:npg_y1uxES0jbqQl@ep-small-bar-adgjjs7g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
CLOUDINARY_URL=cloudinary://<API_KEY>:<API_SECRET>@dlqutksgo
CLOUDINARY_CLOUD_NAME=dlqutksgo
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=onboarding@resend.dev
ADMIN_EMAIL=buxinhealth@gmail.com
ADMIN_PASSWORD=your-admin-password
FLASK_ENV=production
FLASK_DEBUG=false
```

## Step 2: Deploy to Render

### Option A: Using Render Dashboard

1. **Create a New Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use public Git repository)

2. **Configure the Service**
   - **Name**: `health-techbuxin` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: `Oregon` (or closest to your users)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or specify if needed)
   - **Build Command**: `pip install -r requirements.txt && python migrate.py`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

3. **Add Environment Variables**
   - Scroll down to "Environment Variables"
   - Add all the environment variables listed above
   - Click "Save Changes"

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for the build to complete (usually 2-5 minutes)

### Option B: Using render.yaml (Infrastructure as Code)

1. **Push render.yaml to your repository**
   - The `render.yaml` file is already configured
   - Commit and push to your repository

2. **Create Blueprint**
   - Go to https://dashboard.render.com/blueprints
   - Click "New Blueprint"
   - Connect your repository
   - Render will detect `render.yaml` and create the service

3. **Set Environment Variables**
   - After the blueprint is created, go to the service settings
   - Add all environment variables (they won't be synced from render.yaml for security)

## Step 3: Verify Deployment

1. **Check Health Endpoint**
   - Visit `https://your-app-name.onrender.com/health`
   - Should return `{"status": "healthy"}`

2. **Test the Application**
   - Visit your app URL
   - Test the contact form
   - Test the investor booking popup
   - Log in to admin panel at `/admin/login`

3. **Check Logs**
   - Go to your service dashboard
   - Click "Logs" tab
   - Verify no errors during startup

## Step 4: Database Migration

The migration script (`migrate.py`) runs automatically during build. If you need to run it manually:

1. **Via Render Shell**
   - Go to your service dashboard
   - Click "Shell" tab
   - Run: `python migrate.py`

2. **Via Local Connection**
   - Connect to your Neon database
   - Run the migration script locally with proper DATABASE_URL

## Step 5: Post-Deployment Configuration

### Cloudinary Setup

1. **Get Cloudinary Credentials**
   - Sign up at https://cloudinary.com
   - Go to Dashboard → Account Details
   - Copy API Key, API Secret, and Cloud Name

2. **Set Environment Variables**
   - `CLOUDINARY_URL`: `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`
   - `CLOUDINARY_CLOUD_NAME`: `dlqutksgo`
   - `CLOUDINARY_API_KEY`: Your API key
   - `CLOUDINARY_API_SECRET`: Your API secret

### Resend Email Setup

1. **Get Resend API Key**
   - Sign up at https://resend.com
   - Go to API Keys section
   - Create a new API key

2. **Verify Domain (Recommended)**
   - Go to Domains section
   - Add and verify your domain
   - Update `RESEND_FROM_EMAIL` to use your verified domain

3. **Set Environment Variables**
   - `RESEND_API_KEY`: Your API key
   - `RESEND_FROM_EMAIL`: Your verified email or `onboarding@resend.dev`

## Troubleshooting

### Build Fails

- Check build logs for specific errors
- Verify all dependencies in `requirements.txt`
- Ensure Python version is compatible (3.11+)

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Check SSL mode is set to `require`
- Ensure database is accessible from Render's IPs

### File Upload Issues

- Verify Cloudinary credentials are correct
- Check CLOUDINARY_URL format
- Review Cloudinary dashboard for upload logs

### Email Not Sending

- Verify Resend API key is correct
- Check domain verification status
- Review Resend dashboard for email logs
- Check spam folder (test emails often go to spam)

### Application Crashes

- Check application logs
- Verify all environment variables are set
- Ensure database migrations completed successfully
- Check for Python errors in logs

## Monitoring

### Health Checks

- Render automatically monitors `/health` endpoint
- Service will restart if health checks fail

### Logs

- View real-time logs in Render dashboard
- Logs are retained for 7 days on free tier

### Metrics

- Monitor CPU, memory, and response times
- Set up alerts for high error rates

## Security Best Practices

1. **Change Default Admin Password**
   - Set a strong `ADMIN_PASSWORD` in environment variables
   - Never commit passwords to repository

2. **Use Strong SECRET_KEY**
   - Generate a random secret key
   - Keep it secure and never commit to repository

3. **Enable HTTPS**
   - Render automatically provides HTTPS
   - Ensure all URLs use HTTPS

4. **Database Security**
   - Use connection pooling
   - Enable SSL for database connections
   - Regularly rotate credentials

## Scaling

### Horizontal Scaling

- Render supports multiple instances
- Update plan to enable auto-scaling

### Database Scaling

- Upgrade Neon database plan for more resources
- Monitor connection pool usage

## Backup and Recovery

### Database Backups

- Neon provides automatic backups
- Configure backup retention in Neon dashboard

### Application Backups

- Keep code in version control (Git)
- Document all environment variables
- Export database schema regularly

## Support

For issues:
1. Check Render documentation: https://render.com/docs
2. Check application logs
3. Review this deployment guide
4. Contact support if needed

