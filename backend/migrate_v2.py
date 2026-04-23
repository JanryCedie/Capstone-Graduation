from app import create_app
from models import db, User, Redemption, Expense
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Migration V2...")
        try:
            # Create new tables (Redemption, Expense)
            db.create_all()
            print("New tables created (if they didn't exist).")

            with db.engine.connect() as conn:
                # Add total_earned column to user table
                try:
                    conn.execute(text("ALTER TABLE user ADD COLUMN total_earned INTEGER DEFAULT 0"))
                    conn.commit()
                    print("Added 'total_earned' column to 'user' table.")
                    
                    # Initialize total_earned with current points for existing users
                    conn.execute(text("UPDATE user SET total_earned = points"))
                    conn.commit()
                    print("Initialized 'total_earned' with current points for all users.")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print("'total_earned' column already exists.")
                    else:
                        raise e

            print("Migration V2 completed successfully!")
        except Exception as e:
            print(f"Migration ERROR: {e}")

if __name__ == "__main__":
    migrate()
