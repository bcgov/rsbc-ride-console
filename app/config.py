
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    LOG_FORMAT = "[RIDE_CONSOLE_API] %(asctime)s::%(levelname)s::%(name)s::%(message)s"
    LOG_LEVEL  = os.getenv('LOG_LEVEL', 'INFO').upper()

    MONGO_URI = os.getenv("MONGO_URI")
    API_PATH = os.getenv("API_PATH", "/api/v1")
    OIDC_AUTHORITY = os.getenv("OIDC_AUTHORITY", "https://some.authority")
    OIDC_FRONTEND_CLIENT_ID = os.getenv("OIDC_FRONTEND_CLIENT_ID", "client-frontend-local")
    
    FRONTEND_CONFIG = {
        "apiPath": API_PATH,
        "oidc": {
            "authority": OIDC_AUTHORITY,
            "clientId": OIDC_FRONTEND_CLIENT_ID
        },
        "idpList": [
          {
            "name": "IDIR",
            "idp": "idir",
            "identityKey": "idir_user_guid"
          },
        ]
    }
