from app import create_app
from models import User

app = create_app()
with app.app_context():
    admins = User.query.filter(User.role.in_(['admin', 'official'])).all()
    for a in admins:
        print(f"ID: {a.id}, Username: {a.username}, Role: {a.role}")
