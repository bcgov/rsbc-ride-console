from app.tests.test_client import client

def test_config():
    response = client.get("/v1/config")
    assert response.status_code == 200
    # The config is dynamic, but should contain these keys
    data = response.json()
    assert "apiPath" in data
    assert "oidc" in data
    assert "idpList" in data
