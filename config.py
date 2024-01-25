import os

# Secret Key
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Disable debug mode for production
DEBUG = False

# Database configuration
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'your-default-database-uri')
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_TRACK_MODIFICATIONS = False
