from app.tests.test_client import client

def test_read_root():
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {"message": "RIDE Console API Running"}
