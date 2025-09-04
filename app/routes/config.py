from fastapi import APIRouter, Depends
from app.config import Config
from typing import List;
from app.models.event import Event
from app.auth.auth  import authenticate_user
from fastapi_oidc import IDToken
from fastapi_oidc import get_auth
from fastapi import Query, HTTPException

from app.db.mongo import recon_db
from app.ftp.ftputil import FTPUtil
import os
import logging
import base64
import contextvars
from contextlib import asynccontextmanager
import errno

# Holds the current connection (per async context)
current_ftp_connection = contextvars.ContextVar("current_ftp_connection", default=None)



router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/config")
async def config():
    return Config.FRONTEND_CONFIG



