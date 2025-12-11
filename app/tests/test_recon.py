import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.routes import recon

# -----------------------------
# Include router and override auth
# -----------------------------
app.include_router(recon.router, prefix="/api/recon")
app.dependency_overrides[recon.authenticate_user] = lambda: {"user": "test"}

client = TestClient(app)

# -----------------------------
# Mock Data
# -----------------------------
MOCK_DOCS = [
    {
        "_id": str(ObjectId()),
        "eventType": "CREATE",
        "event_type": "CREATE",
        "datasource": "source_A",
        "eventid": "evt123",
        "recon_count": 11,
        "retry_count": 2,
        "apipath": "/api/create",
        "payloadstr": '{"event": "create"}',
        "payloaddata": {"ticket_number": "TKT-111", "event": {"eventid": "evt123"}},
        "errorReason": "Validation error"
    },
    {
        "_id": str(ObjectId()),
        "eventType": "UPDATE",
        "event_type": "UPDATE",
        "datasource": "source_B",
        "eventid": "evt456",
        "recon_count": 12,
        "retry_count": 5,
        "apipath": "/api/update",
        "payloadstr": '{"event": "update"}',
        "payloaddata": {"ticket_number": "TKT-222", "event": {"eventid": "evt456"}},
        "errorReason": "Missing field"
    },
    {
        "_id": str(ObjectId()),
        "eventType": "DELETE",
        "event_type": "DELETE",
        "datasource": "source_C",
        "eventid": "evt789",
        "recon_count": 14,
        "retry_count": 0,
        "apipath": "/api/delete",
        "payloadstr": '{"event": "delete"}',
        "payloaddata": {"ticket_number": "TKT-333", "event": {"eventid": "evt789"}},
        "errorReason": "None"
    }
]

VALID_OBJECT_ID = MOCK_DOCS[0]["_id"]
INVALID_OBJECT_ID = "invalid_id"

# -----------------------------
# Retry Exceptions Tests
# -----------------------------
@patch("app.routes.recon.recon_db")
def test_get_retry_exceptions(mock_db):
    mock_db["mainstaging"].find.return_value.to_list = AsyncMock(return_value=MOCK_DOCS)

    response = client.get("/api/recon/retry-exceptions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[1]["eventid"] == "evt456"


@patch("app.routes.recon.recon_db")
def test_delete_retry_exception_success(mock_db):
    mock_delete = AsyncMock()
    mock_delete.deleted_count = 1
    mock_db["mainstaging"].delete_one = AsyncMock(return_value=mock_delete)

    response = client.delete(f"/api/recon/retry-exceptions/{VALID_OBJECT_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["object_id"] == VALID_OBJECT_ID


@patch("app.routes.recon.recon_db")
def test_delete_retry_exception_not_found(mock_db):
    mock_delete = AsyncMock()
    mock_delete.deleted_count = 0
    mock_db["mainstaging"].delete_one = AsyncMock(return_value=mock_delete)

    response = client.delete(f"/api/recon/retry-exceptions/{VALID_OBJECT_ID}")
    assert response.status_code == 404


@patch("app.routes.recon.recon_db")
def test_reset_recon_count_success(mock_db):
    mock_update = AsyncMock()
    mock_update.matched_count = 1
    mock_db["mainstaging"].update_one = AsyncMock(return_value=mock_update)

    payload = {"object_id": VALID_OBJECT_ID}
    response = client.post("/api/recon/retry-exceptions/reset", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["object_id"] == VALID_OBJECT_ID


def test_reset_recon_count_invalid_object_id():
    payload = {"object_id": INVALID_OBJECT_ID}
    response = client.post("/api/recon/retry-exceptions/reset", json=payload)
    assert response.status_code == 400


@patch("app.routes.recon.recon_db")
def test_reset_all_retry_exceptions(mock_db):
    mock_result = AsyncMock()
    mock_result.matched_count = 3
    mock_result.modified_count = 3
    mock_db["mainstaging"].update_many = AsyncMock(return_value=mock_result)

    response = client.post("/api/recon/retry-exceptions/reset-all")
    assert response.status_code == 200
    data = response.json()
    assert data["matched_count"] == 3


@patch("app.routes.recon.recon_db")
def test_delete_all_retry_exceptions(mock_db):
    mock_delete = AsyncMock()
    mock_delete.deleted_count = 3
    mock_db["mainstaging"].delete_many = AsyncMock(return_value=mock_delete)

    response = client.delete("/api/recon/retry-exceptions")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 3


@patch("app.routes.recon.recon_db")
def test_retry_exceptions_count(mock_db):
    mock_db["mainstaging"].count_documents = AsyncMock(return_value=2)

    response = client.get("/api/recon/retry-exceptions/count")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2

# -----------------------------
# Error Count Tests
# -----------------------------
@patch("app.routes.recon.recon_db")
def test_get_error_count(mock_db):
    mock_db["errortable"].find.return_value.to_list = AsyncMock(return_value=MOCK_DOCS)

    response = client.get("/api/recon/error_count")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@patch("app.routes.recon.recon_db")
def test_reset_retry_count(mock_db):
    mock_update = AsyncMock()
    mock_update.matched_count = 1
    mock_db["errortable"].update_one = AsyncMock(return_value=mock_update)

    payload = {"object_id": VALID_OBJECT_ID}
    response = client.post("/api/recon/error_count/reset", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["object_id"] == VALID_OBJECT_ID


@patch("app.routes.recon.recon_db")
def test_delete_all_error_count(mock_db):
    mock_delete = AsyncMock()
    mock_delete.deleted_count = 3
    mock_db["errortable"].delete_many = AsyncMock(return_value=mock_delete)

    response = client.delete("/api/recon/error_count")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 3

# -----------------------------
# Staging Count Tests
# -----------------------------
@patch("app.routes.recon.recon_db")
def test_get_staging_count(mock_db):
    mock_db["mainstaging"].find.return_value.to_list = AsyncMock(return_value=MOCK_DOCS)

    response = client.get("/api/recon/staging_count")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
