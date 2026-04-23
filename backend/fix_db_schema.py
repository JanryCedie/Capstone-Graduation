from app import create_app
from models import db
from sqlalchemy import text, inspect

app = create_app()

def check_schema():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            print(f"Current 'user' table columns: {columns}")
            
            if 'email' not in columns:
                print("❌ 'email' column is MISSING!")
                print("Attempting to add 'email' column now...")
                try:
                    # Using raw SQL to ensure it runs
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE user ADD COLUMN email VARCHAR(120) UNIQUE AFTER phone_number"))
                        conn.execute(text("ALTER TABLE otp_store ADD COLUMN email VARCHAR(120) AFTER phone_number"))
                        conn.execute(text("ALTER TABLE otp_store MODIFY phone_number VARCHAR(20) NULL"))
                        conn.commit()
                    print("✅ 'email' column added successfully!")
                except Exception as e:
                    print(f"❌ Failed to add column: {e}")
            else:
                print("✅ 'email' column ALREADY EXISTS.")
                
        except Exception as e:
            print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    check_schema()
