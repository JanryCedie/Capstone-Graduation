from sqlalchemy import create_engine, text
import os

# Hardcoded or from environment, but let's try reading config file manually or just using known values
# Assuming standard XAMPP/MySQL setup based on previous context: mysql+pymysql://root:root@127.0.0.1/ecoconnect
# Let's try to parse config.py just in case, or just hardcode for now since environment might be issue

DATABASE_URI = 'mysql+pymysql://root:@localhost:3307/ecoconnect' # Default XAMPP often has no password for root
# But previous migrations used config. Let's try to import config if possible, or just read it.

import sys
sys.path.append('.') # Ensure current dir is in path
try:
    from config import Config
    DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI
    print(f"Using URI from config: {DATABASE_URI}")
except Exception as e:
    print(f"Failed to import config: {e}")
    # Fallback to what was seen in logs or standard
    DATABASE_URI = 'mysql+pymysql://root:@localhost:3307/ecoconnect'

def fix_directly():
    print(f"Connecting to {DATABASE_URI}...")
    try:
        engine = create_engine(DATABASE_URI)
        with engine.connect() as conn:
            print("Connected!")
            
            # 1. Check User table
            try:
                print("Checking 'user' table for 'email' column...")
                # MySQL specific syntax
                result = conn.execute(text("SHOW COLUMNS FROM user LIKE 'email'"))
                row = result.fetchone()
                if row:
                    print("Column 'email' ALREADY EXISTS in 'user'.")
                else:
                    print("Adding 'email' to 'user'...")
                    conn.execute(text("ALTER TABLE user ADD COLUMN email VARCHAR(120) UNIQUE AFTER phone_number"))
                    print("SUCCESS: Added 'email' to 'user'.")
            except Exception as e:
                print(f"Error checking/adding to user: {e}")

            # 2. Check otp_store table
            try:
                print("Checking 'otp_store' table for 'email' column...")
                result = conn.execute(text("SHOW COLUMNS FROM otp_store LIKE 'email'"))
                row = result.fetchone()
                if row:
                    print("Column 'email' ALREADY EXISTS in 'otp_store'.")
                else:
                    print("Adding 'email' to 'otp_store'...")
                    conn.execute(text("ALTER TABLE otp_store ADD COLUMN email VARCHAR(120) AFTER phone_number"))
                    print("SUCCESS: Added 'email' to 'otp_store'.")
            except Exception as e:
                print(f"Error checking/adding to otp_store: {e}")

            # 3. Modify phone_number to be nullable
            try:
                print("Modifying 'otp_store.phone_number' to be nullable...")
                conn.execute(text("ALTER TABLE otp_store MODIFY phone_number VARCHAR(20) NULL"))
                print("SUCCESS: Modified 'otp_store.phone_number'.")
            except Exception as e:
                print(f"Error modifying otp_store: {e}")
            
            conn.commit()
            print("All changes committed.")
    except Exception as e:
        print(f"CRITICAL DB CONNECTION ERROR: {e}")

if __name__ == "__main__":
    fix_directly()
