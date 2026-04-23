import requests
import random
import string

BASE_URL = "http://localhost:5000/api"

def test_verification_lock():
    # 1. Register a new resident (they are unverified by default)
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    username = f"unverified_{suffix}"
    email = f"uv_{suffix}@example.com"
    phone = f"+639{random.randint(100000000, 999999999)}"
    barangay = "Sta. Monica"
    
    reg_payload = {
        "username": username,
        "email": email,
        "phone_number": phone,
        "password": "password123",
        "role": "resident",
        "barangay": barangay
    }
    
    print(f"--- Testing Unverified Resident: {username} ---")
    reg_res = requests.post(f"{BASE_URL}/auth/register", data=reg_payload)
    if reg_res.status_code != 201:
        print(f"Failed to register: {reg_res.text}")
        return

    # 2. Login to get token
    login_payload = {"username": username, "password": "password123", "barangay": barangay}
    login_res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    token = login_res.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Check events list (should be empty for unverified resident)
    events_res = requests.get(f"{BASE_URL}/events/", headers=headers)
    events = events_res.json()
    print(f"Events visible to unverified resident: {len(events)}")
    
    if len(events) == 0:
        print("[SUCCESS] Unverified resident cannot see events.")
    else:
        print("[FAILURE] Unverified resident can see events.")

    # 4. Try to join an event (even if they can't see it, they shouldn't be able to join via ID)
    # We'll assume event ID 1 exists or just try a random one
    join_res = requests.post(f"{BASE_URL}/events/join/1", headers=headers)
    print(f"Attempt to join event 1 status: {join_res.status_code}")
    if join_res.status_code == 403:
        print("[SUCCESS] Unverified resident is blocked from joining events.")
    else:
        print(f"[FAILURE] Unexpected status code when joining: {join_res.status_code}")

if __name__ == "__main__":
    test_verification_lock()
