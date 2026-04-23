from app import create_app
from models import db, User, Event, Participation, OTPStore

app = create_app()
with app.app_context():
    print("--- Starting Data Reset ---")
    
    # Delete in order of dependencies
    print("Clearing Participation records...")
    db.session.query(Participation).delete()
    
    print("Clearing Event records...")
    db.session.query(Event).delete()
    
    print("Clearing OTP records...")
    db.session.query(OTPStore).delete()
    
    print("Clearing all User accounts (Admins and Residents)...")
    db.session.query(User).delete()
    
    db.session.commit()
    print("--- Reset Complete! Local database is now clean. ---")
