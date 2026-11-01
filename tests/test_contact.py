def test_submit_contact_message(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Project Inquiry",
        "message": "We would like to build a web application.",
    }
    response = client.post("/contact", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert data["subject"] == "Project Inquiry"
    assert "id" in data

def test_submit_contact_invalid_email(client):
    payload = {
        "name": "Jane Doe",
        "email": "not-an-email",
        "subject": "Project Inquiry",
        "message": "Testing invalid email.",
    }
    response = client.post("/contact", json=payload)
    assert response.status_code == 422  # Validation error
