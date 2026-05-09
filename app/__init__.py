import os
from flask import Flask
from app.extensions import db, login_manager, migrate
from config import Config

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # Auto‑create tables on first start if they are missing
    with app.app_context():
        db.create_all()
        # Ensure default admin exists
        from app.models import User
        admin_email = 'admin@admin.com'
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                name='Admin',
                college='Admin Portal',
                department='Management',
                year='N/A',
                email=admin_email,
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Default admin user created')


    # Ensure upload directories exist
    os.makedirs(app.config['RESUME_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CERTIFICATE_FOLDER'], exist_ok=True)

    # Register Blueprints
    from app.routes.auth import auth
    from app.routes.student import student
    from app.routes.admin import admin
    from app.routes.api import api

    app.register_blueprint(auth)
    app.register_blueprint(student)
    app.register_blueprint(admin)
    app.register_blueprint(api, url_prefix='/api')

    # Register template filters
    from app.utils.helpers import from_json_filter
    app.jinja_env.filters['from_json'] = from_json_filter

    return app
