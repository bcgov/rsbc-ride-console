import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import UploadFile
from io import BytesIO
from app.main import app
from app.routes import ftp

# -------------------------------
# INCLUDE ROUTER WITH PREFIX
# -------------------------------
app.include_router(ftp.router, prefix="/api/ftp")
client = TestClient(app)



# -------------------------------
# OVERRIDE AUTH
# -------------------------------
@pytest.fixture(autouse=True)
def override_auth(monkeypatch):
    async def mock_auth():
        return {"user": "test"}
    monkeypatch.setattr("app.routes.ftp.authenticate_user", mock_auth)


# -------------------------------
# MOCK FTP/SFTP
# -------------------------------
@pytest.fixture
def mock_sftp():
    sftp = MagicMock()
    sftp.listdir.return_value = ["file1.txt", "file2.txt"]
    sftp.stat.return_value = True
    sftp.remove.return_value = True
    sftp.rename.return_value = True
    sftp.getfo.side_effect = lambda path, file_obj: file_obj.write(b"demo content")
    sftp.open.return_value.__enter__.return_value.write = MagicMock()
    return sftp


@pytest.fixture
def mock_ftp(mock_sftp):
    ftp_instance = MagicMock()
    ftp_instance.acquire_sftp_channel.return_value = mock_sftp
    ftp_instance.release_sftp_channel.return_value = None
    return ftp_instance


@pytest.fixture
def mock_connection(mock_ftp):
    with patch("app.routes.ftp.connect_to_ftp", return_value=mock_ftp):
        ftp.current_ftp_connection.set(None)
        yield mock_ftp
        ftp.current_ftp_connection.set(None)


# -------------------------------
# TEST: LIST FILES
# -------------------------------
def test_list_recon_files(mock_connection):
    response = client.get("/api/ftp/recon_ftp")
    assert response.status_code == 200
    assert response.json() == ["file1.txt", "file2.txt"]


def test_list_archive_files(mock_connection):
    response = client.get("/api/ftp/recon_ftp_archives")
    assert response.status_code == 200
    assert response.json() == ["file1.txt", "file2.txt"]


def test_list_recon_ftp_both(mock_connection):
    response = client.get("/api/ftp/recon_ftp_both")
    assert response.status_code == 200
    assert response.json() == {
        "recon": ["file1.txt", "file2.txt"],
        "archive": ["file1.txt", "file2.txt"]
    }


# -------------------------------
# TEST: DELETE
# -------------------------------
def test_delete_recon_file(mock_connection):
    response = client.delete("/api/ftp/recon_ftp/delete", params={"filename": "file1.txt"})
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_missing_file(mock_connection, mock_sftp):
    mock_sftp.stat.side_effect = OSError(2, "No such file")
    response = client.delete("/api/ftp/recon_ftp/delete", params={"filename": "missing.txt"})
    assert response.status_code == 404


# -------------------------------
# TEST: DOWNLOAD
# -------------------------------
def test_download_recon_file(mock_connection):
    response = client.get("/api/ftp/recon_ftp/download", params={"filename": "file1.txt"})
    assert response.status_code == 200
    assert response.content == b"demo content"
    assert "attachment; filename=file1.txt" in response.headers["content-disposition"]


def test_download_file_not_found(mock_connection, mock_sftp):
    mock_sftp.getfo.side_effect = OSError("No such file")
    response = client.get("/api/ftp/recon_ftp/download", params={"filename": "none.txt"})
    assert response.status_code == 404


# -------------------------------
# TEST: RENAME
# -------------------------------
def test_rename_recon_file(mock_connection, mock_sftp):
    mock_sftp.stat.side_effect = [True, FileNotFoundError()]
    response = client.put("/api/ftp/recon_ftp/rename", params={"old_filename": "a.txt", "new_filename": "b.txt"})
    assert response.status_code == 200
    assert "Renamed" in response.json()["message"]


def test_rename_recon_file_exists(mock_connection, mock_sftp):
    mock_sftp.stat.side_effect = [None, None]
    response = client.put("/api/ftp/recon_ftp/rename", params={"old_filename": "a.txt", "new_filename": "b.txt"})
    assert response.status_code == 400


# -------------------------------
# TEST: COUNT
# -------------------------------
def test_count_recon_files(mock_connection):
    response = client.get("/api/ftp/recon_ftp/count")
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_count_archive_files(mock_connection):
    response = client.get("/api/ftp/recon_ftp_archives/count")
    assert response.status_code == 200
    assert response.json()["count"] == 2


# -------------------------------
# TEST: UPLOAD
# -------------------------------
def test_upload_file(mock_connection, mock_sftp):
    file_content = b"uploaded content"
    files = {"file": ("demo.txt", BytesIO(file_content))}
    response = client.post("/api/ftp/recon_ftp/upload", params={"folder": "primerecon"}, files=files)
    assert response.status_code == 201
    assert "uploaded successfully" in response.json()["message"]
    mock_sftp.open.return_value.__enter__.return_value.write.assert_called_once_with(file_content)
