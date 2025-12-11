import pytest
from unittest.mock import patch, MagicMock
import importlib

def test_mongo_client_with_mock_db():
    mock_mongo_uri = "mongodb://mockuser:mockpass@localhost:27017"

    # Patch Config.MONGO_URI before importing app.db.mongo
    with patch("app.config.Config") as mock_config, \
         patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_motor_client:

        # Set the mock URI before module import
        mock_config.MONGO_URI = mock_mongo_uri

        # Create a mock Mongo client
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.side_effect = lambda name: MagicMock(name=f"{name}_db")
        mock_motor_client.return_value = mock_client_instance

        # Import and reload the module to apply the mocks
        import app.db.mongo as db
        importlib.reload(db)

        # Now db.MONGO_URI should be the mocked URI
        assert db.MONGO_URI == mock_mongo_uri

        # Ensure AsyncIOMotorClient is called with mock URI
        mock_motor_client.assert_called_with(mock_mongo_uri)

        # Ensure the databases are mocks
        assert type(db.recon_db).__name__ == "MagicMock"
        assert type(db.ride_services_db).__name__ == "MagicMock"

        # ensure different mocks for different DBs
        assert db.recon_db is not db.ride_services_db
