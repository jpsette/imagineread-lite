"""
Health Check Router
"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "ImagineRead Lite"
    }


@router.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ImagineRead Lite API",
        "docs": "/docs"
    }
