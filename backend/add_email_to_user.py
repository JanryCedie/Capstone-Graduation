import pymysql
import os
from config import Config

def migrate():
    # Parse URI: mysql+pymysql://root:root@127.0.0.1/ecoconnect
    uri = Config.SQLALCHEMY_DATABASE_URI
    parts = uri.replace('mysql+pymysql://', '').replace('@', '/').replace(':', '/').split('/')
    
    user = parts[0]
    password = parts[1]
    host = parts[2]
    db_name = parts[3]

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    try:
        with connection.cursor() as cursor:
            print("Adding 'email' column to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120) UNIQUE AFTER phone_number")
            
            print("Adding 'email' column to 'otp_store' table...")
            cursor.execute("ALTER TABLE otp_store ADD COLUMN email VARCHAR(120) AFTER phone_number")
            cursor.execute("ALTER TABLE otp_store MODIFY phone_number VARCHAR(20) NULL")
            
            connection.commit()
            print("Migration successful! 🚀")
    except Exception as e:
        print(f"Migration error (already exists?): {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    migrate()
