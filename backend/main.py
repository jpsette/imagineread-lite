"""
ImagineRead Lite - Main Application
"""
import sys
from loguru import logger
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config import ENVIRONMENT, TEMP_DIR

# Configure Loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan management."""
    logger.info("🚀 Starting ImagineRead Lite...")
    logger.info(f"📁 Temp directory: {TEMP_DIR}")
    logger.info(f"🌍 Environment: {ENVIRONMENT}")
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
