from app.tests.test_client import client

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_success(monkeypatch):
    async def mock_command(cmd):
        return {"ok": 1}
    
    class MockDB:
        async def command(self, cmd):
            return await mock_command(cmd)
    
    monkeypatch.setattr("app.database.db", MockDB())
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_failure(monkeypatch):
    async def mock_command(cmd):
        raise Exception("db error")
    
    class MockDB:
        async def command(self, cmd):
            return await mock_command(cmd)
    
    monkeypatch.setattr("app.database.db", MockDB())
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unavailable"
    assert "error" in data
