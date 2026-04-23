from app import create_app
from models import db, User, Participation, Event

app = create_app()
with app.app_context():
    print("--- Users with points ---")
    users = User.query.filter(User.points > 0).all()
    for u in users:
        print(f"User: {u.username}, Points: {u.points}, Barangay: {u.barangay}")
    
    print("\n--- All Participations ---")
    parts = Participation.query.all()
    for p in parts:
        user = User.query.get(p.user_id)
        event = Event.query.get(p.event_id)
        print(f"User: {user.username if user else 'UNKNOWN'}, Event: {event.title if event else 'DELETED EVENT'} (ID: {p.event_id}), Status: {p.status}")
