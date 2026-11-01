import io
import pytest

pytestmark = pytest.mark.skip(reason="Site assets temporarily commented out for future use")

def test_get_public_site_assets(client):
    response = client.get("/site-assets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "global.logo.primary" in data
    assert data["global.logo.primary"]["url"] == "/images/sequenx-logo.svg"
    assert data["global.logo.primary"]["aspect_ratio"] == "Auto (4:1)"

def test_admin_list_site_assets(client):
    # 1. Login as admin
    login_res = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "AdminPassword123!"},
    )
    token = login_res.json()["access_token"]

    # 2. Fetch site assets from admin endpoint
    res = client.get(
        "/admin/site-assets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] >= 50
    assert "homepage" in data["pages"]

def test_upload_and_reset_site_asset(client):
    # 1. Login as admin
    login_res = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "AdminPassword123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload dummy image for homepage hero fallback
    dummy_file = io.BytesIO(b"fake-png-content")
    files = {"file": ("custom-hero.png", dummy_file, "image/png")}
    upload_res = client.post(
        "/admin/site-assets/homepage.hero.fallback/upload",
        headers=headers,
        files=files,
    )
    assert upload_res.status_code == 200
    asset_data = upload_res.json()
    assert asset_data["is_customized"] is True
    assert asset_data["active_url"].startswith("/static/site_assets/")

    # 3. Verify public endpoint reflects change
    pub_res = client.get("/site-assets")
    assert pub_res.status_code == 200
    assert pub_res.json()["homepage.hero.fallback"]["url"].startswith("/static/site_assets/")

    # 4. Reset asset back to factory fallback
    reset_res = client.post(
        "/admin/site-assets/homepage.hero.fallback/reset",
        headers=headers,
    )
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["is_customized"] is False
    assert reset_data["active_url"] == "/images/hero-x-fallback.png"

def test_set_site_asset_url(client):
    # 1. Login
    login_res = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "AdminPassword123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Set asset via external URL
    test_url = "https://images.unsplash.com/photo-1518770660439-4636190af475"
    res = client.post(
        "/admin/site-assets/global.logo.primary/set-url",
        headers=headers,
        json={"url": test_url, "alt_text": "External Logo"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_customized"] is True
    assert data["active_url"] == test_url

    # 3. Reset
    reset_res = client.post(
        "/admin/site-assets/global.logo.primary/reset",
        headers=headers,
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["is_customized"] is False
