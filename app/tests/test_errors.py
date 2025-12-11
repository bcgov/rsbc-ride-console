import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.routes import errors

# -------------------------------
# INCLUDE ROUTER WITH PREFIX
# -------------------------------
app.include_router(errors.router, prefix="/api/errors")
client = TestClient(app)



# -------------------------------
# MOCK DOCUMENTS
# -------------------------------
MOCK_DOCS = [
    {
        "_id": str(ObjectId()),
        "errorCategoryCd": "CAT1",
        "errorSeverityLevelCd": "HIGH",
        "ticketNo": "TKT-111",
        "detailsTxt": "Details 1",
        "serviceNm": "Service1",
        "_class": "Error",
        "fixed": False,
        "under_analysis": False,
    },
    {
        "_id": str(ObjectId()),
        "errorCategoryCd": "CAT2",
        "errorSeverityLevelCd": "MEDIUM",
        "ticketNo": "TKT-222",
        "detailsTxt": "Details 2",
        "serviceNm": "Service2",
        "_class": "Error",
        "fixed": True,
        "under_analysis": False,
    },
    {
        "_id": str(ObjectId()),
        "errorCategoryCd": "CAT3",
        "errorSeverityLevelCd": "LOW",
        "ticketNo": "TKT-333",
        "detailsTxt": "Details 3",
        "serviceNm": "Service3",
        "_class": "Error",
        "fixed": False,
        "under_analysis": True,
    },
]

VALID_OBJECT_ID = MOCK_DOCS[0]["_id"]

# -------------------------------
# OVERRIDE AUTH
# -------------------------------
@pytest.fixture(autouse=True)
def override_auth(monkeypatch):
    async def mock_auth():
        return {"user": "test"}
    monkeypatch.setattr("app.routes.errors.authenticate_user", mock_auth)


# -------------------------------
# PATCH MONGO DB
# -------------------------------
@pytest.fixture
def patch_db():
    with patch("app.routes.errors.ride_services_db") as mock_db:
        yield mock_db


# -------------------------------
# TEST: GET all errors
# -------------------------------
def test_get_errors(patch_db):
    patch_db["errors"].find.return_value.to_list = AsyncMock(return_value=MOCK_DOCS)
    response = client.get("/api/errors/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[1]["ticketNo"] == "TKT-222"


# -------------------------------
# TEST: GET fixed errors
# -------------------------------
def test_get_fixed_errors(patch_db):
    patch_db["errors"].find.return_value.to_list = AsyncMock(return_value=[MOCK_DOCS[1]])
    response = client.get("/api/errors/fixed")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["fixed"] is True


# -------------------------------
# TEST: GET under_analysis errors
# -------------------------------
def test_get_under_analysis_errors(patch_db):
    patch_db["errors"].find.return_value.to_list = AsyncMock(return_value=[MOCK_DOCS[2]])
    response = client.get("/api/errors/under-analysis")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["under_analysis"] is True


# -------------------------------
# TEST: GET new errors
# -------------------------------
def test_get_new_errors(patch_db):
    patch_db["errors"].find.return_value.to_list = AsyncMock(return_value=[MOCK_DOCS[0]])
    response = client.get("/api/errors/new")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["fixed"] is False
    assert data[0]["under_analysis"] is False


# -------------------------------
# TEST: set_fixed_true
# -------------------------------
def test_set_fixed_success(patch_db):
    mock_update = AsyncMock()
    mock_update.matched_count = 1
    patch_db["errors"].update_one = AsyncMock(return_value=mock_update)

    response = client.post("/api/errors/set-fixed", json={"object_id": VALID_OBJECT_ID})
    assert response.status_code == 200
    data = response.json()
    assert data["object_id"] == VALID_OBJECT_ID


def test_set_fixed_not_found(patch_db):
    mock_update = AsyncMock()
    mock_update.matched_count = 0
    patch_db["errors"].update_one = AsyncMock(return_value=mock_update)

    response = client.post("/api/errors/set-fixed", json={"object_id": VALID_OBJECT_ID})
    assert response.status_code == 404


# -------------------------------
# TEST: set_under_analysis_true
# -------------------------------
def test_set_under_analysis_success(patch_db):
    mock_update = AsyncMock()
    mock_update.matched_count = 1
    patch_db["errors"].update_one = AsyncMock(return_value=mock_update)

    response = client.post("/api/errors/set-under-analysis", json={"object_id": VALID_OBJECT_ID})
    assert response.status_code == 200
    data = response.json()
    assert data["object_id"] == VALID_OBJECT_ID


# -------------------------------
# TEST: set_all_fixed_true
# -------------------------------
def test_set_all_fixed(patch_db):
    mock_result = AsyncMock()
    mock_result.matched_count = 3
    mock_result.modified_count = 3
    patch_db["errors"].update_many = AsyncMock(return_value=mock_result)

    response = client.post("/api/errors/set-all-fixed")
    assert response.status_code == 200
    data = response.json()
    assert data["matched_count"] == 3
    assert data["modified_count"] == 3


# -------------------------------
# TEST: set_all_under_analysis_true
# -------------------------------
def test_set_all_under_analysis(patch_db):
    mock_result = AsyncMock()
    mock_result.matched_count = 2
    mock_result.modified_count = 2
    patch_db["errors"].update_many = AsyncMock(return_value=mock_result)

    response = client.post("/api/errors/set-all-under-analysis")
    assert response.status_code == 200
    data = response.json()
    assert data["matched_count"] == 2
    assert data["modified_count"] == 2


# -------------------------------
# TEST: count fixed errors
# -------------------------------
def test_count_fixed_errors(patch_db):
    patch_db["errors"].count_documents = AsyncMock(return_value=5)
    response = client.get("/api/errors/fixed/count")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5


# -------------------------------
# TEST: count under_analysis errors
# -------------------------------
def test_count_under_analysis_errors(patch_db):
    patch_db["errors"].count_documents = AsyncMock(return_value=2)
    response = client.get("/api/errors/under-analysis/count")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2


# -------------------------------
# TEST: count new errors
# -------------------------------
def test_count_new_errors(patch_db):
    patch_db["errors"].count_documents = AsyncMock(return_value=1)
    response = client.get("/api/errors/new/count")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
