"""
ImagineRead Lite - Main Application
"""
import sys
from pathlib import Path
from loguru import logger
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config import ENVIRONMENT, TEMP_DIR

# Configure Loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan management."""
    logger.info("🚀 Starting ImagineRead Lite...")
    logger.info(f"📁 Temp directory: {TEMP_DIR}")
    logger.info(f"🌍 Environment: {ENVIRONMENT}")
    logger.info(f"📂 Static directory: {STATIC_DIR} (exists: {STATIC_DIR.exists()})")
    yield
    logger.info("👋 Shutting down ImagineRead Lite...")


app = FastAPI(
    title="ImagineRead Lite",
    description="File sharing service via QRCode",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://lite.imagineread.com",
    "https://imagineread.com",
    "*"  # TODO: Restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routers import upload, download, health

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(download.router)

# Serve static files (frontend assets)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend."""
        return FileResponse(STATIC_DIR / "index.html")
    
    @app.get("/{catch_all:path}")
    async def serve_spa(catch_all: str):
        """Serve SPA for client-side routing."""
        # Don't catch API routes
        if catch_all.startswith("api/") or catch_all.startswith("docs") or catch_all.startswith("health") or catch_all.startswith("openapi"):
            return {"detail": "Not Found"}
        file_path = STATIC_DIR / catch_all
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

