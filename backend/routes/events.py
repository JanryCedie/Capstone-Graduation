from flask import Blueprint, request, jsonify
from models import db, User, Event, Participation
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import pandas as pd
import io
from flask import send_file

events_bp = Blueprint('events', __name__)

@events_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_events():
    user_id = get_jwt_identity()
    
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(role='admin').first()
    else:
        user = User.query.get(user_id) if user_id else None
    
    if user:
        # STRICT FILTERING: Only verified residents (or any official/admin) see events
        if not user.is_verified and user.role == 'resident':
            events = []
        else:
            events = Event.query.filter_by(barangay=user.barangay).all()
    else:
        # Public visitors see nothing restricted
        events = []
        
    return jsonify([e.to_dict() for e in events]), 200

@events_bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    try:
        user_identity = get_jwt_identity()
        user_id = int(user_identity) # Explicit cast
        user = User.query.get(user_id)
        
        if not user or user.role not in ['official', 'admin']:
            return jsonify({"message": f"Unauthorized. Role: {user.role if user else 'Unknown'}"}), 403
            
        data = request.get_json()
        print(f"DEBUG: Receiving Event Data: {data}")
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
            
        # Hard validation
        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        date_str = data.get('date')
        time = data.get('time')
        points = data.get('points_reward', 10)
        barangay = data.get('barangay')

        if not all([title, description, location, date_str, time]):
            missing = [k for k in ['title', 'description', 'location', 'date', 'time'] if not data.get(k)]
            return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400
        
        # Date validation: Prevent past dates
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            if event_date < current_date:
                return jsonify({"message": "Invalid date: Cleanup directive cannot be backdated. Please select today's date onwards."}), 400
        except ValueError:
            return jsonify({"message": "Invalid date format. Expected YYYY-MM-DD"}), 400
            
        new_event = Event(
            title=str(title),
            description=str(description),
            location=str(location),
            date=str(date_str),
            time=str(time),
            points_reward=int(points) if points is not None else 10,
            barangay=str(barangay) if barangay else None,
            organizer_id=user_id
        )
        
        db.session.add(new_event)
        db.session.commit()
        print(f"DEBUG: Event created successfully (ID: {new_event.id})")
        return jsonify(new_event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"CRITICAL ERROR: {error_details}")
        return jsonify({"message": f"DB Server Error: {str(e)}"}), 500

@events_bp.route('/global-logs', methods=['GET'])
@jwt_required(optional=True)
def get_global_logs():
    try:
        user_id = get_jwt_identity()
        # DEV BYPASS
        if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
            user = User.query.filter_by(role='admin').first()
        else:
            user = User.query.get(user_id) if user_id else None

        if not user or user.role != 'admin':
            return jsonify({"message": "Unauthorized"}), 403
            
        # LOCALIZED JOIN QUERY: Filter by admin's barangay
        results = db.session.query(Participation, User, Event)\
            .join(User, Participation.user_id == User.id)\
            .join(Event, Participation.event_id == Event.id)\
            .filter(Event.barangay == user.barangay)\
            .all()
            
        log_data = []
        for p, u, e in results:
            p_dict = p.to_dict()
            p_dict['user'] = u.to_dict()
            p_dict['event'] = e.to_dict()
            log_data.append(p_dict)
            
        return jsonify(log_data), 200
    except Exception as e:
        print(f"Error fetching global logs: {e}")
        return jsonify([]), 200 # Return empty list on error to prevent frontend crash

@events_bp.route('/barangay-stats', methods=['GET'])
@jwt_required(optional=True)
def get_barangay_stats():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(role='admin').first()
    else:
        user = User.query.get(user_id) if user_id else None

    if not user or user.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403
        
    # LOCALIZED STATS: Only show admin's own barangay stats for residents
    from sqlalchemy import func
    stats = db.session.query(User.barangay, func.sum(User.points), func.count(User.id))\
        .filter(User.barangay == user.barangay, User.role == 'resident')\
        .group_by(User.barangay).all()
    
    result = []
    for s in stats:
        result.append({
            "barangay": s[0] if s[0] else "Unknown",
            "total_points": int(s[1]) if s[1] else 0,
            "total_users": s[2]
        })
    return jsonify(result), 200

