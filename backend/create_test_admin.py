from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    # Check if test_admin exists
    user = User.query.filter_by(username="test_admin").first()
    if user:
        db.session.delete(user)
        db.session.commit()
        
    new_admin = User(
        username="test_admin",
        email="test_admin@example.com",
        phone_number="09111111111",
        role="admin",
        barangay="Sta. Monica",
        is_verified=True
    )
    new_admin.set_password("testpass123")
    db.session.add(new_admin)
    db.session.commit()
    print("Test Admin created: test_admin / testpass123")
