"""Cloudinary service for file uploads and management."""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import logging

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Service for handling Cloudinary file operations."""
    
    def __init__(self):
        """Initialize Cloudinary with credentials from environment."""
        cloudinary_url = os.getenv('CLOUDINARY_URL')
        if not cloudinary_url:
            raise ValueError("CLOUDINARY_URL environment variable is not set")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dlqutksgo'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        # Parse CLOUDINARY_URL if provided (format: cloudinary://api_key:api_secret@cloud_name)
        if cloudinary_url.startswith('cloudinary://'):
            try:
                # Extract credentials from URL
                url_parts = cloudinary_url.replace('cloudinary://', '').split('@')
                if len(url_parts) == 2:
                    credentials = url_parts[0].split(':')
                    cloud_name = url_parts[1]
                    if len(credentials) == 2:
                        api_key, api_secret = credentials
                        cloudinary.config(
                            cloud_name=cloud_name,
                            api_key=api_key,
                            api_secret=api_secret
                        )
            except Exception as e:
                logger.warning(f"Could not parse CLOUDINARY_URL: {e}")
    
    def get_file_type(self, filename):
        """Determine file type from filename."""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        image_exts = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'ico'}
        video_exts = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'flv', 'wmv'}
        pdf_exts = {'pdf'}
        
        if ext in image_exts:
            return 'image'
        elif ext in video_exts:
            return 'video'
        elif ext in pdf_exts:
            return 'pdf'
        else:
            return 'other'
    
    def upload_file(self, file, folder='uploads', resource_type='auto', **options):
        """
        Upload a file to Cloudinary.
        
        Args:
            file: File object or file path
            folder: Cloudinary folder to upload to
            resource_type: 'image', 'video', 'raw', or 'auto'
            **options: Additional Cloudinary upload options
        
        Returns:
            dict with 'url', 'public_id', 'secure_url', and other Cloudinary response data
        """
        try:
            # Determine resource type if auto
            if resource_type == 'auto':
                if hasattr(file, 'filename'):
                    filename = file.filename
                elif isinstance(file, str):
                    filename = file
                else:
                    filename = 'file'
                
                file_type = self.get_file_type(filename)
                if file_type == 'image':
                    resource_type = 'image'
                elif file_type == 'video':
                    resource_type = 'video'
                else:
                    resource_type = 'raw'
            
            # Prepare upload options
            upload_options = {
                'folder': folder,
                'use_filename': True,
                'unique_filename': True,
                'overwrite': False,
                **options
            }
            
            # Upload file
            if hasattr(file, 'read'):
                # File object
                result = cloudinary.uploader.upload(
                    file,
                    resource_type=resource_type,
                    **upload_options
                )
            elif isinstance(file, str):
                # File path
                result = cloudinary.uploader.upload(
                    file,
                    resource_type=resource_type,
                    **upload_options
                )
            else:
                raise ValueError("Invalid file type. Must be file object or file path.")
            
            # Return standardized response
            return {
                'success': True,
                'url': result.get('secure_url') or result.get('url'),
                'public_id': result.get('public_id'),
                'format': result.get('format'),
                'width': result.get('width'),
                'height': result.get('height'),
                'bytes': result.get('bytes'),
                'resource_type': result.get('resource_type'),
                'created_at': result.get('created_at'),
                'raw': result  # Include full response
            }
        
        except Exception as e:
            logger.error(f"Error uploading file to Cloudinary: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, public_id, resource_type='image'):
        """
        Delete a file from Cloudinary.
        
        Args:
            public_id: Cloudinary public ID of the file
            resource_type: 'image', 'video', or 'raw'
        
        Returns:
            dict with 'success' and 'result' or 'error'
        """
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type
            )
            
            if result.get('result') == 'ok':
                return {
                    'success': True,
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('result', 'Unknown error')
                }
        
        except Exception as e:
            logger.error(f"Error deleting file from Cloudinary: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_url(self, public_id, resource_type='image', transformation=None):
        """
        Get Cloudinary URL for a file with optional transformations.
        
        Args:
            public_id: Cloudinary public ID
            resource_type: 'image', 'video', or 'raw'
            transformation: Dict of transformation options
        
        Returns:
            URL string
        """
        try:
            url, options = cloudinary_url(
                public_id,
                resource_type=resource_type,
                transformation=transformation
            )
            return url
        except Exception as e:
            logger.error(f"Error generating Cloudinary URL: {e}")
            return None
    
    def upload_image(self, file, folder='uploads/images', **options):
        """Upload an image file."""
        return self.upload_file(file, folder=folder, resource_type='image', **options)
    
    def upload_video(self, file, folder='uploads/videos', **options):
        """Upload a video file."""
        return self.upload_file(file, folder=folder, resource_type='video', **options)
    
    def upload_pdf(self, file, folder='uploads/pdfs', **options):
        """Upload a PDF file."""
        return self.upload_file(file, folder=folder, resource_type='raw', **options)
    
    def upload_any_file(self, file, folder='uploads/files', **options):
        """Upload any file type (auto-detect)."""
        return self.upload_file(file, folder=folder, resource_type='auto', **options)

# Global instance
_cloudinary_service = None

def get_cloudinary_service():
    """Get or create Cloudinary service instance."""
    global _cloudinary_service
    if _cloudinary_service is None:
        _cloudinary_service = CloudinaryService()
    return _cloudinary_service