@events_bp.route('/join/<int:event_id>', methods=['POST'])
@jwt_required()
def join_event(event_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or (not user.is_verified and user.role == 'resident'):
        return jsonify({"message": "Unauthorized: Verification required to join events"}), 403
        
    event = Event.query.get_or_404(event_id)
    
    existing = Participation.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        return jsonify({"message": "Already joined"}), 400
        
    new_p = Participation(user_id=user_id, event_id=event_id)
    db.session.add(new_p)
    db.session.commit()
    
    return jsonify({"message": "Joined successfully"}), 201

@events_bp.route('/my-participation', methods=['GET'])
@jwt_required()
def get_my_participation():
    user_id = get_jwt_identity()
    p_list = Participation.query.filter_by(user_id=user_id).all()
    
    result = []
    for p in p_list:
        event = Event.query.get(p.event_id)
        p_dict = p.to_dict()
        p_dict['event'] = event.to_dict() if event else None
        result.append(p_dict)
        
    return jsonify(result), 200

@events_bp.route('/participants/<int:event_id>', methods=['GET'])
@jwt_required()
def get_participants(event_id):
    user_identity = get_jwt_identity()
    user = User.query.get(user_identity)
    event = Event.query.get_or_404(event_id)
    
    # STRICT ISOLATION: Admins and Organizers only see their own barangay/events
    if user.role == 'admin':
        if event.barangay != user.barangay:
            return jsonify({"message": "Unauthorized: Event belongs to a different barangay"}), 403
    elif event.organizer_id != int(user_identity):
        return jsonify({"message": "Unauthorized"}), 403
        
    p_list = Participation.query.filter_by(event_id=event_id).all()
    result = []
    for p in p_list:
        user = User.query.get(p.user_id)
        p_dict = p.to_dict()
        p_dict['user'] = user.to_dict() if user else None
        result.append(p_dict)
        
    return jsonify(result), 200

@events_bp.route('/<int:event_id>/participants/export', methods=['GET'])
@jwt_required()
def export_participants(event_id):
    user_identity = get_jwt_identity()
    user = User.query.get(user_identity)
    event = Event.query.get_or_404(event_id)
    
    # STRICT ISOLATION: Admins and Organizers only export their own barangay/events
    if user.role == 'admin':
        if event.barangay != user.barangay:
            return jsonify({"message": "Unauthorized"}), 403
    elif event.organizer_id != int(user_identity):
        return jsonify({"message": "Unauthorized"}), 403
        
    results = db.session.query(Participation, User)\
        .join(User, Participation.user_id == User.id)\
        .filter(Participation.event_id == event_id)\
        .all()
    
    # Prepare data for Excel
    data = []
    for p, u in results:
        verified_at_display = "Not Verified"
        if p.verified_at:
            try:
                # Attempt to parse current 24-hour format and convert to 12-hour
                dt = datetime.strptime(p.verified_at, "%Y-%m-%d %H:%M:%S")
                verified_at_display = dt.strftime("%Y-%m-%d %I:%M:%S %p")
            except:
                # If already in 12-hour or different format, use as is
                verified_at_display = p.verified_at

        data.append({
            "Username": u.username,
            "Email": u.email,
            "Phone Number": u.phone_number,
            "Participation Status": p.status,
            "Verified At": verified_at_display
        })
    
    df = pd.DataFrame(data)
    
    # Save to buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Event Participants')
    
    output.seek(0)
    
    filename = f"Participants_{event.title.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@events_bp.route('/verify/<int:participation_id>', methods=['POST'])
@jwt_required()
def verify_attendance(participation_id):
    user_identity = get_jwt_identity()
    user = User.query.get(user_identity)
    p = Participation.query.get_or_404(participation_id)
    event = Event.query.get(p.event_id)
    
    # STRICT ISOLATION: Admins and Organizers only verify within their barangay/events
    if user.role == 'admin':
        if event.barangay != user.barangay:
            return jsonify({"message": "Unauthorized: Participation belongs to a different barangay"}), 403
    elif event.organizer_id != int(user_identity):
        return jsonify({"message": "Unauthorized"}), 403
        
    if p.status == 'attended':
        return jsonify({"message": "Already verified"}), 400
        
    p.status = 'attended'
    from datetime import datetime
    p.verified_at = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    # Award points
    user = User.query.get(p.user_id)
    if user:
        user.points += event.points_reward
        user.total_earned += event.points_reward
        
    db.session.commit()
    return jsonify({"message": "Attendance verified and points awarded"}), 200

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    event = Event.query.get_or_404(event_id)
    
    # STRICT ISOLATION: Admins only manage their own barangay
    if user.role == 'admin' and event.barangay != user.barangay:
        return jsonify({"message": "Unauthorized: Event belongs to a different barangay"}), 403
    elif user.role != 'admin' and event.organizer_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403
        
    data = request.get_json()
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    event.location = data.get('location', event.location)
    event.date = data.get('date', event.date)
    event.time = data.get('time', event.time)
    event.points_reward = data.get('points_reward', event.points_reward)
    event.barangay = data.get('barangay', event.barangay)
    
    db.session.commit()
    return jsonify(event.to_dict()), 200

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    event = Event.query.get_or_404(event_id)
    
    # STRICT ISOLATION: Admins only delete their own barangay events
    if user.role == 'admin' and event.barangay != user.barangay:
        return jsonify({"message": "Unauthorized: Event belongs to a different barangay"}), 403
    elif user.role != 'admin' and event.organizer_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403
        
    # CASCADE DELETE: Remove all participants first
    try:
        # Deduct points from those who attended
        attended_participants = Participation.query.filter_by(event_id=event_id, status='attended').all()
        for p in attended_participants:
            user_to_deduct = User.query.get(p.user_id)
            if user_to_deduct:
                user_to_deduct.points = max(0, user_to_deduct.points - event.points_reward)
        
        # Use query-level delete for maximum reliability with foreign keys
        Participation.query.filter_by(event_id=event_id).delete()
        
        # Now delete the event
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted and points reversed for attendees"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"DELETE ERROR: {str(e)}")
        return jsonify({"message": f"Critical Error: {str(e)}"}), 500

@events_bp.route('/leaderboard', methods=['GET'])
@jwt_required(optional=True)
def get_leaderboard():
    user_id = get_jwt_identity()
    query = User.query
    
    if user_id:
        user = User.query.get(user_id)
        if user:
            # ONLY show residents from the same barangay
            query = query.filter_by(barangay=user.barangay, role='resident')
        else:
            query = query.filter_by(role='resident')
    else:
        query = query.filter_by(role='resident')
            
    users = query.order_by(User.points.desc()).limit(10).all()
    return jsonify([u.to_dict() for u in users]), 200
