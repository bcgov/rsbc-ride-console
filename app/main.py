import os
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn

from app.routes import config
from app.routes import health
import logging

LOGGER_FORMAT = "[RIDE_CONSOLE_API] %(asctime)s %(levelname)s [%(name)s] %(message)s"
logging.basicConfig(
  level=os.getenv("LOG_LEVEL", logging.INFO),
  format=os.getenv("LOGGER_FORMAT", LOGGER_FORMAT)
)

app = FastAPI(title="RIDE Console API", version="0.0.1")

app.include_router(config.router, prefix="/api")
app.include_router(health.router, prefix="/api")

@app.get("/api")
def read_root():
    return {"message": "RIDE Console API Running"}

print(os.path.join(os.path.dirname(__file__), "static_content"))
static_content_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static_content"))
app.mount("/", StaticFiles(directory=static_content_path, html=True, follow_symlink=True), name="static")

@app.exception_handler(404)
async def custom_404_handler(request, __):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return RedirectResponse(f"/?redirect={request.url.path}&{request.url.query}" if request.url.query else f"/?redirect={request.url.path}")
