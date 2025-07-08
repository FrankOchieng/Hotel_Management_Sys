# config.py 

import os

class Config:
    # Secret key  for Flask sessions and JWTs
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_that_should_be_changed')

    # Database configuration for MySQL
    # Format: mysql+mysqlconnector://user:password@host/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+mysqlconnector://user:password@localhost/hotel_booking_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe API Keys (replace with your actual keys)
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_YOUR_STRIPE_SECRET_KEY')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_YOUR_STRIPE_PUBLIC_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_YOUR_STRIPE_WEBHOOK_SECRET')

    # Email configuration (for sending confirmation emails)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your_email@example.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your_email_password')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

