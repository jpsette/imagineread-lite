"""
ImagineRead Lite - Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Google Cloud
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "imagineread-lite-uploads")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# App Config
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FREE_FILE_SIZE_LIMIT_MB = int(os.getenv("FREE_FILE_SIZE_LIMIT_MB", "30"))
PREMIUM_FILE_SIZE_LIMIT_MB = int(os.getenv("PREMIUM_FILE_SIZE_LIMIT_MB", "100"))
FREE_EXPIRY_HOURS = int(os.getenv("FREE_EXPIRY_HOURS", "24"))

# Derived
FREE_FILE_SIZE_LIMIT_BYTES = FREE_FILE_SIZE_LIMIT_MB * 1024 * 1024
PREMIUM_FILE_SIZE_LIMIT_BYTES = PREMIUM_FILE_SIZE_LIMIT_MB * 1024 * 1024

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "cbz", "cbr", "epub"}
ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/x-cbz": "cbz",
    "application/x-cbr": "cbr",
    "application/epub+zip": "epub",
    "application/zip": "cbz",  # CBZ is often detected as zip
    "application/x-rar-compressed": "cbr",
}

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)
