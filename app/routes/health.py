from fastapi import APIRouter
from app.database import db

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/ready")
async def ready():
    # Check if the database connection is available
    try:
        await db.command("ping")
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}
    # If the database is reachable, return ready status
    return {"status": "ready"}
