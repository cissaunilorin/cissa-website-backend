from uuid import uuid4

from fastapi import status


def test_register_user(client):
    email = f"user_{uuid4().hex}@example.com"
    payload = {"email": email, "password": "Testpass123!", "username": "testuser"}

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["data"]["email"] == email
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_user(client):
    email = f"user_{uuid4().hex}@example.com"
    password = "Testpass123!"

    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "username": "testuser"},
    )

    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["data"]["email"] == email
    assert "access_token" in data
    assert "refresh_token" in data
