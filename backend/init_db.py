from app import create_app
from models import db, User

app = create_app()

def init_admin():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if Admin already exists
        admin = User.query.filter_by(username='Admin').first()
        if not admin:
            print("Creating default Admin account...")
            admin = User(
                username='Admin',
                phone_number='+639000000000',
                role='admin',
                is_verified=True,
                barangay='Command Center'
            )
            admin.set_password('Admin')
            db.session.add(admin)
            db.session.commit()
            print("Default Admin account (Admin / Admin) created successfully!")
        else:
            print("Admin account already exists.")

if __name__ == '__main__':
    init_admin()
