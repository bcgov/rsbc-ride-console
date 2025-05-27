import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from app.routes import config
from app.routes import health

app = FastAPI()

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
    return RedirectResponse("/")
