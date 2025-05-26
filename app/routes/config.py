from fastapi import APIRouter
from app.config import Config

router = APIRouter()

@router.get("/config")
async def config():
    return Config.FRONTEND_CONFIG
