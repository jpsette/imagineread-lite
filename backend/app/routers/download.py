"""
Download Router
Handles file retrieval by code.
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
from loguru import logger
from datetime import datetime
import io

from app.services.storage_service import get_storage
from app.services.transfer_service import get_transfers


router = APIRouter(prefix="/api", tags=["Download"])


class FileInfoResponse(BaseModel):
    """Response model for file info."""
    success: bool
    code: str
    originalName: str
    fileType: str
    fileSizeBytes: int
    downloadUrl: str
    expiresAt: Optional[str]
    downloadCount: int


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str


@router.get("/file/{code}", response_model=FileInfoResponse)
async def get_file_info(code: str):
    """
    Get file information and download URL by code.
    
    - Returns file metadata and a signed download URL
    - Increments download counter
    """
    code = code.upper().replace("-", "")  # Normalize code
    
    transfer_service = get_transfers()
    transfer = transfer_service.get(code)
    
    if not transfer:
        raise HTTPException(
            status_code=404,
            detail="Code not found. Please check and try again."
        )
    
    # Check if expired
    if transfer.is_expired():
        raise HTTPException(
            status_code=410,
            detail="This transfer has expired. Files are available for 24 hours."
        )
    
    # Get download URL
    storage = get_storage()
    download_url = storage.get_download_url(transfer.storage_path)
    
    # Increment download count
    transfer_service.increment_download_count(code)
    
    logger.info(f"📥 File info requested: {code}")
    
    return FileInfoResponse(
        success=True,
        code=code,
        originalName=transfer.original_name,
        fileType=transfer.file_type,
        fileSizeBytes=transfer.file_size_bytes,
        downloadUrl=download_url,
        expiresAt=transfer.expires_at.isoformat() if transfer.expires_at else None,
        downloadCount=transfer.download_count + 1
    )


@router.get("/download/{code}")
async def download_file(code: str):
    """
    Direct file download endpoint (for local development).
    
    In production, use the signed URL from /file/{code} instead.
    """
    code = code.upper().replace("-", "")
    
    transfer_service = get_transfers()
    transfer = transfer_service.get(code)
    
    if not transfer:
        raise HTTPException(status_code=404, detail="Code not found")
    
    if transfer.is_expired():
        raise HTTPException(status_code=410, detail="Transfer expired")
    
    storage = get_storage()
    file_content = storage.get_file(transfer.storage_path)
    
    if not file_content:
        raise HTTPException(status_code=404, detail="File not found in storage")
    
    # Determine content type
    content_types = {
        "pdf": "application/pdf",
        "cbz": "application/x-cbz",
        "cbr": "application/x-cbr",
        "epub": "application/epub+zip"
    }
    content_type = content_types.get(transfer.file_type, "application/octet-stream")
    
    # Increment download count
    transfer_service.increment_download_count(code)
    
    logger.info(f"📥 File downloaded: {code} - {transfer.original_name}")
    
    return Response(
        content=file_content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{transfer.original_name}"'
        }
    )


@router.get("/check/{code}")
async def check_code(code: str):
    """
    Quick check if a code is valid (without downloading).
    
    Useful for mobile app to validate before downloading.
    """
    code = code.upper().replace("-", "")
    
    transfer_service = get_transfers()
    transfer = transfer_service.get(code)
    
    if not transfer:
        return {"valid": False, "reason": "not_found"}
    
    if transfer.is_expired():
        return {"valid": False, "reason": "expired"}
    
    return {
        "valid": True,
        "fileName": transfer.original_name,
        "fileType": transfer.file_type,
        "fileSizeBytes": transfer.file_size_bytes
    }
