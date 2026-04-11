import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    CERTIFICATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'certificates')
    
    # ML Model configuration
    MODEL_PATH = os.path.join(basedir, 'models', 'model.pkl')
    
    # AI Mentor configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
