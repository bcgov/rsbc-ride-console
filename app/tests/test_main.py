from app.tests.test_client import client

def test_read_root():
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {"message": "RIDE Console API Running"}

def test_custom_404_handler_api():
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}

def test_custom_404_handler_static_redirect():
    response = client.get("/nonexistent-page")
    # Should redirect to "/"
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")

def test_static_files_served():
    # This test assumes there is an index.html in static_content directory
    response = client.get("/")
    # Should serve static content (e.g., HTML)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
