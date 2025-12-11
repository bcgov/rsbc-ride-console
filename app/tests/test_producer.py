import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.routes import producer
from app.routes.producer import ProducerPayload

# -------------------------------
# SETUP FASTAPI APP
# -------------------------------
from fastapi import FastAPI
app = FastAPI()
app.include_router(producer.router, prefix="/api/producer")

client = TestClient(app)

# -------------------------------
# MOCK RESPONSE
# -------------------------------
class MockResponse:
    def __init__(self, json_data=None, status_code=200, text=""):
        self._json_data = json_data or {}
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise producer.httpx.HTTPStatusError(
                message="HTTP error",
                request=None,
                response=self
            )

    def json(self):
        return self._json_data

class MockAsyncClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, json=None, headers=None):
        return self._response

# -------------------------------
# TEST: SUCCESSFUL ENDPOINT CALL
# -------------------------------
def test_producer_endpoint_success():
    payload = {"apipath": "/test", "payload": {"key": "value"}}
    mock_response = MockResponse(json_data={"message": "ok"}, status_code=200)

    with patch.object(producer, "PRODUCER_API_URL", "https://fakeapi.com/"), \
         patch.object(producer, "PRODUCER_API_KEY", "FAKE_KEY"), \
         patch("httpx.AsyncClient", return_value=MockAsyncClient(mock_response)):

        response = client.post("/api/producer/send", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["detail"] == {"message": "ok"}

# -------------------------------
# TEST: HTTP ERROR FROM PRODUCER
# -------------------------------
def test_producer_endpoint_http_error():
    payload = {"apipath": "/fail", "payload": {"key": "value"}}
    mock_response = MockResponse(status_code=400, text="Bad request")

    with patch.object(producer, "PRODUCER_API_URL", "https://fakeapi.com/"), \
         patch.object(producer, "PRODUCER_API_KEY", "FAKE_KEY"), \
         patch("httpx.AsyncClient", return_value=MockAsyncClient(mock_response)):

        response = client.post("/api/producer/send", json=payload)
        assert response.status_code == 400
        assert "Bad request" in response.json()["detail"]

# -------------------------------
# TEST: MISSING PAYLOAD
# -------------------------------
def test_producer_endpoint_missing_payload():
    response = client.post("/api/producer/send", json={})
    # Expect validation error from FastAPI / Pydantic
    assert response.status_code == 422
