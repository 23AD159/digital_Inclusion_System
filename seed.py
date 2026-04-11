from app import create_app, db
from app.models import User

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@admin.com').first()
        if not admin:
            admin = User(
                name='Admin',
                college='Admin Portal',
                department='Management',
                year='N/A',
                email='admin@admin.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@admin.com / admin123")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db()
