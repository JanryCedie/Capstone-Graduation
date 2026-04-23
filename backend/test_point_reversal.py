import requests
import random
import string

BASE_URL = "http://localhost:5000/api"

def get_random_string(length=5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_point_reversal():
    suffix = get_random_string()
    
    # 1. Setup Resident
    res_username = f"res_{suffix}"
    res_email = f"res_{suffix}@test.com"
    res_phone = f"+639{random.randint(100000000, 999999999)}"
    barangay = "Sta. Monica"
    
    requests.post(f"{BASE_URL}/auth/register", data={
        "username": res_username, "email": res_email, "phone_number": res_phone,
        "password": "pass", "role": "resident", "barangay": barangay
    })
    res_token = requests.post(f"{BASE_URL}/auth/login", json={
        "username": res_username, "password": "pass", "barangay": barangay
    }).json().get('access_token')
    res_headers = {"Authorization": f"Bearer {res_token}"}

    # 2. Setup Admin (assuming we can register one for testing)
    adm_username = f"adm_{suffix}"
    adm_email = f"adm_{suffix}@test.com"
    adm_phone = f"+639{random.randint(100000000, 999999999)}"
    requests.post(f"{BASE_URL}/auth/register", data={
        "username": adm_username, "email": adm_email, "phone_number": adm_phone,
        "password": "pass", "role": "admin", "barangay": barangay
    })
    adm_token = requests.post(f"{BASE_URL}/auth/login", json={
        "username": adm_username, "password": "pass", "barangay": barangay
    }).json().get('access_token')
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    # Verify Resident
    res_id = requests.get(f"{BASE_URL}/auth/me", headers=res_headers).json().get('id')
    requests.post(f"{BASE_URL}/auth/users/verify/{res_id}", headers=adm_headers)
    print(f"Verified resident {res_username} (ID: {res_id})")

    # 3. Admin creates event
    event_data = {
        "title": "Cleanup Test", "description": "Test", "location": "Test",
        "date": "2026-02-10", "time": "08:00", "points_reward": 50, "barangay": barangay
    }
    event_res = requests.post(f"{BASE_URL}/events/", json=event_data, headers=adm_headers)
    event_id = event_res.json().get('id')
    print(f"Created event {event_id} with 50 points")

    # 4. Resident joins event
    requests.post(f"{BASE_URL}/events/join/{event_id}", headers=res_headers)

    # 5. Admin verifies attendance
    participants = requests.get(f"{BASE_URL}/events/participants/{event_id}", headers=adm_headers).json()
    part_id = participants[0]['id']
    requests.post(f"{BASE_URL}/events/verify/{part_id}", headers=adm_headers)
    
    # Check points before deletion
    res_data = requests.get(f"{BASE_URL}/auth/me", headers=res_headers).json()
    print(f"Points before deletion: {res_data.get('points')}")

    # 6. Admin deletes event
    del_res = requests.delete(f"{BASE_URL}/events/{event_id}", headers=adm_headers)
    print(f"Delete response: {del_res.json().get('message')}")

    # 7. Check points after deletion
    res_data_after = requests.get(f"{BASE_URL}/auth/me", headers=res_headers).json()
    final_points = res_data_after.get('points')
    print(f"Points after deletion: {final_points}")

    if final_points == 0:
        print("[SUCCESS] Points were correctly reversed.")
    else:
        print(f"[FAILURE] Points still exist: {final_points}")

if __name__ == "__main__":
    test_point_reversal()
