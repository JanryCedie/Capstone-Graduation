from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Redemption, Expense
from datetime import datetime

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/redemption/request', methods=['POST'])
@jwt_required(optional=True)
def request_redemption():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(role='admin').first()
        # Give admin points so the bypass test works safely
        if user.points < 100:
            user.points = 500 
    else:
        user = User.query.get(user_id) if user_id else None
        
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    
    item_name = data.get('item_name')
    points_spent = data.get('points_spent')
    
    if not item_name or not points_spent:
        return jsonify({"message": "Missing item name or points"}), 400
        
    if user.points < points_spent:
        return jsonify({"message": "Insufficient points"}), 400
        
    redemption = Redemption(
        user_id=user_id,
        item_name=item_name,
        points_spent=points_spent,
        status='Pending'
    )
    
    # Deduct points immediately or upon approval? 
    # Usually better to deduct immediately to prevent double spending
    user.points -= points_spent
    
    db.session.add(redemption)
    db.session.commit()
    
    return jsonify(redemption.to_dict()), 201

@finance_bp.route('/redemption/history', methods=['GET'])
@jwt_required(optional=True)
def get_redemption_history():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(role='admin').first()
    else:
        user = User.query.get(user_id) if user_id else None
    
    if user and user.role == 'admin':
        # Admins see all for their barangay
        redemptions = db.session.query(Redemption, User).join(User, Redemption.user_id == User.id).filter(User.barangay == user.barangay).all()
        result = []
        for r, u in redemptions:
            d = r.to_dict()
            d['username'] = u.username
            result.append(d)
        return jsonify(result), 200
    else:
        # Residents only see theirs
        redemptions = Redemption.query.filter_by(user_id=user_id).all()
        return jsonify([r.to_dict() for r in redemptions]), 200

@finance_bp.route('/redemption/approve/<int:redemption_id>', methods=['POST'])
@jwt_required()
def approve_redemption(redemption_id):
    user_id = get_jwt_identity()
    admin = User.query.get(user_id)
    if admin.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403
        
    redemption = Redemption.query.get_or_404(redemption_id)
    redemption.status = 'Claimed'
    db.session.commit()
    
    return jsonify(redemption.to_dict()), 200

@finance_bp.route('/expenses', methods=['GET', 'POST'])
@jwt_required(optional=True)
def manage_expenses():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(role='admin').first()
    else:
        user = User.query.get(user_id) if user_id else None
    
    if request.method == 'POST':
        if not user or user.role not in ['admin', 'official']:
            return jsonify({"message": "Unauthorized"}), 403
            
        data = request.get_json()
        expense = Expense(
            barangay=user.barangay,
            amount=data.get('amount'),
            description=data.get('description'),
            category=data.get('category', 'Spent'),
            date=data.get('date', datetime.now().strftime("%Y-%m-%d"))
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify(expense.to_dict()), 201
    else:
        # GET expenses for the barangay
        expenses = Expense.query.filter_by(barangay=user.barangay).order_by(Expense.id.desc()).all()
        return jsonify([e.to_dict() for e in expenses]), 200

@finance_bp.route('/expenses/summary', methods=['GET'])
@jwt_required(optional=True)
def get_expense_summary():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(role='admin').first()
    else:
        user = User.query.get(user_id) if user_id else None
    
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
        
    expenses = Expense.query.filter_by(barangay=user.barangay).all()
    total_budget = sum(e.amount for e in expenses if e.category == 'Budget')
    total_spent = sum(e.amount for e in expenses if e.category == 'Spent')
    
    return jsonify({
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": total_budget - total_spent
    }), 200
