from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any
import os
import httpx
import logging
from app.auth.auth import authenticate_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Read these from environment variables or .env file
PRODUCER_API_URL = os.getenv("VITE_PRODUCER_API_URL")
PRODUCER_API_KEY = os.getenv("VITE_API_RIDE_KEY_PRODUCER")

if not PRODUCER_API_URL or not PRODUCER_API_KEY:
    logger.warning("ProducerService: Missing base URL or API key in environment variables.")

class ProducerPayload(BaseModel):
    apipath: str
    payload: Any

@router.post("/send",tags=["producer"], summary="Send data to external Producer API")
async def send_to_producer(data: ProducerPayload):
    if not PRODUCER_API_URL or not PRODUCER_API_KEY:
        raise HTTPException(status_code=500, detail="Producer API configuration missing")

    url = f"{PRODUCER_API_URL}{data.apipath}"

    headers = {
        "ride-api-key": PRODUCER_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data.payload, headers=headers)
            response.raise_for_status()
        return {"status": "success", "detail": response.json()}
    except httpx.HTTPStatusError as exc:
        logger.error(f"Producer API returned HTTP {exc.response.status_code}: {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        logger.error(f"Error sending to Producer API: {exc}")
        raise HTTPException(status_code=500, detail="Failed to send to Producer API")
