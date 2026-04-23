from app import create_app
from models import db, User, Participation, Event

app = create_app()
with app.app_context():
    print("--- All Events ---")
    events = Event.query.all()
    for e in events:
        print(f"ID: {e.id}, Title: {e.title}, Reward: {e.points_reward}, Barangay: {e.barangay}")
    
    print("\n--- All Participations ---")
    parts = Participation.query.all()
    for p in parts:
        print(f"User ID: {p.user_id}, Event ID: {p.event_id}, Status: {p.status}")
