import pymysql
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database Config
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'root',
    'database': 'ecoconnect',
    'cursorclass': pymysql.cursors.DictCursor
}

def verify_features():
    print("--- VERIFYING FEATURES & POPULATING DATA ---")
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # 1. Clear existing data to be clean (Optional, but good for testing logic)
            # cursor.execute("DELETE FROM participation")
            # cursor.execute("DELETE FROM event WHERE title LIKE 'TEST%'")
            # cursor.execute("DELETE FROM user WHERE username LIKE 'test_%'")
            # conn.commit()
            
            # 2. Create Test Users
            res_pass = generate_password_hash("password")
            cursor.execute("INSERT INTO user (username, email, password_hash, role, barangay, is_verified) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id", 
                           ('user_irawan', 'irawan@test.com', res_pass, 'resident', 'Irawan', 1))
            user_irawan_id = cursor.lastrowid or cursor.execute("SELECT id FROM user WHERE username='user_irawan'")
            
            cursor.execute("INSERT INTO user (username, email, password_hash, role, barangay, is_verified) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id", 
                           ('user_sanjose', 'sanjose@test.com', res_pass, 'resident', 'San Jose', 1))

            print("   [OK] Test Users Created/Checked.")

            # 3. Create Test Events
            # Irawan Exclusive
            cursor.execute("INSERT INTO event (title, description, location, date, time, organizer_id, points_reward, barangay, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           ('TEST Cleanup Irawan', 'Only for Irawan residents', 'Irawan Hall', '2026-12-01', '08:00', 1, 50, 'Irawan', 'upcoming'))
            event_irawan_id = cursor.lastrowid

            # Global Event
            cursor.execute("INSERT INTO event (title, description, location, date, time, organizer_id, points_reward, barangay, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           ('TEST Global Event', 'For everyone', 'City Plaza', '2026-12-05', '09:00', 1, 100, None, 'upcoming'))
            event_global_id = cursor.lastrowid
            
            print("   [OK] Test Events Created.")

            # 4. Create Participations (Populate Logs)
            if event_irawan_id:
                # Need to fetch user id correctly if update happened
                cursor.execute("SELECT id FROM user WHERE username='user_irawan'")
                uid = cursor.fetchone()['id']
                cursor.execute("INSERT INTO participation (user_id, event_id, status) VALUES (%s, %s, %s)", (uid, event_irawan_id, 'joined'))
            
            if event_global_id:
                cursor.execute("SELECT id FROM user WHERE username='user_sanjose'")
                uid = cursor.fetchone()['id']
                cursor.execute("INSERT INTO participation (user_id, event_id, status) VALUES (%s, %s, %s)", (uid, event_global_id, 'joined'))
                
            conn.commit()
            print("   [OK] Participations Created (Global Logs should now have data).")

    except Exception as e:
        print(f"   [ERROR] : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_features()
