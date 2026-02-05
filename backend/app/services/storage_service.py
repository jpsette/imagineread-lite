"""
Storage Service
Handles file storage operations with Cloudflare R2 (S3-compatible).
For local development, uses file system storage.
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from app.config import (
    ENVIRONMENT, 
    TEMP_DIR,
    FREE_EXPIRY_HOURS
)

# R2 Configuration (from environment)
R2_ENDPOINT = os.getenv("R2_ENDPOINT", "https://2f9439b823aea204b0ddc2eb39f90cc7.r2.cloudflarestorage.com")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY", "")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "imagineread-lite")


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
        """Upload file to local storage."""
        tier = "premium" if is_premium else "free"
        file_dir = self.base_path / tier / code
        file_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = file_dir / filename
        file_path.write_bytes(file_content)
        
        storage_path = f"{tier}/{code}/{filename}"
        logger.info(f"📤 Uploaded: {storage_path} ({len(file_content)} bytes)")
        
        return storage_path
    
    def get_file(self, storage_path: str) -> Optional[bytes]:
        """Get file from local storage."""
        file_path = self.base_path / storage_path
        
        if not file_path.exists():
            logger.warning(f"📭 File not found: {storage_path}")
            return None
        
        return file_path.read_bytes()
    
    def get_download_url(self, storage_path: str, expiry_minutes: int = 60) -> str:
        """Get download URL for file (local dev uses API path)."""
        parts = storage_path.split("/")
        if len(parts) >= 2:
            code = parts[1]
            return f"/api/download/{code}"
        return f"/api/download/{storage_path}"
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from storage."""
        file_path = self.base_path / storage_path
        
        if file_path.exists():
            file_path.unlink()
            try:
                file_path.parent.rmdir()
            except OSError:
                pass
            logger.info(f"🗑️ Deleted: {storage_path}")
            return True
        
        return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists."""
        return (self.base_path / storage_path).exists()


class R2StorageService:
    """Cloudflare R2 storage service for production."""
    
    def __init__(self):
        try:
            import boto3
            from botocore.config import Config
            
            self.client = boto3.client(
                's3',
                endpoint_url=R2_ENDPOINT,
                aws_access_key_id=R2_ACCESS_KEY,
                aws_secret_access_key=R2_SECRET_KEY,
                config=Config(
                    signature_version='s3v4',
                    s3={'addressing_style': 'path'}
                )
            )
            self.bucket_name = R2_BUCKET_NAME
            logger.info(f"☁️ R2 initialized: {R2_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize R2: {e}")
            raise
    
    def upload_file(
        self, 
        file_content: bytes, 
        code: str, 
        filename: str,
        is_premium: bool = False
    ) -> str:
        """Upload file to R2."""
        tier = "premium" if is_premium else "free"
        storage_path = f"{tier}/{code}/{filename}"
        
        # Determine content type
        ext = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'epub': 'application/epub+zip',
            'cbz': 'application/x-cbz',
            'cbr': 'application/x-cbr',
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=storage_path,
            Body=file_content,
            ContentType=content_type
        )
        
        logger.info(f"☁️ Uploaded to R2: {storage_path}")
        return storage_path
    
    def get_file(self, storage_path: str) -> Optional[bytes]:
        """Get file from R2."""
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            return response['Body'].read()
        except self.client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get file from R2: {e}")
            return None
    
    def get_download_url(self, storage_path: str, expiry_minutes: int = 60) -> str:
        """
        Get download URL.
        Returns API download URL for consistency with iOS app.
        """
        parts = storage_path.split("/")
        if len(parts) >= 2:
            code = parts[1]
            return f"/api/download/{code}"
        return f"/api/download/{storage_path}"
    
    def generate_presigned_url(self, storage_path: str, expiry_seconds: int = 3600) -> str:
        """Generate presigned URL for direct R2 access (optional, for future use)."""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': storage_path
                },
                ExpiresIn=expiry_seconds
            )
            return url
        except Exception as e:
            logger.error(f"❌ Failed to generate presigned URL: {e}")
            return self.get_download_url(storage_path)
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from R2."""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            logger.info(f"☁️ Deleted from R2: {storage_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete from R2: {e}")
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in R2."""
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            return True
        except:
            return False


def get_storage_service():
    """
    Factory function to get the appropriate storage service.
    """
    if ENVIRONMENT == "development":
        return LocalStorageService()
    else:
        return R2StorageService()


# Singleton instance
_storage_service = None


def get_storage():
    """Get singleton storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = get_storage_service()
    return _storage_service
