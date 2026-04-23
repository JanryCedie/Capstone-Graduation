from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False) # Philippine format: +639XXXXXXXXX
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='resident') # 'resident' or 'official'
    points = db.Column(db.Integer, default=0)
    total_earned = db.Column(db.Integer, default=0) # Lifetime points
    barangay = db.Column(db.String(50), nullable=True) # Sta. Monica, Tiniguiban, San Jose
    id_image = db.Column(db.String(255), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "phone_number": self.phone_number,
            "email": self.email,
            "role": self.role,
            "points": self.points,
            "total_earned": self.total_earned,
            "barangay": self.barangay,
            "id_image": self.id_image,
            "is_verified": self.is_verified
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_reward = db.Column(db.Integer, default=10)
    barangay = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='upcoming') # upcoming, ongoing, completed

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date": self.date,
            "time": self.time,
            "points_reward": self.points_reward,
            "barangay": self.barangay,
            "status": self.status
        }

class Participation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(20), default='joined') # joined, attended, cancelled
    verified_at = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "status": self.status,
            "verified_at": self.verified_at
        }

class OTPStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    is_used = db.Column(db.Boolean, default=False)

class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(20), default='Pending') # Pending, Claimed

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "points_spent": self.points_spent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status
        }

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barangay = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='Spent') # Budget, Spent
    date = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "barangay": self.barangay,
            "amount": self.amount,
            "description": self.description,
            "category": self.category,
            "date": self.date
        }

class TransferRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source_barangay = db.Column(db.String(50), nullable=False)
    target_barangay = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref=db.backref('transfer_requests', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "Unknown",
            "source_barangay": self.source_barangay,
            "target_barangay": self.target_barangay,
            "reason": self.reason,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

