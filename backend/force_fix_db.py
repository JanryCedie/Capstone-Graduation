from app import create_app
from models import db
from sqlalchemy import text
import sys

# Redirect output to file for debugging
sys.stdout = open('migration_log.txt', 'w')
sys.stderr = sys.stdout

app = create_app()

def fix():
    with app.app_context():
        print("Starting schema fix...")
        try:
            with db.engine.connect() as conn:
                print("Connected to DB.")
                
                # Check if email column exists
                result = conn.execute(text("SHOW COLUMNS FROM user LIKE 'email'"))
                if result.fetchone():
                    print("Column 'email' already exists in 'user'.")
                else:
                    print("Adding 'email' to 'user'...")
                    conn.execute(text("ALTER TABLE user ADD COLUMN email VARCHAR(120) UNIQUE AFTER phone_number"))
                    print("Added 'email' to 'user'.")

                # Check otp_store
                result = conn.execute(text("SHOW COLUMNS FROM otp_store LIKE 'email'"))
                if result.fetchone():
                     print("Column 'email' already exists in 'otp_store'.")
                else:
                    print("Adding 'email' to 'otp_store'...")
                    conn.execute(text("ALTER TABLE otp_store ADD COLUMN email VARCHAR(120) AFTER phone_number"))
                    print("Added 'email' to 'otp_store'.")
                
                # Modify phone_number in otp_store
                print("Modifying 'otp_store.phone_number' to be nullable...")
                conn.execute(text("ALTER TABLE otp_store MODIFY phone_number VARCHAR(20) NULL"))
                
                conn.commit()
                print("Migration committed.")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    fix()
