def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Business Portal API" in data["title"]

def test_login_success(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "AdminPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"

def test_login_invalid_password(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "doesnotexist@example.com",
            "password": "AnyPassword123!",
        },
    )
    assert response.status_code == 401

def test_get_current_user_profile(client):
    # 1. Login
    login_res = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "AdminPassword123!",
        },
    )
    token = login_res.json()["access_token"]

    # 2. Access protected /auth/me
    me_res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "admin@example.com"
    assert user_data["role"] == "admin"

def test_unauthorized_access_fails(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
