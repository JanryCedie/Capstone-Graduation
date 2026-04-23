import pymysql
import sys
import subprocess

def setup_database():
    print("--- AUTOMATED DATABASE SETUP ---")
    
    # 1. Connect to MySQL Server (No Database selected yet)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'root',
        'port': 3306
    }
    
    print(f"1. Connecting to MySQL at {db_config['host']}...")
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        print("   [OK] Connected to MySQL Server.")
    except Exception as e:
        print(f"   [ERROR] Could not connect to MySQL: {e}")
        print("   Please check if XAMPP MySQL is successfuly STARTED.")
        return False

    # 2. Create Database
    try:
        print("2. Resetting database 'ecoconnect'...")
        cursor.execute("DROP DATABASE IF EXISTS ecoconnect")
        cursor.execute("CREATE DATABASE ecoconnect")
        conn.commit()
        print("   [OK] Database 'ecoconnect' exists/created.")
    except Exception as e:
        print(f"   [ERROR] Failed to create database: {e}")
        return False
    finally:
        conn.close()

    # 3. Initialize Tables using App Logic
    print("3. Initializing application tables...")
    try:
        # Use the current python interpreter to run init_db.py
        result = subprocess.run([sys.executable, 'init_db.py'], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"   [ERROR] init_db.py failed:\n{result.stderr}")
            return False
        else:
            print("   [OK] Tables initialized and Admin account checked.")
    except Exception as e:
        print(f"   [ERROR] Failed to run initialization script: {e}")
        return False

    print("\n--- SETUP COMPLETE ---")
    return True

if __name__ == "__main__":
    setup_database()
