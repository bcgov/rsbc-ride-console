from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import config
from app.routes import health

app = FastAPI()

app.include_router(config.router, prefix="/api")
app.include_router(health.router, prefix="/api")

@app.get("/api")
def read_root():
    return {"message": "RIDE Console API Running"}

app.mount("/", StaticFiles(directory="app/static_content", html=True, follow_symlink=True), name="static")
