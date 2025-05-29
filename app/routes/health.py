from fastapi import APIRouter
from app.database import db

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/ready")
async def ready():
    # Check if the database connection is available
    from fastapi import status
    from fastapi.responses import JSONResponse
    import logging
    try:
        await db.command("ping")
    except Exception as e:
        logging.exception(f"Database connection error: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "error": "An internal error has occurred."}
        )
    # If the database is reachable, return ready status
    return {"status": "ready"}
