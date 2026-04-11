from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'students' # Keeping the old table name for compatibility if needed, but using SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')
    points = db.Column(db.Integer, default=0)
    badges = db.Column(db.String(200), default='Newcomer')
    login_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship('SurveyResponse', backref='student', lazy=True)
    results = db.relationship('Result', backref='student', lazy=True)
    recommendations = db.relationship('Recommendation', backref='student', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # 25 questions
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    q4 = db.Column(db.Integer)
    q5 = db.Column(db.Integer)
    q6 = db.Column(db.Integer)
    q7 = db.Column(db.Integer)
    q8 = db.Column(db.Integer)
    q9 = db.Column(db.Integer)
    q10 = db.Column(db.Integer)
    q11 = db.Column(db.Integer)
    q12 = db.Column(db.Integer)
    q13 = db.Column(db.Integer)
    q14 = db.Column(db.Integer)
    q15 = db.Column(db.Integer)
    q16 = db.Column(db.Integer)
    q17 = db.Column(db.Integer)
    q18 = db.Column(db.Integer)
    q19 = db.Column(db.Integer)
    q20 = db.Column(db.Integer)
    q21 = db.Column(db.Integer)
    q22 = db.Column(db.Integer)
    q23 = db.Column(db.Integer)
    q24 = db.Column(db.Integer)
    q25 = db.Column(db.Integer)

    # Professional profile links
    resume_path = db.Column(db.String(300))
    github_url = db.Column(db.String(300))
    linkedin_url = db.Column(db.String(300))
    hackerrank_url = db.Column(db.String(300))
    leetcode_url = db.Column(db.String(300))
    certifications_json = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    score = db.Column(db.Integer)
    category = db.Column(db.String(50))
    validation_status = db.Column(db.String(200), default='Pending')
    placement_chance = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    recommendation_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
