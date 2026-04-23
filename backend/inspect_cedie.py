from app import create_app
from models import db, User, Participation, Event

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='Cedie1').first()
    if not user:
        print("User Cedie1 not found.")
    else:
        print(f"User: {user.username}")
        print(f"Points: {user.points}")
        print(f"Barangay: {user.barangay}")
        print(f"Role: {user.role}")
        
        participations = Participation.query.filter_by(user_id=user.id).all()
        print(f"\nParticipations ({len(participations)}):")
        for p in participations:
            event = Event.query.get(p.event_id)
            event_title = event.title if event else "DELETED EVENT"
            print(f"- Event: {event_title} (ID: {p.event_id}), Status: {p.status}")

    print("\nRecent Events:")
    events = Event.query.all()
    for e in events:
        print(f"- Event: {e.title} (ID: {e.id}), Reward: {e.points_reward}, Barangay: {e.barangay}")
