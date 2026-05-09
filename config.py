import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret")
    
    DB_PATH = '/tmp/app.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    CERTIFICATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'certificates')
    
    # ML Model configuration
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.pkl')
    
    # AI Mentor configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
