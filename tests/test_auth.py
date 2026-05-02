from fastapi.testclient import TestClient
from app.main import app 

def test_full_auth_flow():
    test_username = "flow_test_user"
    test_password = "SecurePassword123!"


    with TestClient(app) as client:
        # 1. Register
        client.post(
            "/auth/register", 
            json={"username": test_username, "password": test_password}
        )


        login_response = client.post(
            "/auth/login",
            data={"username": test_username, "password": test_password} 
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]


        headers = {"Authorization": f"Bearer {token}"}
        protected_response = client.get("/patients/?page=1&size=10", headers=headers)
        assert protected_response.status_code == 200


        bad_headers = {"Authorization": "Bearer fake_token"}
        rejected_response = client.get("/patients/?page=1&size=10", headers=bad_headers)
        assert rejected_response.status_code == 401