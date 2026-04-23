import requests
import random
import string

def test_registration():
    url = "http://localhost:5000/api/auth/register"
    
    # Generate random username and email to avoid conflicts
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    username = f"testuser_{suffix}"
    email = f"test_{suffix}@example.com"
    phone_number = f"+639{random.randint(100000000, 999999999)}"
    
    payload = {
        "username": username,
        "email": email,
        "phone_number": phone_number,
        "password": "password123",
        "role": "resident",
        "barangay": "Sta. Monica"
    }
    
    print(f"Testing registration with payload: {payload}")
    
    try:
        response = requests.post(url, data=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration test passed!")
        else:
            print("❌ Registration test failed!")
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("Make sure the backend is running (python backend/app.py)")

if __name__ == "__main__":
    test_registration()
