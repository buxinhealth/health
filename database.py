"""Database configuration and connection management for Neon PostgreSQL."""
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError
import time
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variable."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url

def configure_database_url_for_pooling(database_url):
    """
    Configure database URL for connection pooling.
    Neon requires specific connection parameters for pooling.
    """
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    
    # Ensure SSL mode is required
    query_params['sslmode'] = ['require']
    
    # Add connection pooling parameters
    if 'pooler' not in parsed.hostname:
        # If not using pooler, we should use direct connection with proper settings
        query_params['connect_timeout'] = ['10']
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)

def create_db_engine(database_url=None, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600):
    """
    Create SQLAlchemy engine with connection pooling and reconnection logic.
    
    Args:
        database_url: Database connection URL (if None, gets from env)
        pool_size: Number of connections to maintain in the pool
        max_overflow: Maximum number of connections to create beyond pool_size
        pool_timeout: Seconds to wait before giving up on getting a connection
        pool_recycle: Seconds after which to recycle connections
    """
    if database_url is None:
        database_url = get_database_url()
    
    # Configure URL for pooling
    database_url = configure_database_url_for_pooling(database_url)
    
    # Create engine with connection pooling
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=True,  # Verify connections before using them
        connect_args={
            'connect_timeout': 10,
            'sslmode': 'require'
        },
        echo=False  # Set to True for SQL query logging
    )
    
    # Add event listener for connection invalidation
    @event.listens_for(engine, "engine_connect")
    def set_connection_settings(dbapi_conn, connection_record):
        """Set connection settings on each new connection."""
        try:
            # Set statement timeout (optional, in milliseconds)
            with dbapi_conn.cursor() as cursor:
                cursor.execute("SET statement_timeout = 30000")  # 30 seconds
        except Exception as e:
            logger.warning(f"Could not set connection settings: {e}")
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Handle connection checkout with automatic reconnection."""
        try:
            # Test the connection
            dbapi_conn.execute("SELECT 1")
        except DisconnectionError:
            # Connection is dead, raise to trigger reconnection
            raise DisconnectionError("Connection lost, will reconnect")
        except Exception as e:
            logger.warning(f"Connection check failed: {e}")
            # Try to reconnect
            raise DisconnectionError("Connection check failed, will reconnect")
    
    return engine

def init_db(app, database_url=None):
    """
    Initialize database for Flask app.
    
    Args:
        app: Flask application instance
        database_url: Optional database URL (if None, gets from env)
    """
    from models import db
    
    # Get database URL
    if database_url is None:
        database_url = get_database_url()
    
    # Configure Flask app
    # Convert postgresql:// to postgresql+psycopg:// for psycopg3
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'sslmode': 'require'
        }
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

def get_db_session(app):
    """Get a database session from the Flask app context."""
    from models import db
    return db.session

