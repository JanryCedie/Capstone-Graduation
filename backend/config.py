import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:root@127.0.0.1:3306/ecoconnect'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEMAPHORE_API_KEY = os.environ.get('SEMAPHORE_API_KEY') or '018f61c722788dc7cdca0dcd1a976ece'
    SEMAPHORE_SENDER_NAME = os.environ.get('SEMAPHORE_SENDER_NAME') or None
    
    # FREE SMTP CONFIG
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'YOUR_GMAIL@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'avsu zdkk mkhe xssz'
