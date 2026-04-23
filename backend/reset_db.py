from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("WARNING: This will delete ALL data in the database.")
    print("Dropping all tables...")
    db.drop_all()
    print("Recreating all tables...")
    db.create_all()
    print("Database reset complete! All data has been removed.")
