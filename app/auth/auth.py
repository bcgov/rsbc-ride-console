import httpx
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError

from app.config import Config

from fastapi_oidc import get_auth
from typing import Callable

config = Config()


OIDC_config = {
    "issuer": os.getenv("OIDC_AUTHORITY", "https://some.authority"),
    "client_id": os.getenv("OIDC_FRONTEND_CLIENT_ID", "client-frontend-local"),
    "base_authorization_server_uri": os.getenv("BASE_AUTHORIZATION_SERVER_URI"),
    "signature_cache_ttl": 3600,
    #"validate_access_token": True,
    #"client_secret": os.getenv("OIDC_BACKEND_CLIENT_SECRET", "")
}

authenticate_user: Callable = get_auth(**OIDC_config)






