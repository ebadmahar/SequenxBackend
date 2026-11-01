def test_list_published_blogs(client):
    response = client.get("/blog")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data

def test_blog_search(client):
    response = client.get("/blog?search=engineering")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
