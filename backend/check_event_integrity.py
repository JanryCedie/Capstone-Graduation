from app import create_app
from models import db, Event

app = create_app()
with app.app_context():
    events = Event.query.all()
    print("--- Event Data Integrity Check ---")
    for e in events:
        print(f"ID: {e.id}, Title: {e.title}, Barangay: {e.barangay}, Points Reward: {e.points_reward}")
        if e.points_reward is None:
            print(f"!! WARNING: Event {e.id} has NULL points_reward !!")
        if e.barangay is None:
            print(f"!! WARNING: Event {e.id} has NULL barangay !!")
