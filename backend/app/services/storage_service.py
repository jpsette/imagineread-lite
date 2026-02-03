"""
Storage Service
Handles file storage operations with Google Cloud Storage.
For local development, uses file system storage.
"""
import os
import io
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, BinaryIO
from loguru import logger

from app.config import (
    ENVIRONMENT, 
    GCS_BUCKET_NAME, 
    GOOGLE_CLOUD_PROJECT,
    TEMP_DIR,
    FREE_EXPIRY_HOURS
)


class LocalStorageService:
    """Local file system storage for development."""
    
    def __init__(self):
        self.base_path = TEMP_DIR / "uploads"
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 LocalStorage initialized at: {self.base_path}")
    
    def upload_file(
        self, 
        file_content: bytes, 
        code: str, 
        filename: str,
        is_premium: bool = False
    ) -> str:
        """
        Upload file to local storage.
        
        Returns:
            Storage path
        """
        tier = "premium" if is_premium else "free"
        file_dir = self.base_path / tier / code
        file_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = file_dir / filename
        file_path.write_bytes(file_content)
        
        storage_path = f"{tier}/{code}/{filename}"
        logger.info(f"📤 Uploaded: {storage_path} ({len(file_content)} bytes)")
        
        return storage_path
    
    def get_file(self, storage_path: str) -> Optional[bytes]:
        """
        Get file from local storage.
        
        Returns:
            File content bytes or None if not found
        """
        file_path = self.base_path / storage_path
        
        if not file_path.exists():
            logger.warning(f"📭 File not found: {storage_path}")
            return None
        
        return file_path.read_bytes()
    
    def get_download_url(self, storage_path: str, expiry_minutes: int = 60) -> str:
        """
        Get download URL for file.
        In local dev, returns a local file URL.
        
        Returns:
            Download URL
        """
        # For local dev, return a relative path that will be served by FastAPI
        return f"/files/{storage_path}"
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.
        
        Returns:
            True if deleted, False otherwise
        """
        file_path = self.base_path / storage_path
        
        if file_path.exists():
            file_path.unlink()
            # Try to remove empty parent directories
            try:
                file_path.parent.rmdir()
            except OSError:
                pass  # Directory not empty
            logger.info(f"🗑️ Deleted: {storage_path}")
            return True
        
        return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists."""
        return (self.base_path / storage_path).exists()


class GCSStorageService:
    """Google Cloud Storage service for production."""
    
    def __init__(self):
        try:
            from google.cloud import storage
            self.client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
            self.bucket = self.client.bucket(GCS_BUCKET_NAME)
            logger.info(f"☁️ GCS initialized: {GCS_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCS: {e}")
            raise
    
    def upload_file(
        self, 
        file_content: bytes, 
        code: str, 
        filename: str,
        is_premium: bool = False
    ) -> str:
        """Upload file to GCS."""
        tier = "premium" if is_premium else "free"
        storage_path = f"{tier}/{code}/{filename}"
        
        blob = self.bucket.blob(storage_path)
        blob.upload_from_string(file_content)
        
        # Set expiration for free tier
        if not is_premium:
            expiry = datetime.utcnow() + timedelta(hours=FREE_EXPIRY_HOURS)
            blob.custom_time = expiry
        
        logger.info(f"☁️ Uploaded to GCS: {storage_path}")
        return storage_path
    
    def get_file(self, storage_path: str) -> Optional[bytes]:
        """Get file from GCS."""
        blob = self.bucket.blob(storage_path)
        
        if not blob.exists():
            return None
        
        return blob.download_as_bytes()
    
    def get_download_url(self, storage_path: str, expiry_minutes: int = 60) -> str:
        """Get signed URL for secure download."""
        blob = self.bucket.blob(storage_path)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiry_minutes),
            method="GET"
        )
        
        return url
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from GCS."""
        blob = self.bucket.blob(storage_path)
        
        if blob.exists():
            blob.delete()
            logger.info(f"☁️ Deleted from GCS: {storage_path}")
            return True
        
        return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in GCS."""
        blob = self.bucket.blob(storage_path)
        return blob.exists()


def get_storage_service():
    """
    Factory function to get the appropriate storage service.
    
    Returns:
        Storage service instance
    """
    if ENVIRONMENT == "development":
        return LocalStorageService()
    else:
        return GCSStorageService()


# Singleton instance
_storage_service = None


def get_storage():
    """Get singleton storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = get_storage_service()
    return _storage_service
