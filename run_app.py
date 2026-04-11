from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database and create admin user."""
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
    app.run(debug=True, port=5000, use_reloader=False)
