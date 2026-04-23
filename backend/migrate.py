from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Add barangay column to event table
                conn.execute(text('ALTER TABLE event ADD COLUMN barangay VARCHAR(50)'))
                conn.commit()
            print("MIGRATION SUCCESS: added 'barangay' column to 'event' table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("MIGRATION SKIP: 'barangay' column already exists.")
            else:
                print(f"MIGRATION ERROR: {e}")

if __name__ == '__main__':
    migrate()
