from app import create_app
from models import db, User, Participation, Event

app = create_app()
with app.app_context():
    print("--- Starting Point Synchronization ---")
    users = User.query.all()
    for u in users:
        # Sum points from all 'attended' participations
        participations = Participation.query.filter_by(user_id=u.id, status='attended').all()
        correct_points = 0
        for p in participations:
            event = Event.query.get(p.event_id)
            if event:
                correct_points += event.points_reward
        
        if u.points != correct_points:
            print(f"Syncing {u.username}: {u.points} -> {correct_points}")
            u.points = correct_points
        else:
            print(f"User {u.username} is already in sync ({u.points} pts)")
            
    db.session.commit()
    print("--- Synchronization Complete ---")
