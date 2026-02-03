"""
Upload Router
Handles file uploads and generates access codes.
"""
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger

from app.config import (
    FREE_FILE_SIZE_LIMIT_BYTES,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES
)
from app.services.code_generator import generate_code, format_code_for_display
from app.services.storage_service import get_storage
from app.services.transfer_service import get_transfers, Transfer


router = APIRouter(prefix="/api", tags=["Upload"])


class UploadResponse(BaseModel):
    """Response model for successful upload."""
    success: bool
    code: str
    codeFormatted: str
    originalName: str
    fileType: str
    fileSizeBytes: int
    expiresAt: str | None
    message: str


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[1].lower()


def validate_file_type(filename: str, content_type: str) -> str:
    """
    Validate file type and return normalized extension.
    
    Raises:
        HTTPException: If file type is not allowed
    """
    extension = get_file_extension(filename)
    
    # Check extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{extension}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type (if provided)
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        # Allow through if extension is valid (some browsers send wrong MIME)
        logger.warning(f"Unknown MIME type: {content_type}, but extension is valid: {extension}")
    
    return extension


def validate_file_size(file_size: int, is_premium: bool = False) -> None:
    """
    Validate file size.
    
    Raises:
        HTTPException: If file is too large
    """
    limit = FREE_FILE_SIZE_LIMIT_BYTES if not is_premium else FREE_FILE_SIZE_LIMIT_BYTES * 10
    
    if file_size > limit:
        limit_mb = limit / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {limit_mb}MB"
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    request: Request = None
):
    """
    Upload a file and get an access code.
    
    - Accepts: PDF, CBZ, CBR, EPUB
    - Max size: 10MB (free) / 100MB (premium)
    - Returns: Unique code for accessing the file
    """
    try:
        # Validate file type
        file_type = validate_file_type(file.filename, file.content_type)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        validate_file_size(file_size, is_premium=False)
        
        # Generate unique code
        transfer_service = get_transfers()
        existing_codes = transfer_service.get_all_codes()
        code = generate_code()
        
        # Ensure uniqueness (very rare case)
        attempts = 0
        while code in existing_codes and attempts < 10:
            code = generate_code()
            attempts += 1
        
        # Upload to storage
        storage = get_storage()
        storage_path = storage.upload_file(
            file_content=content,
            code=code,
            filename=file.filename,
            is_premium=False
        )
        
        # Create transfer record
        transfer = Transfer(
            code=code,
            original_name=file.filename,
            file_type=file_type,
            file_size_bytes=file_size,
            storage_path=storage_path,
            is_premium=False
        )
        
        transfer_service.create(transfer)
        
        logger.info(f"✅ Upload complete: {code} - {file.filename} ({file_size} bytes)")
        
        return UploadResponse(
            success=True,
            code=code,
            codeFormatted=format_code_for_display(code),
            originalName=file.filename,
            fileType=file_type,
            fileSizeBytes=file_size,
            expiresAt=transfer.expires_at.isoformat() if transfer.expires_at else None,
            message="File uploaded successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
