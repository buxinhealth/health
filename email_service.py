"""Email service for sending emails via Resend."""
import os
import resend
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via Resend API."""
    
    def __init__(self):
        """Initialize Resend client with API key from environment."""
        api_key = os.getenv('RESEND_API_KEY')
        if not api_key:
            raise ValueError("RESEND_API_KEY environment variable is not set")
        
        resend.api_key = api_key
        
        # Try to initialize Resend client (newer versions)
        try:
            self.resend_client = resend.Resend(api_key=api_key)
        except (AttributeError, TypeError):
            self.resend_client = None
    
    def send_email(self, to_email, subject, html_content, from_email=None):
        """
        Send an email via Resend.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email (defaults to env variable or default)
        
        Returns:
            dict with 'success', 'email_id' or 'error'
        """
        try:
            # Get from email
            if not from_email:
                from_email = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
            
            # Send email
            if self.resend_client:
                try:
                    result = self.resend_client.emails.send({
                        "from": from_email,
                        "to": to_email,
                        "subject": subject,
                        "html": html_content
                    })
                except (AttributeError, TypeError):
                    # Fallback to module-level API
                    result = resend.Emails.send({
                        "from": from_email,
                        "to": to_email,
                        "subject": subject,
                        "html": html_content
                    })
            else:
                result = resend.Emails.send({
                    "from": from_email,
                    "to": to_email,
                    "subject": subject,
                    "html": html_content
                })
            
            # Extract email ID from result
            email_id = None
            if isinstance(result, dict):
                email_id = result.get('id')
            elif hasattr(result, 'id'):
                email_id = result.id
            
            return {
                'success': True,
                'email_id': email_id,
                'result': result
            }
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_contact_notification(self, contact_message, admin_email=None):
        """
        Send notification email to admin about new contact message.
        
        Args:
            contact_message: ContactMessage object or dict
            admin_email: Admin email address (defaults to env variable)
        
        Returns:
            dict with 'success' and 'email_id' or 'error'
        """
        if not admin_email:
            admin_email = os.getenv('ADMIN_EMAIL', 'buxinhealth@gmail.com')
        
        # Extract data
        if hasattr(contact_message, 'to_dict'):
            data = contact_message.to_dict()
        else:
            data = contact_message
        
        # Create HTML email
        html_content = f"""
        <h2>New Contact Form Message</h2>
        <p>You have received a new message from the contact form:</p>
        <ul>
            <li><strong>Full Name:</strong> {data.get('full_name', 'N/A')}</li>
            <li><strong>Email:</strong> {data.get('email', 'N/A')}</li>
            <li><strong>Subject:</strong> {data.get('subject', 'N/A')}</li>
            <li><strong>Date & Time:</strong> {data.get('submitted_at', 'N/A')}</li>
        </ul>
        <h3>Message:</h3>
        <p>{data.get('message', '').replace(chr(10), '<br>')}</p>
        <p>You can view and manage this message in the admin panel.</p>
        """
        
        subject = f"New Contact Form Message: {data.get('subject', 'No Subject')}"
        
        return self.send_email(admin_email, subject, html_content)
    
    def send_contact_confirmation(self, contact_message, from_email=None):
        """
        Send confirmation email to user after contact form submission.
        
        Args:
            contact_message: ContactMessage object or dict
            from_email: Sender email (defaults to env variable)
        
        Returns:
            dict with 'success' and 'email_id' or 'error'
        """
        # Extract data
        if hasattr(contact_message, 'to_dict'):
            data = contact_message.to_dict()
        else:
            data = contact_message
        
        # Create HTML email
        html_content = f"""
        <h2>Thank You for Contacting Us</h2>
        <p>Dear {data.get('full_name', 'Valued Customer')},</p>
        <p>Thank you for contacting us. We have received your message and will get back to you soon.</p>
        <p><strong>Your Message:</strong></p>
        <p><em>{data.get('subject', 'No Subject')}</em></p>
        <p>Best regards,<br>Healthcare Robot Team</p>
        """
        
        subject = "We Received Your Message"
        user_email = data.get('email')
        
        if not user_email:
            return {
                'success': False,
                'error': 'No email address provided'
            }
        
        return self.send_email(user_email, subject, html_content, from_email=from_email)
    
    def send_investor_notification(self, investor_booking, admin_email=None):
        """
        Send notification email to admin about new investor meeting request.
        
        Args:
            investor_booking: InvestorBooking object or dict
            admin_email: Admin email address (defaults to env variable)
        
        Returns:
            dict with 'success' and 'email_id' or 'error'
        """
        if not admin_email:
            admin_email = os.getenv('ADMIN_EMAIL', 'buxinhealth@gmail.com')
        
        # Extract data
        if hasattr(investor_booking, 'to_dict'):
            data = investor_booking.to_dict()
        else:
            data = investor_booking
        
        # Platform display names
        platform_names = {
            'google_meet': 'Google Meet',
            'zoom': 'Zoom',
            'whatsapp': 'WhatsApp',
            'phone': 'Direct Phone Call'
        }
        platform_name = platform_names.get(data.get('platform', ''), data.get('platform', 'N/A'))
        
        # Create HTML email
        html_content = f"""
        <h2>New Investor Meeting Request</h2>
        <p>A new investor has requested a meeting:</p>
        <ul>
            <li><strong>Name:</strong> {data.get('full_name', 'N/A')}</li>
            <li><strong>Email:</strong> {data.get('email', 'N/A')}</li>
            <li><strong>Phone:</strong> {data.get('phone', 'N/A')}</li>
            <li><strong>Country:</strong> {data.get('country', 'N/A')}</li>
            <li><strong>Meeting Date & Time:</strong> {data.get('meeting_date', 'N/A')}</li>
            <li><strong>Platform:</strong> {platform_name}</li>
        </ul>
        <p>Please review this booking in the admin panel.</p>
        """
        
        subject = f"New Investor Meeting Request from {data.get('full_name', 'Investor')}"
        
        return self.send_email(admin_email, subject, html_content)
    
    def send_investor_confirmation(self, investor_booking, from_email=None):
        """
        Send confirmation email to investor after meeting request submission.
        
        Args:
            investor_booking: InvestorBooking object or dict
            from_email: Sender email (defaults to env variable)
        
        Returns:
            dict with 'success' and 'email_id' or 'error'
        """
        # Extract data
        if hasattr(investor_booking, 'to_dict'):
            data = investor_booking.to_dict()
        else:
            data = investor_booking
        
        # Platform display names
        platform_names = {
            'google_meet': 'Google Meet',
            'zoom': 'Zoom',
            'whatsapp': 'WhatsApp',
            'phone': 'Direct Phone Call'
        }
        platform_name = platform_names.get(data.get('platform', ''), data.get('platform', 'N/A'))
        
        # Create HTML email
        html_content = f"""
        <h2>Meeting Request Confirmed</h2>
        <p>Dear {data.get('full_name', 'Valued Investor')},</p>
        <p>Thank you for your interest! We have received your meeting request.</p>
        <h3>Your Meeting Details:</h3>
        <ul>
            <li><strong>Date & Time:</strong> {data.get('meeting_date', 'N/A')}</li>
            <li><strong>Platform:</strong> {platform_name}</li>
        </ul>
        <p>We will review your request and get back to you shortly to confirm the meeting details.</p>
        <p>Best regards,<br>Healthcare Robot Team</p>
        """
        
        subject = "Your Meeting Request Has Been Received"
        investor_email = data.get('email')
        
        if not investor_email:
            return {
                'success': False,
                'error': 'No email address provided'
            }
        
        return self.send_email(investor_email, subject, html_content, from_email=from_email)

# Global instance
_email_service = None

def get_email_service():
    """Get or create Email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

