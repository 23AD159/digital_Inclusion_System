from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models import User, AuditLog
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.survey'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            user.login_count += 1
            from datetime import datetime
            user.last_login = datetime.utcnow()
            
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            
            # Log the login
            log = AuditLog(user_id=user.id, action=f"User logged in as {user.role}")
            db.session.add(log)
            db.session.commit()

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.survey'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        college = request.form.get('college_name')
        dept = request.form.get('department')
        year = request.form.get('year_of_study')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered!', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(
            name=name,
            college=college,
            department=dept,
            year=year,
            email=email,
            role='student'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.index'))

@auth.route('/')
def index():
    return render_template('index.html')
