import requests
import datetime

BASE_URL = "http://localhost:5000/api"

def test_date_validation():
    # Login as admin
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "test_admin",
        "password": "testpass123",
        "barangay": "Sta. Monica"
    })
    print(f"Login Status: {login_res.status_code}")
    login_data = login_res.json()
    print(f"Login Data: {login_data}")
    
    token = login_data.get('access_token')
    if not token:
        print("[CRITICAL] Failed to get access token!")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    
    test_cases = [
        {"date": yesterday.strftime('%Y-%m-%d'), "expected_status": 400, "label": "Past Date"},
        {"date": today.strftime('%Y-%m-%d'), "expected_status": 201, "label": "Today's Date"},
        {"date": tomorrow.strftime('%Y-%m-%d'), "expected_status": 201, "label": "Future Date"},
    ]
    
    for case in test_cases:
        print(f"Testing {case['label']} ({case['date']})...")
        res = requests.post(f"{BASE_URL}/events/", json={
            "title": f"Test Event {case['label']}",
            "description": "Validation Test",
            "location": "9.7392, 118.7357",
            "date": case['date'],
            "time": "10:00",
            "points_reward": 10,
            "barangay": "Sta. Monica"
        }, headers=headers)
        
        if res.status_code == case['expected_status']:
            print(f"[PASSED] Got {res.status_code}")
            if res.status_code == 400:
                print(f"Error Message: {res.json().get('message')}")
        else:
            print(f"[FAILED] Expected {case['expected_status']}, got {res.status_code}")
            print(f"Response: {res.text}")

if __name__ == "__main__":
    test_date_validation()
