import sys
from app import create_app
from models import db, User

def link_email(phone, email):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(phone_number=phone).first()
        if user:
            user.email = email
            db.session.commit()
            print(f"✅ Success: Account {phone} is now linked to {email}")
        else:
            print(f"❌ Error: No account found with phone {phone}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python link_email.py <phone_number> <email>")
        print("Example: python link_email.py +639123456789 myemail@gmail.com")
    else:
        link_email(sys.argv[1], sys.argv[2])
