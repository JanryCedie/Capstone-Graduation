from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        print("Checking/Adding 'email' to 'user' table...")
        db.session.execute(text("ALTER TABLE user ADD COLUMN email VARCHAR(120) UNIQUE AFTER phone_number"))
        
        print("Checking/Adding 'email' to 'otp_store' table...")
        db.session.execute(text("ALTER TABLE otp_store ADD COLUMN email VARCHAR(120) AFTER phone_number"))
        db.session.execute(text("ALTER TABLE otp_store MODIFY phone_number VARCHAR(20) NULL"))
        
        db.session.commit()
        print("✅ Database successfully updated for Email OTP!")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Migration note: {e}")
