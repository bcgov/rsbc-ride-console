from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.routes import config, health, recon, ftp, errors

# Logging setup
LOGGER_FORMAT = "[RIDE_CONSOLE_API] %(asctime)s %(levelname)s [%(name)s] %(message)s"
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", logging.INFO),
    format=os.getenv("LOGGER_FORMAT", LOGGER_FORMAT)
)

app = FastAPI(title="RIDE Console API", version="0.0.1")

# API routers
app.include_router(config.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(recon.router, prefix="/api")
app.include_router(ftp.router, prefix="/api")
app.include_router(errors.router, prefix="/api")

# Mount static content
app.mount("/assets", StaticFiles(directory="app/static_content/assets", check_dir=False), name="assets")
app.mount("/static", StaticFiles(directory="app/static_content", check_dir=False), name="static")


@app.get("/api", include_in_schema=False)
async def read_root():
    return {"message": "RIDE Console API Running"}


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_router(request: Request, full_path: str):
    # If the path looks like an API call, return 404 JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

   
    index_path = "app/static_content/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")

    return JSONResponse(status_code=404, content={"error": "index.html not found"})


@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    # Return JSON for missing API routes
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    
    redirect_url = f"/?redirect={request.url.path}"
    if request.url.query:
        redirect_url += f"&{request.url.query}"

    return RedirectResponse(redirect_url)
