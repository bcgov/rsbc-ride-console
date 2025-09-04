
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
   
  
    OIDC_BACKEND_CLIENT_ID=os.getenv("OIDC_BACKEND_CLIENT_ID", "client-backend-local")
    OIDC_BACKEND_CLIENT_SECRET=os.getenv("OIDC_BACKEND_CLIENT_SECRET", "")
    BASE_AUTHORIZATION_SERVER_URI=os.getenv("BASE_AUTHORIZATION_SERVER_URI", "BASE_AUTHORIZATION_SERVER_URI")
    VITE_GRAFANA_URL= os.getenv("VITE_GRAFANA_URL",'')

    
    FRONTEND_CONFIG = {
        "apiPath": API_PATH,
        "grafanaURL": VITE_GRAFANA_URL,
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
