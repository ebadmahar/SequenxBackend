def test_list_open_jobs(client):
    response = client.get("/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_nonexistent_job_returns_404(client):
    response = client.get("/jobs/99999")
    assert response.status_code == 404
