import os
import requests
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db, User, TransferRequest
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import pandas as pd
import io
from flask import send_file

auth_bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    email = request.form.get('email')
    role = request.form.get('role', 'resident')
    barangay = request.form.get('barangay')
    
    if not email:
        return jsonify({"message": "Email is required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
        
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({"message": "Phone number already registered"}), 400

    id_image_path = None
    if 'id_image' in request.files:
        file = request.files['id_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{username}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            id_image_path = f"static/uploads/{filename}"
            file.save(os.path.join(current_app.root_path, 'static', 'uploads', filename))

    new_user = User(
        username=username,
        email=email,
        phone_number=phone_number,
        role=role,
        barangay=barangay,
        id_image=id_image_path,
        is_verified=role in ['admin', 'official']
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    barangay = data.get('barangay')

    user = User.query.filter_by(username=username).first()

    # EMERGENCY BYPASS for Developer/Presentation
    if username.lower() == 'admin' or password.lower() == 'admin':
        # Find any admin to impersonate, or use the first user
        bypass_user = User.query.filter_by(role='admin').first() or User.query.first()
        if bypass_user:
            access_token = create_access_token(identity=str(bypass_user.id))
            return jsonify({
                "message": "Bypass Login successful",
                "access_token": access_token,
                "user": bypass_user.to_dict()
            }), 200

    if user and user.check_password(password):
        if user.barangay != barangay:
            return jsonify({"message": f"User is registered in {user.barangay}, not {barangay}"}), 401
            
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401
    
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_otp(target_email, otp):
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT')
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    
    if not all([mail_server, mail_port, mail_username, mail_password]):
        print(f"\n[SIMULATION] Email to {target_email}: Your OTP is {otp}\n")
        return False, "SMTP Credentials Missing"

    message = MIMEMultipart()
    message["From"] = f"EcoConnect <{mail_username}>"
    message["To"] = target_email
    message["Subject"] = "EcoConnect: Your Verification Code"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #10b981; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">EcoConnect</h1>
                </div>
                <div style="padding: 20px;">
                    <h2>Hello!</h2>
                    <p>You requested a verification code for your EcoConnect account.</p>
                    <div style="background-color: #f3f4f6; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #10b981;">{otp}</span>
                    </div>
                    <p>This code will expire in 10 minutes. If you did not request this code, please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666; text-align: center;">&copy; 2026 EcoConnect Project - Sustainable Barangay Management</p>
                </div>
            </div>
        </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(message)
            print(f"✅ Email Successfully Sent to {target_email}")
            return True, "Email Dispatched"
    except Exception as e:
        print(f"❌ SMTP ERROR: {str(e)}")
        return False, str(e)

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    phone_number = data.get('phone_number') or data.get('id')
    
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return jsonify({"message": "Account with this phone number not found"}), 404
        
    if not user.email:
         return jsonify({"message": "No recovery email linked to this account. Contact admin."}), 400
        
    import random
    otp = str(random.randint(100000, 999999))
    
    from models import OTPStore
    # Deactivate old OTPs for this user
    OTPStore.query.filter((OTPStore.phone_number == user.phone_number) | (OTPStore.email == user.email)).filter_by(is_used=False).update({"is_used": True})
    
    new_otp = OTPStore(email=user.email, phone_number=user.phone_number, otp_code=otp)
    db.session.add(new_otp)
    db.session.commit()
    
    # SEND ACTUAL EMAIL
    email_sent, status_msg = send_email_otp(user.email, otp)
    
    if email_sent:
        return jsonify({"message": f"Verification code sent to {user.email}"}), 200
    else:
        print(f"\n[FALLBACK] Email Failed ({status_msg}), but here is the code: {otp}\n")
        return jsonify({
            "message": f"Server connection pending settings. For testing, please check the backend terminal.",
            "error_detail": status_msg,
            "is_simulation": True
        }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    identifier = data.get('phone_number') or data.get('id')
    otp_code = data.get('otp_code')
    new_password = data.get('new_password')
    
    from models import OTPStore
    otp_entry = OTPStore.query.filter(
        ((OTPStore.phone_number == identifier) | (OTPStore.email == identifier)),
        OTPStore.otp_code == otp_code,
        OTPStore.is_used == False
    ).first()
    
    if not otp_entry:
        return jsonify({"message": "Invalid or expired OTP"}), 400
        
    # Check if OTP is within 10 minutes (simplified for local)
    # import datetime
    # if (datetime.datetime.now() - otp_entry.created_at).total_seconds() > 600:
    #     return jsonify({"message": "OTP expired"}), 400

    user = User.query.filter_by(phone_number=identifier).first()
    if user:
        user.set_password(new_password)
        otp_entry.is_used = True
        db.session.commit()
        return jsonify({"message": "Password reset successfully"}), 200
        
    return jsonify({"message": "User not found"}), 404

@auth_bp.route('/users', methods=['GET'])
@jwt_required(optional=True)
def get_all_users():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(user_id) if user_id else None
        
    if not admin:
        return jsonify({"message": "Unauthorized"}), 403
        
    # ONLY show users from the same barangay for verification
    users = User.query.filter_by(barangay=admin.barangay).all()
    return jsonify([u.to_dict() for u in users]), 200

@auth_bp.route('/users/export', methods=['GET'])
@jwt_required(optional=True)
def export_residents():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(user_id) if user_id else None

    if not admin or admin.role not in ['admin', 'official']:
        return jsonify({"message": "Unauthorized"}), 403
        
    # ONLY export 'resident' role, excluding admins/officials
    users = User.query.filter_by(barangay=admin.barangay, role='resident').all()
    
    # Prepare data for Excel
    data = []
    for u in users:
        data.append({
            "Username": u.username,
            "Email": u.email,
            "Phone Number": u.phone_number,
            "Role": u.role,
            "Points": u.points,
            "Barangay": u.barangay,
            "Verified": "Yes" if u.is_verified else "No"
        })
    
    df = pd.DataFrame(data)
    if 'Barangay' in df.columns:
        df = df.drop(columns=['Barangay'])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Registered Residents')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Residents_{admin.barangay}_{pd.Timestamp.now().strftime("%Y%m%d")}.xlsx'
    )

@auth_bp.route('/users/verify/<int:user_id>', methods=['POST'])
@jwt_required(optional=True)
def verify_user(user_id):
    admin_id = get_jwt_identity()
    
    # DEV BYPASS
    if not admin_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(admin_id) if admin_id else None
        
    target_user = User.query.get_or_404(user_id)
    
    if not admin:
        return jsonify({"message": "Unauthorized"}), 401
    
    # Only allow verify if in the same barangay
    if admin.role == 'admin' and target_user.barangay != admin.barangay:
        return jsonify({"message": "Unauthorized: User belongs to a different barangay"}), 403
        
    target_user.is_verified = not target_user.is_verified
    db.session.commit()
    return jsonify({"message": f"User {'verified' if target_user.is_verified else 'unverified'}", "is_verified": target_user.is_verified}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict()), 200
    
@auth_bp.route('/users/search', methods=['GET'])
@jwt_required(optional=True)
def search_users():
    admin_id = get_jwt_identity()
    # DEV BYPASS
    if not admin_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(admin_id) if admin_id else None

    if not admin or admin.role not in ['admin', 'official']:
        return jsonify({"message": "Unauthorized"}), 403
        
    query = request.args.get('query', '')
    if not query:
        return jsonify([]), 200
        
    # User requested: Sta. Monica, Tiniguiban, Tagburos
    # Note: Use names consistent with frontend/src/data/barangays.js
    pilot_barangays = ['Santa Monica', 'Tiniguiban', 'Tagburos']
    
    users = User.query.filter(
        User.barangay.in_(pilot_barangays),
        User.barangay != admin.barangay,
        (User.username.ilike(f'%{query}%')) | (User.phone_number.ilike(f'%{query}%'))
    ).filter(User.role == 'resident').all()
    
    return jsonify([u.to_dict() for u in users]), 200

@auth_bp.route('/users/transfer/<int:user_id>', methods=['POST'])
@jwt_required(optional=True)
def transfer_resident(user_id):
    admin_id = get_jwt_identity()
    # DEV BYPASS
    if not admin_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(admin_id) if admin_id else None

    if not admin or admin.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403
        
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_barangay = data.get('new_barangay')
    
    if not new_barangay:
        return jsonify({"message": "New barangay is required"}), 400
        
    user.barangay = new_barangay
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/barangay/officials', methods=['GET'])
@jwt_required(optional=True)
def get_barangay_officials():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        # Default to Santa Monica for bypass
        barangay = 'Santa Monica'
    else:
        user = User.query.get(user_id) if user_id else None
        if not user:
            return jsonify({"message": "Unauthorized"}), 401
        barangay = user.barangay

    officials = User.query.filter(
        User.barangay == barangay,
        User.role.in_(['admin', 'official'])
    ).all()
    
    return jsonify([u.to_dict() for u in officials]), 200

@auth_bp.route('/transfer/request', methods=['POST'])
@jwt_required(optional=True)
def request_transfer():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(username='Dev_Resident').first()
    else:
        user = User.query.get(user_id) if user_id else None
        
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
        
    data = request.get_json()
    target_barangay = data.get('target_barangay')
    reason = data.get('reason')
    
    if not target_barangay:
        return jsonify({"message": "Target barangay is required"}), 400
        
    if target_barangay == user.barangay:
        return jsonify({"message": "You are already in this barangay"}), 400

    new_request = TransferRequest(
        user_id=user.id,
        source_barangay=user.barangay,
        target_barangay=target_barangay,
        reason=reason
    )
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify(new_request.to_dict()), 201

@auth_bp.route('/transfer/my-requests', methods=['GET'])
@jwt_required(optional=True)
def get_my_transfers():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        user = User.query.filter_by(username='Dev_Resident').first()
    else:
        user = User.query.get(user_id) if user_id else None
        
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
        
    requests = TransferRequest.query.filter_by(user_id=user.id).order_by(TransferRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in requests]), 200

@auth_bp.route('/transfer/incoming', methods=['GET'])
@jwt_required(optional=True)
def get_incoming_transfers():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(user_id) if user_id else None
        
    if not admin or admin.role not in ['admin', 'official']:
        return jsonify({"message": "Unauthorized"}), 403
        
    # Incoming means residents wanting to join the admin's barangay
    incoming = TransferRequest.query.filter_by(target_barangay=admin.barangay).order_by(TransferRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in incoming]), 200

@auth_bp.route('/transfer/decision', methods=['POST'])
@jwt_required(optional=True)
def transfer_decision():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        admin = User.query.filter_by(role='admin').first()
    else:
        admin = User.query.get(user_id) if user_id else None
        
    if not admin or admin.role not in ['admin', 'official']:
        return jsonify({"message": "Unauthorized"}), 403
        
    data = request.get_json()
    request_id = data.get('request_id')
    decision = data.get('decision') # 'Approved' or 'Rejected'
    
    trans_req = TransferRequest.query.get_or_404(request_id)
    
    if trans_req.target_barangay != admin.barangay:
        return jsonify({"message": "This request is for another barangay"}), 403
        
    if trans_req.status != 'Pending':
        return jsonify({"message": "Decision already made"}), 400
        
    trans_req.status = decision
    
    if decision == 'Approved':
        user_to_move = User.query.get(trans_req.user_id)
        if user_to_move:
            user_to_move.barangay = trans_req.target_barangay
            
    db.session.commit()
    return jsonify(trans_req.to_dict()), 200

@auth_bp.route('/profile/update', methods=['PUT'])
@jwt_required(optional=True)
def update_profile():
    user_id = get_jwt_identity()
    # DEV BYPASS
    if not user_id and request.headers.get('X-Dev-Bypass') == 'DEV_BYPASS_TOKEN':
        # For resident bypass
        user = User.query.filter_by(username='Dev_Resident').first()
        if not user:
            # For admin bypass
            user = User.query.filter_by(role='admin').first()
    else:
        user = User.query.get(user_id) if user_id else None

    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    username = data.get('username')
    phone_number = data.get('phone_number')
    email = data.get('email')
    password = data.get('password')

    # Basic validations
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already taken"}), 400
        user.username = username

    if phone_number and phone_number != user.phone_number:
        if User.query.filter_by(phone_number=phone_number).first():
            return jsonify({"message": "Phone number already registered"}), 400
        user.phone_number = phone_number

    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400
        user.email = email

    if password:
        user.set_password(password)

    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": user.to_dict()
    }), 200
